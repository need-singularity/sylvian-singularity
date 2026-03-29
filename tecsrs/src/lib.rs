// tecsrs — TECS-L Rust acceleration library
// Phases: sieves, search, monte_carlo, grid, ode, atlas

use pyo3::prelude::*;

mod sieves;
mod search;
mod monte_carlo;
mod grid;
mod ode;
mod atlas;
mod perfect;

/// TECS-L Rust acceleration module
#[pymodule]
fn tecsrs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Phase 1: Sieves
    m.add_class::<sieves::SieveTables>()?;
    m.add_function(wrap_pyfunction!(sieves::sieve_all, m)?)?;
    m.add_function(wrap_pyfunction!(sieves::sieve_sigma, m)?)?;
    m.add_function(wrap_pyfunction!(sieves::sieve_tau, m)?)?;
    m.add_function(wrap_pyfunction!(sieves::sieve_phi, m)?)?;

    // Phase 2: Search
    m.add_class::<search::DfsEngine>()?;
    m.add_class::<search::SearchMatch>()?;
    m.add_function(wrap_pyfunction!(search::dfs_search, m)?)?;
    m.add_function(wrap_pyfunction!(search::reachability, m)?)?;

    // Phase 3: Monte Carlo
    m.add_class::<monte_carlo::TexasResult>()?;
    m.add_function(wrap_pyfunction!(monte_carlo::texas_sharpshooter, m)?)?;
    m.add_function(wrap_pyfunction!(monte_carlo::bootstrap_ci, m)?)?;
    m.add_function(wrap_pyfunction!(monte_carlo::bootstrap_stat, m)?)?;
    m.add_function(wrap_pyfunction!(monte_carlo::permutation_test, m)?)?;

    // Phase 4: Grid
    m.add_function(wrap_pyfunction!(grid::gz_ratio, m)?)?;
    m.add_function(wrap_pyfunction!(grid::gz_zone_stats, m)?)?;
    m.add_function(wrap_pyfunction!(grid::grid_scan, m)?)?;

    // Phase 5: ODE
    m.add_function(wrap_pyfunction!(ode::lorenz, m)?)?;
    m.add_function(wrap_pyfunction!(ode::rossler, m)?)?;
    m.add_function(wrap_pyfunction!(ode::chen, m)?)?;
    m.add_function(wrap_pyfunction!(ode::chua, m)?)?;
    m.add_function(wrap_pyfunction!(ode::simulate_all, m)?)?;

    // Phase 6: Atlas
    m.add_function(wrap_pyfunction!(atlas::scan_hypotheses, m)?)?;
    m.add_function(wrap_pyfunction!(atlas::scan_multi_repo, m)?)?;
    m.add_function(wrap_pyfunction!(atlas::parse_grade, m)?)?;
    m.add_function(wrap_pyfunction!(atlas::parse_refs, m)?)?;

    // Phase 7: Perfect number chains
    m.add_function(wrap_pyfunction!(perfect::sigma_chain, m)?)?;
    m.add_function(wrap_pyfunction!(perfect::sigma_chain_analysis, m)?)?;
    m.add_function(wrap_pyfunction!(perfect::mersenne_bootstrap, m)?)?;
    m.add_function(wrap_pyfunction!(perfect::find_sigma_phi_tau, m)?)?;
    m.add_function(wrap_pyfunction!(perfect::uniqueness_score, m)?)?;

    Ok(())
}
