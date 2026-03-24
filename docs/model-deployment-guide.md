# 700M x 3 모델 인터넷 배포 가이드

## 개요

700M 파라미터 모델 3개를 인터넷망에 서빙하기 위한 인프라 가이드.

## VRAM 요구량

| | FP16 | INT8 | INT4 |
|---|---|---|---|
| 모델 1개 | ~1.4GB | ~0.7GB | ~0.35GB |
| **3개 합계** | **~4.2GB** | **~2.1GB** | **~1.05GB** |
| + KV cache/오버헤드 | ~6-8GB | ~4-5GB | ~3GB |

GPU 1대 (16GB+ VRAM)이면 충분.

## 서빙 아키텍처

```
1대 GPU 서버
├── vLLM (3개 모델 동시 로드)
│   ├── model_A (port 8001)
│   ├── model_B (port 8002)
│   └── model_C (port 8003)
├── Nginx (리버스 프록시 + SSL + 로드밸런싱)
├── FastAPI 게이트웨이 (라우팅 + API 키 인증)
└── Cloudflare (도메인 + DDoS 방어)
```

## 필요 구성요소

### 하드웨어
- GPU 서버 1대 (16GB+ VRAM)

### 소프트웨어
- Docker + NVIDIA Container Toolkit
- vLLM 또는 TGI (서빙 프레임워크)
- Nginx + Let's Encrypt (SSL)
- 도메인 1개 (~$10/년)

### 네트워크/보안
- 도메인 + SSL (Let's Encrypt 무료)
- 리버스 프록시: Nginx / Caddy
- API 키 인증 + rate limiting
- 방화벽 (포트 최소 개방)
- DDoS 방어: Cloudflare

## 서빙 프레임워크 비교

| 프레임워크 | 특징 |
|---|---|
| **vLLM** | LLM 특화, PagedAttention, 처리량 최고 |
| **TGI** (HuggingFace) | HF 생태계 통합, 간편 |
| **Triton** (NVIDIA) | 범용, 멀티모델, 배치 최적화 |
| **Ollama** | 로컬/소규모, 간편 설치 |
| **llama.cpp server** | CPU/경량 GPU, GGUF 포맷 |

## 최적화

- **양자화**: GPTQ, AWQ, GGUF (4bit/8bit) → VRAM 절감
- **KV cache 최적화**: PagedAttention (vLLM 자동)
- **배치 처리**: continuous batching
- **스트리밍**: SSE (Server-Sent Events)

## 플랫폼 추천

### 가성비 순위

| 순위 | 서비스 | 월 비용 | 특징 |
|---|---|---|---|
| 1 | **RunPod Serverless** | **$5-30** | 호출당 과금, 트래픽 없으면 $0 |
| 2 | **Modal** | **$10-40** | 콜드스타트 빠름, Python 네이티브 |
| 3 | **Replicate** | **$20-50** | 배포 제일 쉬움, `cog push` 한 줄 |
| 4 | **RunPod Pod** | ~$160 | 24시간 상시, 트래픽 많을 때 |
| 5 | **AWS SageMaker** | ~$200+ | 기업용 |
| 6 | **GCP Vertex AI** | ~$200+ | 기업용 |

### 트래픽별 추천

| 트래픽 | 추천 | 비용 |
|---|---|---|
| 적음 (하루 ~1000건 이하) | RunPod Serverless / Modal | $5-30/월 |
| 중간 (하루 ~1만건) | RunPod Pod (RTX 3090) | ~$160/월 |
| 많음 (하루 ~10만건+) | 전용 서버 (Hetzner, OVH) | $100-200/월 |

### GPU 추천

| GPU | 월 비용 | 비고 |
|---|---|---|
| **RTX 3090 24GB** | ~$160/월 (클라우드) | 3개 여유, 가성비 최고 |
| **RTX 4090 24GB** | ~$300/월 | 처리량 2배 |
| **T4 16GB** | ~$80/월 (AWS/GCP) | FP16 3개 가능, 느림 |
| **A10G 24GB** | ~$120/월 (AWS) | 안정적 |
| 본인 **RTX 5070** | $0 | 집에서 서빙 가능 |

### 비용 요약

| 항목 | 셀프호스팅 (5070) | 클라우드 (RTX 3090) |
|---|---|---|
| 서버 | 전기세 ~$30 | ~$160 |
| 도메인 | ~$1 | ~$1 |
| Cloudflare | 무료 | 무료 |
| **합계** | **~$31/월** | **~$161/월** |

## 빠른 시작

### Replicate (5분 배포)

```bash
cog push r8.im/username/model-a
cog push r8.im/username/model-b
cog push r8.im/username/model-c
```

### RunPod Serverless

```
handler.py 작성 → Docker 빌드 → Endpoint 생성 → API 호출
```

### 셀프호스팅 (RTX 5070)

```bash
# Cloudflare Tunnel로 고정 IP 불필요
cloudflared tunnel --url http://localhost:8000
```
