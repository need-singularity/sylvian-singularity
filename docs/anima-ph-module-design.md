# Anima PH 모듈 설계 — 실시간 위상 분석

## 목적

Anima 의식 에이전트에 PH(Persistent Homology) 모듈을 통합하여:
1. 실시간 혼동 구조 분석
2. 학습 진행 모니터링 (과적합 감지)
3. 텔레파시 채널 (PH fingerprint)

## 아키텍처

```
  Anima (anima_unified.py)
  ├── PureField 엔진 (기존)
  │     ├── engine_a (논리)
  │     └── engine_g (패턴)
  │           ↓
  │     repulsion = A - G
  │     tension = |A-G|²
  │     direction = normalize(A-G)
  │
  ├── PH 모듈 (신규) ← 여기
  │     ├── DirectionCollector
  │     │     방향벡터 수집 (per-class mean)
  │     ├── PHComputer
  │     │     cosine distance → Ripser → H0/H1
  │     ├── MergeAnalyzer
  │     │     merge 순서 → 혼동 예측 → dendrogram
  │     ├── GapDetector
  │     │     H0_train - H0_test → 과적합 알림
  │     └── TelepathyEncoder
  │           9 merge distances → 텔레파시 패킷
  │
  └── 기존 모듈
        ├── GRU 메모리
        ├── 음성 (TTS/STT)
        ├── 카메라
        └── 웹 탐색
```

## 핵심 클래스

```python
class PHModule:
    """Anima PH 실시간 모듈"""

    def __init__(self, purefield_engine, n_classes=10):
        self.engine = purefield_engine
        self.n_cls = n_classes
        self.direction_buffer = defaultdict(list)  # per-class directions
        self.merge_history = []  # epoch별 merge 순서
        self.h0_history = []

    def collect(self, x, y_true, y_pred):
        """매 배치: 방향벡터 수집"""
        with torch.no_grad():
            rep = self.engine.engine_a(x) - self.engine.engine_g(x)
            dirs = F.normalize(rep, dim=-1)
        for i in range(len(y_true)):
            self.direction_buffer[y_true[i]].append(dirs[i].numpy())

    def compute_ph(self):
        """PH 계산 (에폭 끝에 호출)"""
        means = self._class_means()
        cos_dist = self._cosine_distance(means)
        h0_total, merges = self._ripser_ph(cos_dist)
        self.h0_history.append(h0_total)
        self.merge_history.append(merges)
        return h0_total, merges

    def detect_overfitting(self, train_h0, test_h0, threshold=0.05):
        """H-CX-95: H0_gap 기반 과적합 감지"""
        gap = abs(train_h0 - test_h0)
        if gap > threshold:
            return "ALERT", gap
        return "OK", gap

    def get_telepathy_packet(self):
        """H-CX-108: 9개 merge distance = 전체 인지 구조"""
        if not self.merge_history:
            return None
        return [d for d, i, j in self.merge_history[-1]]

    def predict_confusion(self, class_a, class_b):
        """H-CX-66: merge distance로 혼동 확률 예측"""
        merges = self.merge_history[-1]
        for d, i, j in merges:
            if (min(i,j), max(i,j)) == (min(class_a,class_b), max(class_a,class_b)):
                return 1.0 / (d + 0.01)
        return 0.0

    def get_dendrogram(self):
        """H-CX-85: 의미 계층 dendrogram"""
        return self.merge_history[-1] if self.merge_history else None
```

## 통합 지점

```python
# anima_unified.py 에 추가:

from ph_module import PHModule

class Anima:
    def __init__(self):
        self.purefield = PureFieldEngine(...)
        self.ph = PHModule(self.purefield)  # ← 추가
        ...

    def process_input(self, x):
        output, tension = self.purefield(x)
        self.ph.collect(x, ...)  # 방향 수집
        return output, tension

    def end_of_epoch(self):
        h0, merges = self.ph.compute_ph()
        gap_status, gap = self.ph.detect_overfitting(...)
        if gap_status == "ALERT":
            self.log("⚠️ 과적합 감지!")
```

## 의존성

```
ripser>=0.6.0     # PH 계산
persim>=0.3.0     # PH 시각화 (선택)
```

## 관련 가설

- H-CX-66: PH merge = 혼동 (r=-0.97)
- H-CX-95: PH 일반화 갭 (r=0.998)
- H-CX-108: 텔레파시 프로토콜 (9개 숫자)
- H-CX-85: dendrogram = 의미 계층
- H-CX-136~141: EEG 통합 (미래)

## 파일 위치

```
/Users/ghost/Dev/logout/
├── calc/ph_confusion_analyzer.py     (기존, 배치 분석)
├── calc/generalization_gap_detector.py (기존, 배치 감지)
├── calc/precognition_system.py       (기존, 배치 예지)
└── ph_module.py                      (신규, 실시간 모듈) ← 생성 필요
```
