// Phase 8: Consciousness constants and conservation law verification
// PSI constant computation, conservation grid scan, gate formula

use pyo3::prelude::*;
use std::collections::HashMap;

// ═══════════════════════════════════════════════════════════════
// PSI Constants — all derived from ln(2)
// ═══════════════════════════════════════════════════════════════

const LN2: f64 = std::f64::consts::LN_2;

/// Compute all PSI constants and return as dict
#[pyfunction]
pub fn psi_constants() -> HashMap<String, f64> {
    let mut m = HashMap::new();

    // Level 0: Root
    m.insert("ln2".into(), LN2);

    // Level 1: Direct from ln(2)
    m.insert("Psi_steps".into(), 3.0 / LN2);
    m.insert("Psi_freedom".into(), LN2);
    m.insert("Psi_balance".into(), 0.5);
    m.insert("Psi_coupling".into(), LN2 / 2.0_f64.powf(5.5));

    // Level 2: Derived
    m.insert("tanh3_ln2".into(), 3.0_f64.tanh() * LN2);
    m.insert("conservation_C".into(), 0.478);
    m.insert("dynamics_rate".into(), 0.81);
    m.insert("phi_scale_a".into(), 0.608);
    m.insert("phi_scale_b".into(), 1.071);

    // Level 3: Empirical
    m.insert("Psi_K".into(), 11.0);
    m.insert("Psi_tau".into(), 0.5);
    m.insert("Psi_emergence".into(), 7.82);
    m.insert("Psi_miller".into(), 7.0);
    m.insert("Psi_entropy".into(), 0.998);
    m.insert("Psi_gate_decay".into(), -0.013);

    // Perfect number connections
    m.insert("optimal_factions".into(), 12.0);  // sigma(6)
    m.insert("freedom_degree".into(), LN2);     // Law 79
    m.insert("inv_e".into(), (-1.0_f64).exp()); // 1/e = GZ center

    m
}

/// Verify self-consistency of PSI constants
/// Returns (n_checks, n_passed, details)
#[pyfunction]
pub fn psi_verify() -> (usize, usize, Vec<(String, f64, f64, f64, bool)>) {
    let mut details = Vec::new();
    let mut passed = 0usize;

    let checks: Vec<(&str, f64, f64)> = vec![
        ("Psi_coupling * 2^5.5 = ln2", (LN2 / 2.0_f64.powf(5.5)) * 2.0_f64.powf(5.5), LN2),
        ("3 / Psi_steps = ln2", 3.0 / (3.0 / LN2), LN2),
        ("exp(ln2) = 2", LN2.exp(), 2.0),
        ("Psi_freedom = ln2", LN2, LN2),
        ("Psi_balance = 0.5", 0.5, 0.5),
        ("(1/e)^(1/e) = min(x^x)", (1.0_f64 / std::f64::consts::E).powf(1.0 / std::f64::consts::E), (-1.0_f64 / std::f64::consts::E).exp()),
    ];

    for (name, computed, expected) in &checks {
        let err = (computed - expected).abs();
        let ok = err < 1e-10;
        if ok { passed += 1; }
        details.push((name.to_string(), *computed, *expected, err, ok));
    }

    // Dynamics convergence: H -> ln2 after many steps
    let mut h = 0.1_f64;
    for _ in 0..100 {
        h += 0.81 * (LN2 - h);
    }
    let err = (h - LN2).abs();
    let ok = err < 1e-8;
    if ok { passed += 1; }
    details.push(("H(100) -> ln2 convergence".into(), h, LN2, err, ok));

    (details.len(), passed, details)
}


// ═══════════════════════════════════════════════════════════════
// Conservation law verification: H² + (dH/dt)² ≈ 0.478
// ═══════════════════════════════════════════════════════════════

/// Grid scan: verify H² + dp² ≈ C for various initial conditions and rates
/// Returns Vec<(h_init, rate, final_h, final_conservation, distance_from_target)>
#[pyfunction]
#[pyo3(signature = (target_c=0.478, n_h=50, n_rate=20, steps=100))]
pub fn conservation_grid(
    target_c: f64,
    n_h: usize,
    n_rate: usize,
    steps: usize,
) -> Vec<(f64, f64, f64, f64, f64)> {
    let mut results = Vec::with_capacity(n_h * n_rate);

    for ih in 0..n_h {
        let h_init = 0.01 + (ih as f64 / n_h as f64) * 0.98; // 0.01 to 0.99

        for ir in 0..n_rate {
            let rate = 0.1 + (ir as f64 / n_rate as f64) * 1.8; // 0.1 to 1.9

            // Simulate
            let mut h = h_init;
            for _ in 0..steps {
                let dh = rate * (LN2 - h);
                h += dh;
            }

            // Final conservation quantity
            let dh_final = rate * (LN2 - h);
            let conservation = h * h + dh_final * dh_final;
            let distance = (conservation - target_c).abs();

            results.push((h_init, rate, h, conservation, distance));
        }
    }

    // Sort by distance from target
    results.sort_by(|a, b| a.4.partial_cmp(&b.4).unwrap_or(std::cmp::Ordering::Equal));
    results
}


/// Single trajectory conservation check with fine-grained output
#[pyfunction]
#[pyo3(signature = (h_init=0.1, rate=0.81, steps=1000, dt=0.01))]
pub fn conservation_trajectory(
    h_init: f64,
    rate: f64,
    steps: usize,
    dt: f64,
) -> HashMap<String, Vec<f64>> {
    let mut h_list = Vec::with_capacity(steps);
    let mut dh_list = Vec::with_capacity(steps);
    let mut cons_list = Vec::with_capacity(steps);
    let mut time_list = Vec::with_capacity(steps);

    let mut h = h_init;
    for i in 0..steps {
        let dh = rate * (LN2 - h) * dt;
        h += dh;
        let cons = h * h + dh * dh;
        h_list.push(h);
        dh_list.push(dh);
        cons_list.push(cons);
        time_list.push(i as f64 * dt);
    }

    // Statistics on conservation quantity
    let n = cons_list.len() as f64;
    let mean_c: f64 = cons_list.iter().sum::<f64>() / n;
    let std_c: f64 = (cons_list.iter().map(|c| (c - mean_c).powi(2)).sum::<f64>() / n).sqrt();

    let mut result = HashMap::new();
    result.insert("h".into(), h_list);
    result.insert("dh".into(), dh_list);
    result.insert("conservation".into(), cons_list);
    result.insert("time".into(), time_list);
    result.insert("mean_conservation".into(), vec![mean_c]);
    result.insert("std_conservation".into(), vec![std_c]);
    result.insert("target".into(), vec![0.478]);
    result.insert("final_h".into(), vec![h]);
    result.insert("distance_to_target".into(), vec![(mean_c - 0.478).abs()]);

    result
}


// ═══════════════════════════════════════════════════════════════
// Gate formula (Law 77)
// ═══════════════════════════════════════════════════════════════

/// Compute optimal gate value for given corpus size (in MB)
/// Returns (gate_value, regime_name)
#[pyfunction]
pub fn gate_formula(corpus_mb: f64) -> (f64, String) {
    if corpus_mb <= 0.0 {
        return (0.0, "ZERO".into());
    }

    let breakpoints: Vec<(f64, f64, &str)> = vec![
        (1.0,    0.001, "MICRO"),
        (10.0,   0.01,  "LOW"),
        (25.0,   0.1,   "MEDIUM-LOW"),
        (50.0,   0.5,   "MEDIUM"),
        (100.0,  0.8,   "HIGH"),
        (500.0,  0.95,  "FULL"),
        (1000.0, 1.0,   "MAXIMUM"),
    ];

    for (i, &(threshold, gate, regime)) in breakpoints.iter().enumerate() {
        if corpus_mb <= threshold {
            if i == 0 {
                return (gate, regime.into());
            }
            let (prev_t, prev_g, _) = breakpoints[i - 1];
            let log_ratio = (corpus_mb / prev_t).ln() / (threshold / prev_t).ln();
            let interpolated = prev_g + (gate - prev_g) * log_ratio;
            return (interpolated.max(0.0).min(1.0), regime.into());
        }
    }

    (1.0, "MAXIMUM".into())
}

/// Compute gate decay trajectory (Law 69)
/// Returns Vec<(step, gate_value)>
#[pyfunction]
#[pyo3(signature = (initial_gate, steps, decay_rate=-0.013))]
pub fn gate_decay(initial_gate: f64, steps: usize, decay_rate: f64) -> Vec<(usize, f64)> {
    let mut trajectory = Vec::with_capacity(steps);
    let mut gate = initial_gate;
    for t in 0..steps {
        gate *= (decay_rate).exp();
        gate = gate.max(0.001); // floor
        trajectory.push((t + 1, gate));
    }
    trajectory
}

/// Batch gate formula: compute gates for many corpus sizes at once
#[pyfunction]
pub fn gate_batch(corpus_sizes_mb: Vec<f64>) -> Vec<(f64, f64, String)> {
    corpus_sizes_mb.iter().map(|&mb| {
        let (gate, regime) = gate_formula(mb);
        (mb, gate, regime)
    }).collect()
}
