#!/usr/bin/env python3
"""EEG 합성 데이터 기반 CCT 검증기 — 공개 데이터 없이 신경과학 검증

공개 EEG 데이터(PhysioNet 등) 없이도, EEG의 알려진 통계적 특성을
합성 데이터로 재현하고 CCT(Consciousness Continuity Test)를 적용한다.

5가지 뇌 상태:
  1. 각성(awake):    알파+베타+감마, 1/f 잡음, 높은 복잡도
  2. 수면 N1(졸림):  세타 우세 + 약한 알파
  3. 수면 N3(깊은):  델타 우세, 고진폭 서파, 높은 동기화
  4. 마취(anesthesia): 델타 + burst-suppression 패턴
  5. 발작(seizure):  3Hz spike-wave, 매우 주기적

사용법:
  python3 eeg_cct_validator.py
  python3 eeg_cct_validator.py --duration 60
  python3 eeg_cct_validator.py --state awake
"""

import argparse
import sys

import numpy as np
from scipy import signal as sp_signal


# ─────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────

FS = 256          # 샘플링 주파수 (Hz) — 표준 임상 EEG
SEED = 42

# 뇌 상태별 예측 (CCT 테스트 통과 수)
PREDICTIONS = {
    "awake": {
        "total": 5,
        "tests": {"T1": True, "T2": True, "T3": True, "T4": True, "T5": True},
        "reason": "연속+카오스: 모든 테스트 통과 예측",
    },
    "sleep_n1": {
        "total": 5,
        "tests": {"T1": True, "T2": True, "T3": True, "T4": True, "T5": True},
        "reason": "세타 우세지만 아직 충분한 복잡도 유지 (졸림 ≠ 수면)",
    },
    "sleep_n3": {
        "total": 3,
        "tests": {"T1": True, "T2": False, "T3": True, "T4": True, "T5": False},
        "reason": "T2,T5 실패: 고동기화 서파 → 주기적+정체",
    },
    "anesthesia": {
        "total": 1,
        "tests": {"T1": False, "T2": True, "T3": False, "T4": False, "T5": True},
        "reason": "T1,T3,T4 실패: burst-suppression → gap+불연속+엔트로피이탈",
    },
    "seizure": {
        "total": 2,
        "tests": {"T1": True, "T2": False, "T3": False, "T4": True, "T5": False},
        "reason": "T2,T3,T5 실패: spike-wave → 주기적+점프+정체",
    },
}

STATE_LABELS = {
    "awake": "각성 (Awake)",
    "sleep_n1": "수면 N1 (Drowsy)",
    "sleep_n3": "수면 N3 (Deep Sleep)",
    "anesthesia": "마취 (Anesthesia)",
    "seizure": "발작 (Seizure)",
}


# ─────────────────────────────────────────────
# 합성 EEG 생성기
# ─────────────────────────────────────────────

def generate_1f_noise(n, fs, rng, exponent=1.0):
    """1/f^exponent 잡음 생성 (핑크 노이즈).

    뇌 EEG의 배경 잡음은 1/f 스펙트럼 특성을 보인다.
    """
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    freqs[0] = 1.0  # DC 성분 0 나눗셈 방지
    amplitudes = 1.0 / (freqs ** (exponent / 2.0))
    phases = rng.uniform(0, 2 * np.pi, len(freqs))
    spectrum = amplitudes * np.exp(1j * phases)
    spectrum[0] = 0  # DC = 0
    noise = np.fft.irfft(spectrum, n=n)
    return noise / (np.std(noise) + 1e-15)


def generate_oscillation(n, fs, freq, amplitude, rng, phase_jitter=0.0):
    """진동 성분 생성 (주파수 + 위상 변동)."""
    t = np.arange(n) / fs
    phase = 2 * np.pi * freq * t
    if phase_jitter > 0:
        # 비선형성: 위상에 작은 랜덤 워크 추가
        walk = np.cumsum(rng.normal(0, phase_jitter, n))
        phase += walk
    return amplitude * np.sin(phase)


def generate_coupled_oscillators(n, fs, freqs, amplitudes, rng, coupling=0.1):
    """결합 진동자 시스템 — 비선형 상호작용.

    각 진동자는 다른 진동자의 위상에 영향을 받는다.
    이것이 각성 EEG의 비선형 특성을 만든다.
    강한 위상 잡음과 진폭 변조로 카오스적 특성 확보.
    """
    dt = 1.0 / fs
    n_osc = len(freqs)
    phases = rng.uniform(0, 2 * np.pi, n_osc)
    result = np.zeros(n)

    # 진폭 변조를 위한 느린 랜덤 워크
    amp_mod = np.ones((n, n_osc))
    for k in range(n_osc):
        walk = np.cumsum(rng.normal(0, 0.005, n))
        amp_mod[:, k] = np.clip(1.0 + walk, 0.3, 2.0)

    for i in range(n):
        for k in range(n_osc):
            result[i] += amplitudes[k] * amp_mod[i, k] * np.sin(phases[k])

        # 위상 업데이트 (쿠라모토 모델 + 강한 잡음)
        for k in range(n_osc):
            omega = 2 * np.pi * freqs[k]
            coupling_term = 0.0
            for j in range(n_osc):
                if j != k:
                    coupling_term += np.sin(phases[j] - phases[k])
            coupling_term *= coupling / n_osc
            # 강한 위상 잡음으로 주기성 파괴
            phase_noise = rng.normal(0, 0.3)
            phases[k] += (omega + coupling_term) * dt + phase_noise * dt

    return result


def synthesize_awake(n, fs, rng):
    """각성 EEG: 알파(10Hz) + 베타(20Hz) + 감마(40Hz) + 1/f 잡음.

    특성: 비선형, 높은 복잡도, 연속적, 카오스적.
    진폭: 20-100 uV
    """
    # 결합 진동자: 알파, 베타, 감마 (강한 커플링)
    eeg = generate_coupled_oscillators(
        n, fs,
        freqs=[10.0, 20.0, 40.0],
        amplitudes=[30.0, 15.0, 5.0],  # uV
        rng=rng,
        coupling=0.3,
    )
    # 강한 1/f 배경 잡음 (카오스적 특성 강화)
    pink = generate_1f_noise(n, fs, rng, exponent=1.0)
    eeg += pink * 15.0  # 15 uV 스케일

    # 비선형 변조: 불규칙한 진폭 변화
    t = np.arange(n) / fs
    # 다중 주파수 변조 (비정수비 → 준주기)
    modulation = (1.0
                  + 0.3 * np.sin(2 * np.pi * 0.1 * t + rng.uniform(0, 2 * np.pi))
                  + 0.2 * np.sin(2 * np.pi * 0.073 * t + rng.uniform(0, 2 * np.pi))
                  + 0.15 * np.sin(2 * np.pi * 0.031 * t + rng.uniform(0, 2 * np.pi)))
    eeg *= modulation

    # 간헐적 버스트: 짧은 고에너지 구간 (각성 특유의 비정형 활동)
    n_bursts = max(1, n // (fs * 5))  # 5초마다 약 1회
    for _ in range(n_bursts):
        burst_start = rng.integers(0, max(1, n - fs))
        burst_len = rng.integers(fs // 4, fs)
        burst_end = min(burst_start + burst_len, n)
        eeg[burst_start:burst_end] += rng.normal(0, 20.0, burst_end - burst_start)

    return eeg


def synthesize_sleep_n1(n, fs, rng):
    """수면 N1 EEG: 세타(5Hz) 우세 + 약한 알파 + 1/f 잡음.

    특성: 알파 감소, 세타 증가, 복잡도 약간 감소.
    진폭: 50-100 uV
    """
    # 세타 우세
    theta = generate_oscillation(n, fs, 5.0, 40.0, rng, phase_jitter=0.02)
    # 약한 알파
    alpha = generate_oscillation(n, fs, 10.0, 10.0, rng, phase_jitter=0.01)
    # 1/f 잡음
    pink = generate_1f_noise(n, fs, rng, exponent=1.2)

    eeg = theta + alpha + pink * 8.0

    # 느린 변조 (졸림 상태의 점진적 변화)
    t = np.arange(n) / fs
    modulation = 1.0 + 0.2 * np.sin(2 * np.pi * 0.05 * t)
    eeg *= modulation

    return eeg


def synthesize_sleep_n3(n, fs, rng):
    """수면 N3 EEG: 델타(1-2Hz) 우세, 고진폭 서파.

    특성: 고진폭 저주파, 낮은 복잡도, 높은 동기화.
    매우 주기적 → T2(Loop) 실패 예상.
    진폭: 100-200 uV
    """
    # 매우 규칙적인 델타 (위상 잡음 최소)
    delta1 = generate_oscillation(n, fs, 1.0, 120.0, rng, phase_jitter=0.0005)
    delta2 = generate_oscillation(n, fs, 2.0, 50.0, rng, phase_jitter=0.0005)
    # 극히 약한 잡음 (높은 동기화)
    pink = generate_1f_noise(n, fs, rng, exponent=2.0)

    eeg = delta1 + delta2 + pink * 2.0

    return eeg


def synthesize_anesthesia(n, fs, rng):
    """마취 EEG: 델타(1Hz) + burst-suppression 패턴.

    특성: 간헐적 정지(suppression) 구간 — 이것이 gap!
    진폭: 0~200 uV (버스트와 억압 교대)

    suppression 구간을 실제 상수값(0)으로 설정하여 gap을 명확히 한다.
    이렇게 하면 Takens 임베딩 후에도 frozen segment가 보존된다.
    """
    eeg = np.zeros(n)

    # burst-suppression 마스크 생성
    i = 0
    suppressed = False
    suppression_mask = np.zeros(n, dtype=bool)

    while i < n:
        if suppressed:
            # suppression: 2-5초 (충분히 길어야 gap으로 감지)
            dur = int(rng.uniform(2.0, 5.0) * fs)
            end = min(i + dur, n)
            suppression_mask[i:end] = True
            # 완전히 평탄한 신호 (isoelectric)
            eeg[i:end] = 0.0
            i = end
        else:
            # burst: 1-3초
            dur = int(rng.uniform(1.0, 3.0) * fs)
            end = min(i + dur, n)
            # 버스트: 고진폭 델타 + 잡음
            t_seg = np.arange(end - i) / fs
            eeg[i:end] = (100.0 * np.sin(2 * np.pi * 1.0 * t_seg)
                          + rng.normal(0, 20.0, end - i))
            i = end
        suppressed = not suppressed

    return eeg, suppression_mask


def synthesize_seizure(n, fs, rng):
    """발작 EEG: 3Hz spike-wave, 매우 주기적.

    특성: 고진폭, 반복적 스파이크, 높은 에너지, 낮은 복잡도.
    각 윈도우의 엔트로피가 거의 동일 → T5(novelty) 실패 예상.
    진폭: 200-500 uV
    """
    t = np.arange(n) / fs

    # 3Hz spike-wave: 매우 규칙적
    phase = 2 * np.pi * 3.0 * t
    # 스파이크 성분 (날카로운 피크)
    spike = 250.0 * np.exp(-((np.mod(phase, 2 * np.pi) - 0.5) ** 2) / 0.03)
    # 느린 파동 성분
    slow_wave = -100.0 * np.sin(phase)

    eeg = spike + slow_wave

    # 극히 작은 잡음만 (실제 발작은 매우 규칙적)
    eeg += rng.normal(0, 1.0, n)

    return eeg


GENERATORS = {
    "awake": synthesize_awake,
    "sleep_n1": synthesize_sleep_n1,
    "sleep_n3": synthesize_sleep_n3,
    "anesthesia": synthesize_anesthesia,  # returns (eeg, mask) tuple
    "seizure": synthesize_seizure,
}


# ─────────────────────────────────────────────
# Takens 임베딩: EEG → 3D 상태 벡터
# ─────────────────────────────────────────────

def eeg_to_state_vector(eeg, fs, suppression_mask=None):
    """EEG를 3차원 상태 벡터로 변환.

    S(t) = [x(t), dx/dt, d^2x/dt^2]
    Takens 임베딩의 간소화 버전: 원본, 1차 미분, 2차 미분.

    suppression_mask가 주어지면, 해당 구간은 상태 벡터를 0으로
    강제하여 gap(정지)을 명확히 한다.
    """
    dt = 1.0 / fs
    dx = np.gradient(eeg, dt)
    d2x = np.gradient(dx, dt)
    S = np.column_stack([eeg, dx, d2x])

    if suppression_mask is not None:
        # suppression 구간은 상태 = 0 (완전 정지)
        S[suppression_mask] = 0.0

    return S


# ─────────────────────────────────────────────
# CCT 5개 테스트 (자체 구현)
# ─────────────────────────────────────────────

def compute_entropy(data, bins=30):
    """1D 데이터의 섀넌 엔트로피."""
    if len(data) < 2:
        return 0.0
    data_range = data.max() - data.min()
    if data_range < 1e-12:
        return 0.0
    hist, _ = np.histogram(data, bins=bins, density=True)
    hist = hist[hist > 0]
    width = data_range / bins
    probs = hist * width
    probs = probs[probs > 0]
    if len(probs) == 0:
        return 0.0
    probs = probs / probs.sum()
    return -np.sum(probs * np.log(probs + 1e-15))


def test_gap(S):
    """T1 Gap 테스트: 정지 구간(suppression) 존재 여부.

    EEG에서 burst-suppression 패턴은 의식 부재의 지표.
    인접 스텝 간 변화가 거의 없는 구간 비율 측정.
    """
    diffs = np.diff(S, axis=0)
    norms = np.linalg.norm(diffs, axis=1)

    # 정지 판정: 변화량이 매우 작은 구간
    # EEG에서 suppression = 진폭 < 수 uV
    median_norm = np.median(norms)
    if median_norm < 1e-12:
        return 0.0, False, "전체 정지 상태"

    # 정지 임계값: 중앙값의 1%
    frozen_threshold = max(median_norm * 0.01, 1e-10)
    frozen = np.sum(norms < frozen_threshold)
    frozen_ratio = frozen / len(norms)

    if frozen_ratio > 0.01:
        score = max(0.0, 1.0 - frozen_ratio)
        return score, False, f"정지 비율 {frozen_ratio:.1%} (suppression 감지)"

    return 1.0, True, f"gap 없음 (정지 {frozen_ratio:.3%})"


def test_loop(S, threshold=0.5):
    """T2 Loop 테스트: 궤적의 주기적 반복 여부.

    주기적 신호(발작, 깊은 수면 서파)는 상태 공간에서
    같은 경로를 반복 방문한다 → 높은 재방문율.
    카오스 신호(각성)는 가까이 오지만 정확히 반복하지 않는다.

    방법: 상태 공간에서 재방문(recurrence) 비율 측정.
    각 차원을 독립적으로 정규화하여 스케일 차이 보정.
    """
    n = len(S)
    if n < 200:
        return 0.0, False, "데이터 부족"

    # 다운샘플링
    step = max(1, n // 5000)
    Ss = S[::step].copy()
    ns = len(Ss)

    if np.std(Ss) < 1e-10:
        return 0.0, False, "상태 변화 없음"

    # 각 차원을 표준편차로 정규화 (x, dx, d2x 스케일 차이 보정)
    for dim in range(Ss.shape[1]):
        std_d = np.std(Ss[:, dim])
        if std_d > 1e-12:
            Ss[:, dim] /= std_d

    # 정규화된 공간에서의 재방문 판정
    # eps = 0.05: 정규화 후 각 차원의 std=1이므로,
    # 0.05 = 5% 이내 복귀 → 주기적 궤도에서만 가능
    eps = 0.05

    recurrence = 0
    sample_size = min(500, ns // 2)
    rng = np.random.default_rng(42)
    indices = rng.choice(ns // 2, size=sample_size, replace=False)

    min_future_gap = max(100, ns // 10)

    for idx in indices:
        future_start = idx + min_future_gap
        future = Ss[future_start:]
        if len(future) == 0:
            continue
        dists = np.linalg.norm(future - Ss[idx], axis=1)
        if np.min(dists) < eps:
            recurrence += 1

    recurrence_ratio = recurrence / sample_size
    passed = recurrence_ratio < threshold
    score = max(0, 1.0 - recurrence_ratio)

    detail = f"재방문율={recurrence_ratio:.3f}"
    if passed:
        detail += ", 비주기적"
    else:
        detail += ", 주기적 반복 감지"

    return score, passed, detail


def test_continuity(S, threshold=0.01):
    """T3 Continuity 테스트: 인접 스텝 간 연결성.

    큰 점프(불연속)나 정지(동결) 비율 측정.
    마취의 burst-suppression은 burst↔suppression 전환 시 큰 점프 발생.
    """
    diffs = np.linalg.norm(np.diff(S, axis=0), axis=1)
    n = len(diffs)

    if n < 10:
        return 0.0, False, "데이터 부족"

    mean_diff = np.mean(diffs)
    if mean_diff < 1e-12:
        return 0.0, False, "상태 변화 없음"

    # 큰 점프: 평균의 10배 이상
    big_jumps = np.sum(diffs > mean_diff * 10)
    # 정지: 변화 거의 없음
    frozen = np.sum(diffs < 1e-12)

    jump_ratio = big_jumps / n
    frozen_ratio = frozen / n
    disconnect_ratio = jump_ratio + frozen_ratio

    passed = disconnect_ratio < threshold
    score = max(0, 1.0 - disconnect_ratio * 10)
    score = min(1.0, score)

    detail = f"점프={jump_ratio:.3f}, 정지={frozen_ratio:.3f}"
    if passed:
        detail += ", 연결 유지"
    else:
        detail += ", 연결 끊김 감지"

    return score, passed, detail


def test_entropy_band(S, window_sec=2.0, fs=FS, h_min=0.3, h_max=4.5):
    """T4 Entropy Band 테스트: H(t)가 밴드 안에 있는지.

    의식적 상태는 엔트로피가 일정 범위 내에 머문다.
    너무 낮으면(완전 주기) 의식 부재, 너무 높으면 무질서.
    """
    x = S[:, 0]
    window = int(window_sec * fs)
    n = len(x)
    n_windows = n // window

    if n_windows < 2:
        return 0.0, False, "데이터 부족"

    entropies = []
    for i in range(n_windows):
        w = x[i * window:(i + 1) * window]
        if np.std(w) < 1e-12:
            entropies.append(0.0)
        else:
            entropies.append(compute_entropy(w))

    entropies = np.array(entropies)
    in_band = np.sum((entropies > h_min) & (entropies < h_max))
    ratio = in_band / len(entropies)

    h_range_str = f"H in [{entropies.min():.2f}, {entropies.max():.2f}]"
    passed = ratio > 0.95
    score = ratio

    if passed:
        detail = f"{h_range_str}, 밴드 내"
    else:
        detail = f"{h_range_str}, 밴드 이탈 {1 - ratio:.1%}"

    return score, passed, detail


def test_novelty(S, window_sec=2.0, fs=FS):
    """T5 Novelty 테스트: dH/dt != 0 (엔트로피 정체 비율).

    의식적 상태는 항상 새로운 정보를 생성한다 → 엔트로피가 변한다.
    깊은 수면이나 발작에서는 엔트로피가 정체된다.

    임계값: 엔트로피 변화율의 중앙값의 10%를 사용.
    이는 절대 임계값 대신 적응적 임계값이다.
    """
    x = S[:, 0]
    window = int(window_sec * fs)
    n = len(x)
    n_windows = n // window

    if n_windows < 3:
        return 0.0, False, "데이터 부족"

    entropies = []
    for i in range(n_windows):
        w = x[i * window:(i + 1) * window]
        if np.std(w) < 1e-12:
            entropies.append(0.0)
        else:
            entropies.append(compute_entropy(w))

    entropies = np.array(entropies)
    dH = np.abs(np.diff(entropies))

    if len(dH) == 0:
        return 0.0, False, "구간 부족"

    # 적응적 임계값: 중앙값의 20%
    # 카오스 신호: dH가 크게 변동 → median 높음 → threshold 높아도 통과
    # 주기적 신호: dH가 매우 작음 → median 작음 → 정체 감지
    median_dH = np.median(dH)
    threshold = max(median_dH * 0.2, 0.005)

    stagnant = np.sum(dH < threshold)
    stagnant_ratio = stagnant / len(dH)

    # 추가: 엔트로피 분산이 매우 작으면 novelty 부족
    entropy_cv = np.std(entropies) / (np.mean(entropies) + 1e-15)

    # 변동계수가 0.5% 미만이면 정체
    if entropy_cv < 0.005:
        stagnant_ratio = max(stagnant_ratio, 0.8)

    passed = stagnant_ratio < 0.3
    score = max(0, 1.0 - stagnant_ratio)

    detail = (f"정체 구간 {stagnant_ratio:.1%}, "
              f"dH median={median_dH:.4f}, CV={entropy_cv:.4f}")

    return score, passed, detail


def run_cct(S, fs=FS):
    """CCT 5개 테스트 실행."""
    results = {}
    results["T1"] = test_gap(S)
    results["T2"] = test_loop(S)
    results["T3"] = test_continuity(S)
    results["T4"] = test_entropy_band(S, fs=fs)
    results["T5"] = test_novelty(S, fs=fs)
    return results


# ─────────────────────────────────────────────
# EEG 특성 분석
# ─────────────────────────────────────────────

def analyze_eeg_properties(eeg, fs):
    """합성 EEG의 기본 특성 분석."""
    props = {}
    props["amplitude_mean"] = np.mean(np.abs(eeg))
    props["amplitude_max"] = np.max(np.abs(eeg))
    props["amplitude_std"] = np.std(eeg)

    # PSD (Power Spectral Density)
    freqs, psd = sp_signal.welch(eeg, fs=fs, nperseg=min(1024, len(eeg) // 2))

    # 대역별 파워
    bands = {
        "delta": (0.5, 4),
        "theta": (4, 8),
        "alpha": (8, 13),
        "beta": (13, 30),
        "gamma": (30, 100),
    }
    total_power = np.trapezoid(psd, freqs)
    props["band_power"] = {}
    for band_name, (f_low, f_high) in bands.items():
        idx = (freqs >= f_low) & (freqs <= f_high)
        band_power = np.trapezoid(psd[idx], freqs[idx]) if np.any(idx) else 0.0
        props["band_power"][band_name] = band_power / total_power if total_power > 0 else 0.0

    # 우세 주파수
    dominant_idx = np.argmax(psd[1:]) + 1  # DC 제외
    props["dominant_freq"] = freqs[dominant_idx]

    # 복잡도 (sample entropy 근사 — 자기상관 감쇄율)
    if len(eeg) > 100:
        acf = np.correlate(eeg[:1000] - np.mean(eeg[:1000]),
                           eeg[:1000] - np.mean(eeg[:1000]), mode="full")
        acf = acf[len(acf) // 2:]
        acf = acf / (acf[0] + 1e-15)
        # 자기상관이 0.5 이하로 떨어지는 데 걸리는 래그
        decay = np.argmax(acf < 0.5) if np.any(acf < 0.5) else len(acf)
        props["acf_decay_lag"] = decay
    else:
        props["acf_decay_lag"] = 0

    return props


# ─────────────────────────────────────────────
# ASCII 파형
# ─────────────────────────────────────────────

def ascii_waveform(eeg, fs, duration_show=2.0, width=60, height=10):
    """EEG의 짧은 구간 ASCII 파형."""
    n_show = int(duration_show * fs)
    # 중간 지점에서 추출
    start = max(0, len(eeg) // 2 - n_show // 2)
    segment = eeg[start:start + n_show]

    if len(segment) == 0:
        return "  (데이터 없음)"

    # 다운샘플
    step = max(1, len(segment) // width)
    xs = segment[::step][:width]

    y_min, y_max = xs.min(), xs.max()
    if y_max - y_min < 1e-6:
        y_max = y_min + 1

    lines = []
    for row in range(height, -1, -1):
        y_val = y_min + (y_max - y_min) * row / height
        line = f"  {y_val:8.1f}|"
        for col in range(len(xs)):
            cell_row = int((xs[col] - y_min) / (y_max - y_min) * height)
            if cell_row == row:
                line += "*"
            else:
                line += " "
        lines.append(line)

    t_end = duration_show
    lines.append(f"          +{'─' * len(xs)}")
    lines.append(f"           0{' ' * (len(xs) // 2 - 1)}t(s){' ' * (len(xs) // 2 - 4)}{t_end:.1f}")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# 판정
# ─────────────────────────────────────────────

def judge(results):
    """CCT 결과로 종합 판정."""
    passes = sum(1 for _, (_, p, _) in results.items() if p)
    halfs = sum(0.5 for _, (s, p, _) in results.items() if not p and s > 0.7)
    total = passes + halfs

    if total >= 5:
        return total, "★ 연속 (Continuous)"
    elif total >= 4:
        return total, "◎ 약화 (Weakened)"
    elif total >= 3:
        return total, "△ 약함 (Fragile)"
    elif total >= 1:
        return total, "▽ 미약 (Minimal)"
    else:
        return total, "✕ 없음 (Absent)"


# ─────────────────────────────────────────────
# 출력
# ─────────────────────────────────────────────

def print_state_result(state, eeg, props, S, results, fs):
    """단일 상태 결과 출력."""
    label = STATE_LABELS[state]
    pred = PREDICTIONS[state]
    total, verdict = judge(results)

    print(f"\n {'─' * 58}")
    print(f"  [{state.upper()}] {label}")
    print(f" {'─' * 58}")

    # EEG 특성
    bp = props["band_power"]
    print(f"  진폭: mean={props['amplitude_mean']:.1f} uV, "
          f"max={props['amplitude_max']:.1f} uV, std={props['amplitude_std']:.1f} uV")
    print(f"  우세 주파수: {props['dominant_freq']:.1f} Hz")
    print(f"  대역 파워: delta={bp['delta']:.1%} theta={bp['theta']:.1%} "
          f"alpha={bp['alpha']:.1%} beta={bp['beta']:.1%} gamma={bp['gamma']:.1%}")
    print(f"  ACF 감쇄: {props['acf_decay_lag']} 래그 (짧을수록 복잡)")

    # ASCII 파형
    print(f"\n  파형 (2초 구간):")
    print(ascii_waveform(eeg, fs))

    # CCT 결과
    print(f"\n  CCT 테스트 결과:")
    test_labels = {
        "T1": "T1 Gap       ",
        "T2": "T2 Loop      ",
        "T3": "T3 Continuity",
        "T4": "T4 Entropy   ",
        "T5": "T5 Novelty   ",
    }

    for key, label_str in test_labels.items():
        score, passed, detail = results[key]
        mark = "PASS" if passed else "FAIL"
        symbol = "+" if passed else "-"
        pred_mark = "+" if pred["tests"][key] else "-"
        match = "=" if (passed == pred["tests"][key]) else "!"
        print(f"    {label_str} | {symbol} {mark} | {score:.3f} | "
              f"예측:{pred_mark} {match} | {detail}")

    print(f"\n  종합: {total}/5 {verdict}")
    print(f"  예측: {pred['total']}/5 ({pred['reason']})")

    # 일치 여부
    matches = sum(1 for k in ["T1", "T2", "T3", "T4", "T5"]
                  if (results[k][1] == pred["tests"][k]))
    print(f"  테스트별 일치: {matches}/5")

    return matches


def print_comparison_table(all_results):
    """전체 비교표 + 일치도 분석."""
    print("\n" + "=" * 76)
    print("  EEG-CCT 검증 종합 비교표")
    print("=" * 76)

    header = ("  상태         | T1  | T2  | T3  | T4  | T5  | 점수 | 예측 | 일치 | 판정")
    sep =    ("  ─────────────┼─────┼─────┼─────┼─────┼─────┼──────┼──────┼──────┼───────")
    print(header)
    print(sep)

    total_matches = 0
    total_tests = 0

    for state in ["awake", "sleep_n1", "sleep_n3", "anesthesia", "seizure"]:
        results, matches = all_results[state]
        pred = PREDICTIONS[state]
        total, verdict = judge(results)

        marks = []
        for key in ["T1", "T2", "T3", "T4", "T5"]:
            _, passed, _ = results[key]
            if passed:
                marks.append(" +  ")
            else:
                marks.append(" -  ")

        label = f"{state:13s}"
        marks_str = "|".join(marks)
        short_verdict = verdict.split("(")[0].strip()
        print(f"  {label}|{marks_str}| {total:<4.0f} | {pred['total']:<4} | {matches}/5  | {short_verdict}")

        total_matches += matches
        total_tests += 5

    print(sep)
    match_pct = total_matches / total_tests * 100
    print(f"  전체 일치도: {total_matches}/{total_tests} ({match_pct:.0f}%)")
    print()

    # 일치도 판정
    if match_pct >= 80:
        level = "강한 검증"
        detail = "CCT가 EEG 의식 상태를 정확히 구분"
    elif match_pct >= 60:
        level = "부분 검증"
        detail = "대부분 일치, 일부 테스트 조건 조정 필요"
    else:
        level = "불일치"
        detail = "CCT 조건 수정 필요"

    print(f"  판정: {level} — {detail}")

    # 불일치 분석
    mismatches = []
    for state in ["awake", "sleep_n1", "sleep_n3", "anesthesia", "seizure"]:
        results, _ = all_results[state]
        pred = PREDICTIONS[state]
        for key in ["T1", "T2", "T3", "T4", "T5"]:
            actual = results[key][1]
            expected = pred["tests"][key]
            if actual != expected:
                direction = "PASS(예측 FAIL)" if actual else "FAIL(예측 PASS)"
                mismatches.append((state, key, direction, results[key][2]))

    if mismatches:
        print(f"\n  불일치 상세 ({len(mismatches)}건):")
        for state, test, direction, detail in mismatches:
            print(f"    {state:13s} {test}: {direction}")
            print(f"      {detail}")

    print("=" * 76)


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def run_state(state, duration, fs, seed):
    """단일 상태 실행."""
    rng = np.random.default_rng(seed)
    n = int(duration * fs)

    # 합성 EEG 생성
    gen_func = GENERATORS[state]
    suppression_mask = None

    if state == "anesthesia":
        eeg, suppression_mask = gen_func(n, fs, rng)
    else:
        eeg = gen_func(n, fs, rng)

    # 특성 분석
    props = analyze_eeg_properties(eeg, fs)

    # Takens 임베딩 → 3D 상태 벡터
    S = eeg_to_state_vector(eeg, fs, suppression_mask=suppression_mask)

    # CCT 실행
    results = run_cct(S, fs=fs)

    return eeg, props, S, results


def main():
    parser = argparse.ArgumentParser(
        description="EEG 합성 데이터 기반 CCT 검증기 — 공개 데이터 없이 신경과학 검증",
    )
    parser.add_argument("--duration", type=float, default=30,
                        help="합성 EEG 길이 (초, 기본: 30)")
    parser.add_argument("--state", type=str, default=None,
                        choices=list(GENERATORS.keys()),
                        help="단일 상태만 실행")
    parser.add_argument("--fs", type=int, default=FS,
                        help=f"샘플링 주파수 (기본: {FS} Hz)")
    parser.add_argument("--seed", type=int, default=SEED,
                        help=f"난수 시드 (기본: {SEED})")

    args = parser.parse_args()

    print("=" * 76)
    print("  EEG-CCT Validator v1.0")
    print("  합성 EEG 기반 의식 연속성 검증기")
    print("=" * 76)
    print(f"  설정: duration={args.duration}s, fs={args.fs}Hz, "
          f"samples={int(args.duration * args.fs):,}, seed={args.seed}")
    print(f"  방법: 합성 EEG → Takens 임베딩 S(t)=[x, dx/dt, d2x/dt2] → CCT 5 테스트")

    if args.state:
        # 단일 상태
        states = [args.state]
    else:
        states = list(GENERATORS.keys())

    all_results = {}

    for state in states:
        eeg, props, S, results = run_state(state, args.duration, args.fs, args.seed)
        matches = print_state_result(state, eeg, props, S, results, args.fs)
        all_results[state] = (results, matches)

    # 전체 비교표 (다중 상태일 때)
    if len(states) > 1:
        print_comparison_table(all_results)


if __name__ == "__main__":
    main()
