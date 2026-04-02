"""telescope.py — All 16 lenses via Rust (telescope_rs)

Usage:
    import telescope_rs
    telescope_rs.consciousness_scan(data)
    telescope_rs.topology_scan(data)
    telescope_rs.causal_scan(data)
    telescope_rs.gravity_scan(data)
    telescope_rs.thermo_scan(data)
    telescope_rs.wave_scan(data)
    telescope_rs.evolution_scan(data)
    telescope_rs.info_scan(data)
    telescope_rs.quantum_scan(data)
    telescope_rs.em_scan(data)
    telescope_rs.ruler_scan(data)
    telescope_rs.triangle_scan(data)
    telescope_rs.compass_scan(data)
    telescope_rs.mirror_scan(data)
    telescope_rs.scale_scan(data)
    telescope_rs.quantum_microscope_scan(data)

All functions take numpy ndarray (N_samples, N_features) → dict.
"""
import telescope_rs

# Re-export all scan functions at module level
consciousness_scan = telescope_rs.consciousness_scan
topology_scan = telescope_rs.topology_scan
causal_scan = telescope_rs.causal_scan
gravity_scan = telescope_rs.gravity_scan
thermo_scan = telescope_rs.thermo_scan
wave_scan = telescope_rs.wave_scan
evolution_scan = telescope_rs.evolution_scan
info_scan = telescope_rs.info_scan
quantum_scan = telescope_rs.quantum_scan
em_scan = telescope_rs.em_scan
ruler_scan = telescope_rs.ruler_scan
triangle_scan = telescope_rs.triangle_scan
compass_scan = telescope_rs.compass_scan
mirror_scan = telescope_rs.mirror_scan
scale_scan = telescope_rs.scale_scan
quantum_microscope_scan = telescope_rs.quantum_microscope_scan
fast_mutual_info = telescope_rs.fast_mutual_info

ALL_SCANS = [
    consciousness_scan, topology_scan, causal_scan, gravity_scan,
    thermo_scan, wave_scan, evolution_scan, info_scan,
    quantum_scan, em_scan, ruler_scan, triangle_scan,
    compass_scan, mirror_scan, scale_scan, quantum_microscope_scan,
]


def full_scan(data):
    """Run all 16 lenses, return dict of lens_name → result dict."""
    import numpy as np
    data = np.asarray(data, dtype=np.float64)
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    return {
        'consciousness': consciousness_scan(data),
        'topology': topology_scan(data),
        'causal': causal_scan(data),
        'gravity': gravity_scan(data),
        'thermo': thermo_scan(data),
        'wave': wave_scan(data),
        'evolution': evolution_scan(data),
        'info': info_scan(data),
        'quantum': quantum_scan(data),
        'em': em_scan(data),
        'ruler': ruler_scan(data),
        'triangle': triangle_scan(data),
        'compass': compass_scan(data),
        'mirror': mirror_scan(data),
        'scale': scale_scan(data),
        'quantum_microscope': quantum_microscope_scan(data),
    }
