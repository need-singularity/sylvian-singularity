// Phase 7: Perfect number chains — σ-chain, Mersenne bootstrap, iterated functions
// Supports: iterated sigma, phi, tau chains, triangular/factorial detection,
// perfect number characterization, and the Mersenne bootstrap theorem

use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::sieves::ArithTables;

/// Check if n is a triangular number. Returns Some(m) if n = m(m+1)/2, else None.
fn is_triangular(n: u64) -> Option<u64> {
    // n = m(m+1)/2 → m² + m - 2n = 0 → m = (-1 + √(1+8n)) / 2
    let disc = 1 + 8 * n;
    let sqrt_disc = (disc as f64).sqrt() as u64;
    // Check sqrt_disc and sqrt_disc+1 for exact match
    for s in [sqrt_disc.saturating_sub(1), sqrt_disc, sqrt_disc + 1] {
        if s * s == disc {
            if (s - 1) % 2 == 0 {
                return Some((s - 1) / 2);
            }
        }
    }
    None
}

/// Check if n is a factorial. Returns Some(k) if n = k!, else None.
fn is_factorial(n: u64) -> Option<u64> {
    if n == 1 { return Some(1); }
    let mut k = 2u64;
    let mut fact = 2u64;
    while fact < n {
        k += 1;
        fact = fact.checked_mul(k).unwrap_or(u64::MAX);
    }
    if fact == n { Some(k) } else { None }
}

/// Check if n is a perfect number using precomputed sigma
fn is_perfect(n: u64, sigma_n: u64) -> bool {
    sigma_n == 2 * n
}

/// Compute sigma(n) by trial division (for n beyond sieve limit)
fn sigma_trial(n: u64) -> u64 {
    if n <= 1 { return n; }
    let mut result = 0u64;
    let mut d = 1u64;
    while d * d <= n {
        if n % d == 0 {
            result += d;
            if d != n / d {
                result += n / d;
            }
        }
        d += 1;
    }
    result
}

/// Compute phi(n) by trial division
fn phi_trial(n: u64) -> u64 {
    if n <= 1 { return n; }
    let mut result = n;
    let mut temp = n;
    let mut p = 2u64;
    while p * p <= temp {
        if temp % p == 0 {
            while temp % p == 0 {
                temp /= p;
            }
            result -= result / p;
        }
        p += 1;
    }
    if temp > 1 {
        result -= result / temp;
    }
    result
}

/// Compute tau(n) by trial division
fn tau_trial(n: u64) -> u64 {
    if n <= 1 { return n; }
    let mut count = 0u64;
    let mut d = 1u64;
    while d * d <= n {
        if n % d == 0 {
            count += 1;
            if d != n / d {
                count += 1;
            }
        }
        d += 1;
    }
    count
}

/// Compute iterated sigma chain: σ^k(n) for k = 0, 1, ..., max_iter
#[pyfunction]
#[pyo3(signature = (n, max_iter=20))]
pub fn sigma_chain(n: u64, max_iter: usize) -> Vec<u64> {
    let mut chain = Vec::with_capacity(max_iter + 1);
    let mut current = n;
    chain.push(current);
    for _ in 0..max_iter {
        current = sigma_trial(current);
        if current > 10_000_000_000 { break; } // overflow guard
        chain.push(current);
    }
    chain
}

/// Analyze the sigma chain with full metadata
#[pyfunction]
#[pyo3(signature = (n, max_iter=20))]
pub fn sigma_chain_analysis(py: Python<'_>, n: u64, max_iter: usize) -> PyResult<Vec<Py<PyAny>>> {
    let mut results = Vec::new();
    let mut current = n;

    for step in 0..=max_iter {
        let dict = PyDict::new(py);
        dict.set_item("step", step)?;
        dict.set_item("n", current)?;

        let sigma_n = sigma_trial(current);
        let tau_n = tau_trial(current);
        let phi_n = phi_trial(current);

        dict.set_item("sigma", sigma_n)?;
        dict.set_item("tau", tau_n)?;
        dict.set_item("phi", phi_n)?;
        dict.set_item("abundancy", sigma_n as f64 / current as f64)?;
        dict.set_item("is_perfect", sigma_n == 2 * current)?;

        if let Some(m) = is_triangular(current) {
            dict.set_item("triangular_index", m)?;
        }
        if let Some(k) = is_factorial(current) {
            dict.set_item("factorial_of", k)?;
        }

        results.push(dict.into_any().unbind());

        if sigma_n > 10_000_000_000 || step == max_iter { break; }
        current = sigma_n;
    }
    Ok(results)
}

/// Check the Mersenne bootstrap: for which even perfect numbers P
/// is σ(σ(P)) also a perfect number?
#[pyfunction]
pub fn mersenne_bootstrap(py: Python<'_>, max_exponent: u32) -> PyResult<Vec<Py<PyAny>>> {
    // Known Mersenne exponents (hardcoded for speed)
    let mersenne_exps: Vec<u32> = vec![2, 3, 5, 7, 13, 17, 19, 31];
    let mut results = Vec::new();

    for &p in &mersenne_exps {
        if p > max_exponent { break; }

        let dict = PyDict::new(py);
        dict.set_item("p", p)?;

        let mp: u64 = (1u64 << p) - 1; // 2^p - 1
        let pk: u64 = (1u64 << (p - 1)) * mp; // 2^(p-1) * (2^p-1)

        dict.set_item("mersenne_prime", mp)?;
        dict.set_item("perfect_number", pk)?;

        // σ(σ(P)) = (2^(p+1)-1) * 2^p
        let m: u64 = (1u64 << (p + 1)) - 1; // 2^(p+1) - 1
        let sigma_sigma: u64 = m * (1u64 << p);

        dict.set_item("sigma_sigma", sigma_sigma)?;
        dict.set_item("triangular_index", m)?;

        // Is m a Mersenne prime?
        let m_is_prime = is_prime_u64(m);
        dict.set_item("index_is_mersenne_prime", m_is_prime)?;

        // Is σσ itself perfect?
        let ss_perfect = m_is_prime && {
            // If m is Mersenne prime, T_m = 2^((p+1)-1) * m is perfect
            true
        };
        dict.set_item("sigma_sigma_is_perfect", ss_perfect)?;

        // p+1 info
        let p_plus_1 = p + 1;
        let p_plus_1_prime = is_prime_u32(p_plus_1);
        dict.set_item("p_plus_1", p_plus_1)?;
        dict.set_item("p_plus_1_is_prime", p_plus_1_prime)?;

        results.push(dict.into_any().unbind());
    }
    Ok(results)
}

/// Find all n in [2, limit] where σ(n)φ(n)+τ(n) = target
#[pyfunction]
pub fn find_sigma_phi_tau(target: u64, limit: usize) -> Vec<u64> {
    let tables = ArithTables::new(limit);
    let mut solutions = Vec::new();
    for n in 2..=limit {
        let s = tables.sigma[n];
        let p = tables.phi[n];
        let t = tables.tau[n];
        if s * p + t == target {
            solutions.push(n as u64);
        }
    }
    solutions
}

/// Scan for unique identities at a target n: count how many from a predefined
/// set of identities are satisfied ONLY by n in [2, limit]
#[pyfunction]
pub fn uniqueness_score(target: usize, limit: usize) -> PyResult<u32> {
    let tables = ArithTables::new(limit);
    let mut score = 0u32;

    // List of identity checks (lhs == rhs for each n)
    // Each returns (lhs, rhs) given arithmetic functions
    let identities: Vec<Box<dyn Fn(usize, u64, u64, u64, u64, u64) -> (i64, i64)>> = vec![
        // n-2 = tau
        Box::new(|n, _s, t, _p, _sp, _om| (n as i64 - 2, t as i64)),
        // n = sigma/phi
        Box::new(|n, s, _t, p, _sp, _om| (n as i64 * p as i64, s as i64)),
        // n-1 = sopfr
        Box::new(|n, _s, _t, _p, sp, _om| (n as i64 - 1, sp as i64)),
        // sigma*2 = n*tau
        Box::new(|n, s, t, _p, _sp, _om| (s as i64 * 2, n as i64 * t as i64)),
        // n+2 = sigma-tau
        Box::new(|n, s, t, _p, _sp, _om| (n as i64 + 2, s as i64 - t as i64)),
        // sigma-tau-phi = n
        Box::new(|n, s, t, p, _sp, _om| (s as i64 - t as i64 - p as i64, n as i64)),
        // n/phi = sigma/tau (requires divisibility)
        Box::new(|n, s, t, p, _sp, _om| {
            if p > 0 && t > 0 { (n as i64 * t as i64, s as i64 * p as i64) }
            else { (0, 1) }
        }),
        // tau^2 = sigma + tau
        Box::new(|_n, s, t, _p, _sp, _om| (t as i64 * t as i64, s as i64 + t as i64)),
        // n^2 - sigma = tau! (check up to tau=12)
        Box::new(|n, s, t, _p, _sp, _om| {
            let lhs = (n * n) as i64 - s as i64;
            let rhs = if t <= 12 { (1..=t).product::<u64>() as i64 } else { -1 };
            (lhs, rhs)
        }),
    ];

    for identity in &identities {
        let mut solutions = Vec::new();
        for n in 2..=limit {
            let s = tables.sigma[n];
            let t = tables.tau[n];
            let p = tables.phi[n];
            let sp = tables.sopfr[n];
            let om = tables.omega[n];
            let (lhs, rhs) = identity(n, s, t, p, sp, om);
            if lhs == rhs && rhs >= 0 {
                solutions.push(n);
            }
        }
        if solutions.len() == 1 && solutions[0] == target {
            score += 1;
        }
    }
    Ok(score)
}

// Helper: primality test for u64
fn is_prime_u64(n: u64) -> bool {
    if n < 2 { return false; }
    if n < 4 { return true; }
    if n % 2 == 0 || n % 3 == 0 { return false; }
    let mut i = 5u64;
    while i * i <= n {
        if n % i == 0 || n % (i + 2) == 0 { return false; }
        i += 6;
    }
    true
}

fn is_prime_u32(n: u32) -> bool {
    is_prime_u64(n as u64)
}
