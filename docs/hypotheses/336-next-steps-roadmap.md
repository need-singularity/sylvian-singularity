# 가설 336: 다음 단계 로드맵 — 5개 미진행 분야

> **PureField 5/5 검증 완료 후, 다음 확장 방향. 난이도/의존성별 정리.**

## 즉시 가능 (CPU, 공개 데이터)

```
  1. Fisher 정보 심화 (H325)
     현재: r=-0.12 (약함, 2000 샘플)
     다음: 전체 테스트셋 + per-class Fisher + Hessian 근사
     → calc/fisher_analyzer.py 작성

  2. GNN 분자 (H328) — sklearn proxy 확장
     현재: Wine(천장) + Cancer(독성 AUROC 0.40 실패)
     다음: Digits를 "분자 특성" proxy로, PureField 적용
     → boundary r=-0.79 발견을 다른 데이터셋에서 재현
```

## 외부 데이터 필요

```
  3. EEG 실제 데이터 (H322)
     데이터: PhysioNet EEG Motor Movement (공개)
     다운로드: mne 라이브러리 or wget
     → pip install mne → 실제 뇌파에서 PureField 테스트
     현재: 합성 EEG proxy (awake≈sleep>>drowsy)

  4. 멀티모달 (H323)
     데이터: MNIST + 텍스트 설명 (합성 가능)
     또는: CIFAR + 클래스 이름 임베딩
     → 모달별 PureField → 교차 모달 장력
```

## GPU 필요 (Windows/RunPod)

```
  5. 골든MoE LLM (H327, H335)
     리포: golden-llama (logout_test)
     현재: PPL 4634 (step 500)
     다음: PureField layer 추가, tension-PPL 상관 측정
     → 윈도우 RTX 5070 또는 RunPod A100
```

## 우선순위

```
  1순위: Fisher 심화 (즉시, CPU) — H325 강화
  2순위: EEG 실제 (mne 설치) — H322 실제 검증
  3순위: 멀티모달 합성 (CPU) — H323 첫 실험
  4순위: GNN proxy 확장 (CPU) — H328 boundary 재현
  5순위: 골든MoE LLM (GPU) — H335 PureField LLM
```

## 상태: 📋 로드맵 (PureField 완성 후 확장 방향)
