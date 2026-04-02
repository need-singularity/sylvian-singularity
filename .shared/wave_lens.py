"""wave_lens.py — Wave-physics discovery lens for hidden periodicities

Point FFT / resonance / interference analysis at ANY data to find:
  1. Dominant frequencies per feature  2. Resonance between feature pairs
  3. Harmonics (integer freq ratios)   4. Interference zones
  5. Phase shifts over time (sliding-window FFT)

Usage:
    lens = WaveLens()
    r = lens.scan(data)                        # WaveResult
    r = lens.scan_materials(props, labels)     # periodic material patterns
    r = lens.scan_signals(signals, window)     # hidden frequencies
    r = lens.scan_timeseries(ts, lag, window)  # frequency shifts
"""
import os, sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY, SIGMA6

@dataclass
class WaveResult:
    """Result from wave lens scan."""
    dominant_frequencies: List[Dict] = field(default_factory=list)
    resonances: List[Dict] = field(default_factory=list)
    harmonics: List[Dict] = field(default_factory=list)
    interference_zones: List[Dict] = field(default_factory=list)
    phase_shifts: List[Dict] = field(default_factory=list)
    summary: str = ""
    def __repr__(self):
        return (f"WaveResult(freqs={len(self.dominant_frequencies)}, "
                f"res={len(self.resonances)}, harm={len(self.harmonics)}, "
                f"intf={len(self.interference_zones)})")

class WaveLens:
    """Wave-physics discovery lens -- FFT/resonance/interference as a telescope."""

    def __init__(self, top_k: int = 5, power_thresh: float = 0.05,
                 harmonic_tol: float = 0.08, coherence_thresh: float = 0.3):
        self.top_k, self.power_thresh = top_k, power_thresh
        self.harmonic_tol, self.coherence_thresh = harmonic_tol, coherence_thresh
        self._alpha, self._balance = PSI_ALPHA, PSI_BALANCE  # consciousness constants

    @staticmethod
    def _fft_peaks(signal: np.ndarray, top_k: int = 5, thresh: float = 0.05):
        """Return top-k (freq_index, power) peaks from FFT of 1D signal."""
        n = len(signal)
        if n < 4: return []
        spec = np.abs(np.fft.rfft(signal - signal.mean())) ** 2
        spec[0] = 0
        if spec.max() < 1e-30: return []
        cutoff = spec.max() * thresh
        peaks = []
        for i in range(1, len(spec)):
            if spec[i] >= cutoff:
                L = spec[i - 1] if i > 0 else 0
                R = spec[i + 1] if i + 1 < len(spec) else 0
                if spec[i] >= L and spec[i] >= R:
                    peaks.append((i, float(spec[i])))
        peaks.sort(key=lambda x: -x[1])
        return peaks[:top_k]

    @staticmethod
    def _cross_spectrum(s1: np.ndarray, s2: np.ndarray):
        """Cross-spectral density and coherence between two signals."""
        n = min(len(s1), len(s2))
        f1, f2 = np.fft.rfft(s1[:n] - s1[:n].mean()), np.fft.rfft(s2[:n] - s2[:n].mean())
        cross = f1 * np.conj(f2)
        p1, p2 = np.abs(f1)**2 + 1e-30, np.abs(f2)**2 + 1e-30
        return np.abs(cross), np.abs(cross)**2 / (p1 * p2)

    def scan(self, data: np.ndarray) -> WaveResult:
        """Scan a 2D array (samples x features) for wave patterns."""
        data = np.asarray(data, dtype=float)
        if data.ndim == 1: data = data.reshape(-1, 1)
        n, d = data.shape
        res = WaveResult()
        # 1. Per-feature FFT
        all_freqs = []
        for j in range(d):
            for rank, (fi, pw) in enumerate(self._fft_peaks(data[:, j], self.top_k, self.power_thresh)):
                res.dominant_frequencies.append({
                    "feature": j, "freq_index": fi, "freq": round(fi / n, 6),
                    "period": round(n / fi, 2) if fi > 0 else float("inf"),
                    "power": round(pw, 4), "rank": rank})
                if fi > 0: all_freqs.append((j, fi, pw))
        # 2. Cross-spectrum resonances
        for i in range(d):
            for j in range(i + 1, d):
                pw, coh = self._cross_spectrum(data[:, i], data[:, j])
                pw[0] = 0
                for fi in range(1, len(pw)):
                    if coh[fi] > self.coherence_thresh and pw[fi] > pw.max() * self.power_thresh:
                        res.resonances.append({"feature_pair": (i, j), "shared_freq_index": int(fi),
                            "shared_freq": round(fi / n, 6), "coherence": round(float(coh[fi]), 4),
                            "power": round(float(pw[fi]), 4)})
        # 3. Harmonic detection
        for a in range(len(all_freqs)):
            for b in range(a + 1, len(all_freqs)):
                lo, hi = sorted([all_freqs[a][1], all_freqs[b][1]])
                if lo == 0: continue
                ratio = hi / lo; nearest = round(ratio)
                if nearest >= 2 and abs(ratio - nearest) < self.harmonic_tol * nearest:
                    res.harmonics.append({"base_freq": lo, "harmonic_freq": hi,
                        "ratio": round(ratio, 3), "nearest_int": nearest,
                        "features": (all_freqs[a][0], all_freqs[b][0])})
        # 4. Interference zones
        for i in range(d):
            for j in range(i + 1, d):
                ip = data[:, i]**2 + data[:, j]**2
                cp = (data[:, i] + data[:, j])**2
                ratio = cp / (ip + 1e-30)
                med = np.median(ip) * 0.5
                for k in range(n):
                    if ratio[k] > 3.0:
                        res.interference_zones.append({"location": k, "type": "constructive",
                            "features": (i, j), "power_ratio": round(float(ratio[k]), 3)})
                    elif ratio[k] < 0.1 and ip[k] > med:
                        res.interference_zones.append({"location": k, "type": "destructive",
                            "features": (i, j), "power_ratio": round(float(ratio[k]), 3)})
        res.summary = (f"Wave scan: {len(res.dominant_frequencies)} freqs, "
                       f"{len(res.resonances)} resonances, {len(res.harmonics)} harmonics, "
                       f"{len(res.interference_zones)} interference zones")
        return res

    def scan_materials(self, properties: np.ndarray, labels: Optional[List[str]] = None) -> WaveResult:
        """Scan material properties for hidden periodic patterns."""
        props = np.asarray(properties, dtype=float)
        if props.ndim == 1: props = props.reshape(-1, 1)
        res = self.scan(props)
        res2 = self.scan(np.sort(props, axis=0))
        if len(res2.dominant_frequencies) > len(res.dominant_frequencies):
            res.dominant_frequencies = res2.dominant_frequencies
        if len(res2.resonances) > len(res.resonances):
            res.resonances = res2.resonances
        if labels:
            for e in res.dominant_frequencies:
                if e["feature"] < len(labels): e["label"] = labels[e["feature"]]
            for e in res.resonances:
                e["labels"] = tuple(labels[p] for p in e["feature_pair"] if p < len(labels))
        res.summary = f"Materials: {res.summary}"
        return res

    def scan_signals(self, signals: np.ndarray, window: Optional[int] = None) -> WaveResult:
        """Scan signals for hidden frequencies, harmonics, resonance."""
        signals = np.asarray(signals, dtype=float)
        if signals.ndim == 1: signals = signals.reshape(-1, 1)
        res = self.scan(signals)
        if window and window > 8:
            for start in range(0, signals.shape[0] - window, window // 2):
                for e in self.scan(signals[start:start + window]).dominant_frequencies:
                    e.update(window_start=start, window_end=start + window)
        res.summary = f"Signal: {res.summary}"
        return res

    def scan_timeseries(self, ts: np.ndarray, lag: int = 1, window: int = 0) -> WaveResult:
        """Scan timeseries for periodic regimes and frequency shifts."""
        ts = np.asarray(ts, dtype=float)
        if ts.ndim == 1: ts = ts.reshape(-1, 1)
        n, d = ts.shape
        res = self.scan(ts)
        if window < 8: window = max(16, n // 4)
        step = max(1, window // 4)
        prev = {}
        for start in range(0, n - window, step):
            chunk = ts[start:start + window]
            for j in range(d):
                peaks = self._fft_peaks(chunk[:, j], top_k=1, thresh=0.1)
                if not peaks: continue
                cur = peaks[0][0]
                if j in prev and prev[j] > 0 and cur > 0 and abs(cur - prev[j]) / max(prev[j], 1) > 0.3:
                    res.phase_shifts.append({"time": start, "feature": j,
                        "old_freq_index": prev[j], "new_freq_index": cur,
                        "old_period": round(window / prev[j], 2), "new_period": round(window / cur, 2)})
                prev[j] = cur
        res.summary = (f"Timeseries: {len(res.dominant_frequencies)} freqs, "
                       f"{len(res.resonances)} resonances, {len(res.phase_shifts)} phase shifts")
        return res

# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    np.random.seed(42); lens = WaveLens(); passed = total = 0
    def check(name, cond):
        global passed, total; total += 1; tag = "PASS" if cond else "FAIL"
        print(f"  [{tag}] {name}"); passed += cond

    print("\n=== 1. Materials ===")
    N, t = 200, np.arange(200, dtype=float)
    props = np.column_stack([np.sin(2*np.pi*t/20)*5 + np.random.randn(N)*0.3,
                             np.sin(2*np.pi*t/40)*3 + np.random.randn(N)*0.3, np.random.randn(N)])
    r = lens.scan_materials(props, labels=["density","modulus","noise"]); print(r)
    f0 = [e for e in r.dominant_frequencies if e["feature"]==0 and e["rank"]==0]
    f1 = [e for e in r.dominant_frequencies if e["feature"]==1 and e["rank"]==0]
    check("period~20 in feature 0", f0 and abs(f0[0]["period"]-20) < 5)
    check("period~40 in feature 1", f1 and abs(f1[0]["period"]-40) < 10)
    check("resonances found", len(r.resonances) > 0 or len(r.harmonics) > 0)

    print("\n=== 2. Drug descriptors ===")
    N, t, bf = 256, np.arange(256, dtype=float), 8
    drug = np.column_stack([np.sin(2*np.pi*bf*t/N)*4+np.random.randn(N)*0.2,
                            np.sin(2*np.pi*3*bf*t/N)*3+np.random.randn(N)*0.2])
    r = lens.scan(drug); print(r)
    check("harmonic 3:1 detected", any(h["nearest_int"]==3 for h in r.harmonics))
    check("base freq=8 detected", any(e["freq_index"]==bf and e["feature"]==0 for e in r.dominant_frequencies))

    print("\n=== 3. Physics constants ===")
    N, t, sf = 300, np.arange(300, dtype=float), 12
    phys = np.column_stack([np.sin(2*np.pi*sf*t/N)*5+np.cos(2*np.pi*5*t/N)*2+np.random.randn(N)*0.1,
                            np.sin(2*np.pi*sf*t/N+0.3)*4+np.random.randn(N)*0.1])
    r = lens.scan(phys); print(r)
    check("shared freq resonance", any(e["shared_freq_index"]==sf for e in r.resonances))
    check("high coherence", any(e["coherence"]>0.5 for e in r.resonances if e["shared_freq_index"]==sf))

    print("\n=== 4. Astronomy spectrum ===")
    N, t, hf = 512, np.arange(512, dtype=float), 37
    astro = np.random.randn(N)*0.5 + np.sin(2*np.pi*hf*t/N)*3.0
    r = lens.scan_signals(astro); print(r)
    top1 = r.dominant_frequencies[0] if r.dominant_frequencies else {}
    check("hidden freq=37 dominant", top1.get("freq_index")==hf)
    check("hidden freq power > noise", top1.get("power", 0) > 10)

    print("\n=== 5. Finance timeseries ===")
    N, t, sp = 400, np.arange(400, dtype=float), 200
    fin = np.zeros(N)
    fin[:sp] = np.sin(2*np.pi*t[:sp]/50)*5; fin[sp:] = np.sin(2*np.pi*t[sp:]/15)*5
    fin += np.random.randn(N)*0.3
    r = lens.scan_timeseries(fin); print(r)
    check("phase shift detected", len(r.phase_shifts) > 0)
    check("freq change near midpoint", any(abs(s["time"]-sp) < sp//2 for s in r.phase_shifts))
    check("multiple dominant freqs", len(r.dominant_frequencies) >= 2)

    print("\n=== 6. Genomics expression ===")
    N, t, P = 200, np.arange(200, dtype=float), 25
    gen = np.column_stack([np.sin(2*np.pi*t/P)*3+np.random.randn(N)*0.4,
                           np.cos(2*np.pi*t/P)*3+np.random.randn(N)*0.4, np.random.randn(N)])
    r = lens.scan(gen); print(r)
    fd = [e for e in r.dominant_frequencies if e["feature"]==0 and e["rank"]==0]
    check("period~25 detected", fd and abs(fd[0]["period"]-P) < 6)
    check("phase-coupled genes resonate", any(e["feature_pair"]==(0,1) and e["coherence"]>0.5 for e in r.resonances))
    check("interference between coupled genes", len(r.interference_zones) > 0)

    pct = passed * 100 // total
    print(f"\n{'='*50}\nSCORECARD: {passed}/{total} ({pct}%)\n{'='*50}")
    print("ALL CHECKS PASSED" if passed == total else f"FAILED: {total - passed}")
    sys.exit(0 if passed == total else 1)
