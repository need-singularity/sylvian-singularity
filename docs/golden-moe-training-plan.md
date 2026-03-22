# Golden MoE 훈련 계획서

## 1. 현재 상태

### 모델 구성
- **베이스 모델**: TinyLlama/TinyLlama-1.1B-Chat-v1.0 (1.1B 파라미터)
- **Expert 수**: 8개, 활성 비율 62.5% (5/8 Expert 활성)
- **억제율 I**: 0.375 (골든존 범위 [0.213, 0.500] 내)
- **온도**: T = e ≈ 2.718 (볼츠만 라우터)
- **레이어**: 22개 전체 MoE 변환 완료
- **Expert당 intermediate**: 704 (5632 / 8)

### 훈련 결과 (500 스텝)
- **PPL**: ~4634 (500 스텝 기준)
- **훈련 방식**: 라우터만 파인튜닝 (Expert 동결)
- **데이터셋**: wikitext-2-raw-v1 (train split, ~23K 샘플 중 일부)
- **배치 크기**: 8, 학습률: 1e-4, max_length: 256
- **결과**: golden-test-finetuned/ 에 저장 완료

### 문제 진단
- PPL 4634는 사실상 무작위 출력 수준 (coherent한 텍스트 생성 불가)
- 원인 1: 500 스텝으로는 라우터가 Expert 조합을 충분히 학습하지 못함
- 원인 2: 22개 레이어 x 8개 Expert = 176개 라우터 게이트를 동시에 학습해야 함
- 원인 3: Dense FFN을 8등분한 후 라우터 없이 바로 조합하면 출력이 깨짐

## 2. 목표

| 단계 | PPL 목표 | 의미 |
|------|---------|------|
| Phase 1 | < 1000 | 라우터가 올바른 Expert를 선택하기 시작 |
| Phase 2 | < 100 | 최소 coherence — 문장 구조 유지 |
| Phase 3 | < 30 | 원본 TinyLlama 수준 근접 |
| Phase 4 | < 20 | 실용적 MoE — 속도 이점 확인 가능 |

**1차 목표**: PPL < 100 (최소 coherence 달성)

## 3. 훈련 전략

### 3.1 스텝 수 증가: 2000 → 5000

현재 `finetune_router.py`의 `--max-steps` 기본값은 500. 이를 단계적으로 증가:

```bash
# Phase 1: 2000 스텝 (예상 시간: CPU ~4시간, GPU ~30분)
python3 finetune_router.py --model golden-test --epochs 3 --max-steps 2000 --lr 3e-4

# Phase 2: 5000 스텝 (예상 시간: CPU ~10시간, GPU ~1.5시간)
python3 finetune_router.py --model golden-test --epochs 5 --max-steps 5000 --lr 1e-4
```

### 3.2 전체 데이터셋 활용 (23K 샘플)

현재 wikitext-2-raw-v1의 train split 전체를 사용하되, 필터링 후 ~23K 샘플:
- 현재: `len(text.strip()) > 10` 필터 → 약 23K 유효 샘플
- 500 스텝 x 배치 8 = 4000 샘플만 사용 (전체의 ~17%)
- 5000 스텝 x 배치 8 = 40000 → 전체 데이터셋 1.7 에폭 순회

### 3.3 학습률 스케줄링 (코드 수정 필요)

```python
# finetune_router.py에 추가할 스케줄러
from torch.optim.lr_scheduler import CosineAnnealingLR

scheduler = CosineAnnealingLR(optimizer, T_max=max_steps, eta_min=1e-6)
# 매 스텝마다: scheduler.step()
```

워밍업 + 코사인 감쇠 적용 시 수렴 속도 2-3배 개선 기대.

### 3.4 그래디언트 축적 (메모리 제한 시)

```python
# 실효 배치 = batch_size * accumulation_steps = 8 * 4 = 32
accumulation_steps = 4
loss = loss / accumulation_steps
loss.backward()
if steps % accumulation_steps == 0:
    optimizer.step()
    optimizer.zero_grad()
```

## 4. 도메인별 PPL 측정 — Savant Detection

### 4.1 목적

가설 178(실비우스열 결여)에 따르면, 특정 도메인에서의 Expert 교차 활성 패턴이 savant 능력과 대응. 도메인별 PPL을 분리 측정하여 Expert 특화 정도를 정량화.

### 4.2 측정 도메인

| 도메인 | 데이터소스 | Savant 대응 |
|--------|-----------|-------------|
| 수학 | GSM8K, MATH | 수학적 계산 능력 |
| 음악 | MusicNet descriptions | 절대음감, 음악 기억 |
| 시각-공간 | ARC-AGI patterns | 시각 패턴 인식 |
| 언어 | WikiText (현재) | 언어 기본 능력 |
| 달력 | 날짜-요일 QA | 달력 계산 능력 |

### 4.3 구현 (`benchmark.py` 확장)

```python
def measure_domain_ppl(model, tokenizer, domain="math"):
    """도메인별 Perplexity — savant 특화 측정"""
    domain_datasets = {
        "math": ("gsm8k", "main", "question"),
        "language": ("wikitext", "wikitext-2-raw-v1", "text"),
        "code": ("codeparrot/github-code", "default", "code"),
    }
    dataset_name, subset, field = domain_datasets[domain]
    dataset = load_dataset(dataset_name, subset, split="test")
    texts = [t[field] for t in dataset if len(str(t[field])) > 50][:100]
    return measure_perplexity(model, tokenizer, texts)

def savant_profile(model, tokenizer):
    """도메인 PPL 프로파일 → 불균등할수록 savant 특성"""
    ppls = {}
    for domain in ["math", "language", "code"]:
        ppls[domain] = measure_domain_ppl(model, tokenizer, domain)

    # Savant Index = max(PPL) / min(PPL)
    # 높을수록 도메인 특화 (savant-like)
    values = list(ppls.values())
    savant_index = max(values) / min(values) if min(values) > 0 else float('inf')
    ppls['savant_index'] = savant_index
    return ppls
```

**Savant Index 해석**:
- SI ≈ 1.0: 모든 도메인에서 균등 → Dense 모델과 유사
- SI > 3.0: 특정 도메인에 강한 특화 → MoE Expert 분화 시작
- SI > 10.0: 극단적 특화 → savant 패턴 (의도적 유도 가능)

## 5. Expert 교차 활성 구현 — 가설 241

### 5.1 가설 241: Expert Cross-Activation

> "MoE 모델에서 특정 입력이 비정상적으로 많은 Expert를 동시 활성화할 때,
> 이는 뇌의 실비우스열 결여로 인한 과잉 연결과 대응한다."

### 5.2 수학적 정의

정상 모드: 5/8 Expert 활성 (active_ratio = 0.625)
교차 활성 모드: 7/8 또는 8/8 Expert 활성 (특정 입력에 대해)

```
CrossActivation(x) = |{e : w_e(x) > threshold}| / num_experts
```

여기서 `w_e(x)`는 입력 x에 대한 Expert e의 라우터 가중치.

### 5.3 구현 개요

```python
class AdaptiveGoldenMoELayer(GoldenMoELayer):
    """가설 241 — 입력 복잡도에 따라 활성 Expert 수 조절"""

    def __init__(self, *args, cross_threshold=0.8, **kwargs):
        super().__init__(*args, **kwargs)
        self.cross_threshold = cross_threshold

    def forward(self, x):
        scores = self.router.gate(x) / self.router.temperature
        probs = F.softmax(scores, dim=-1)

        # 입력 복잡도 측정: 엔트로피 기반
        entropy = -(probs * (probs + 1e-8).log()).sum(dim=-1)  # (B, S)
        max_entropy = math.log(self.num_experts)
        complexity = entropy / max_entropy  # 0~1 정규화

        # 복잡도 높으면 더 많은 Expert 활성 (교차 활성)
        adaptive_k = torch.where(
            complexity > self.cross_threshold,
            torch.tensor(self.num_experts),      # 전체 활성
            torch.tensor(self.router.num_active)  # 기본 5/8
        )

        # 적응적 top-k 선택
        # ... (토큰별 다른 k로 선택하는 구현 필요)

        return output

    def get_cross_activation_stats(self):
        """교차 활성 빈도 통계"""
        return {
            'cross_activation_rate': self._cross_count / max(self._total_count, 1),
            'avg_active_experts': self._active_sum / max(self._total_count, 1),
        }
```

### 5.4 실험 계획

1. **기본 라우터 학습 완료** (PPL < 100) → Phase 2 이후
2. **교차 활성 라우터 교체** → `AdaptiveGoldenMoELayer` 적용
3. **교차 활성 빈도 측정** → 도메인별로 어떤 입력이 교차 활성을 유발하는지 분석
4. **G 수식 재계산** → 교차 활성 시 I가 동적으로 변하므로 G = D x P / I(x) 로 일반화

### 5.5 기대 결과

- 수학 문제 → 높은 교차 활성 (여러 Expert가 동시에 필요)
- 일반 텍스트 → 낮은 교차 활성 (소수 Expert로 충분)
- Savant 도메인 → 비정상적 교차 활성 패턴 발견 가능

## 6. 실행 로드맵

```
현재 ─────────────────────────────────────── 목표
PPL 4634                                    PPL < 20

Step 1: 라우터 2000 스텝 훈련
  └─ 예상: PPL ~500
  └─ 확인: 로스 커브 수렴 여부

Step 2: 학습률 스케줄러 추가 + 5000 스텝
  └─ 예상: PPL ~50-100
  └─ 확인: 텍스트 생성 coherence 테스트

Step 3: 도메인별 PPL 측정 도구 구현
  └─ benchmark.py에 savant_profile() 추가
  └─ Savant Index 계산

Step 4: Expert 교차 활성 레이어 구현 (가설 241)
  └─ convert.py에 AdaptiveGoldenMoELayer 추가
  └─ 교차 활성 통계 수집

Step 5: 교차 활성 모델 재훈련
  └─ 적응적 라우터 파인튜닝
  └─ G = D × P / I(x) 동적 계산 검증
```

## 7. 파일 참조

| 파일 | 위치 | 역할 |
|------|------|------|
| convert.py | golden-llama/ | Dense → MoE 변환 (BoltzmannRouter, GoldenMoELayer) |
| finetune_router.py | golden-llama/ | 라우터 파인튜닝 (Expert 동결) |
| benchmark.py | golden-llama/ | PPL/속도 벤치마크 |
| golden-test/ | golden-llama/ | 변환된 MoE 모델 (4.1GB) |
| golden-test-finetuned/ | golden-llama/ | 500 스텝 파인튜닝 모델 |
