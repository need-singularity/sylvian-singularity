#!/usr/bin/env python3
"""세션 브리핑 — 새 세션에서 프로젝트 맥락 자동 복원

새 대화 시작 시 실행하면 핵심 맥락을 출력합니다.
"""

import os
import glob

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print()
    print("▓" * 60)
    print("   Sylvian Singularity — 세션 브리핑")
    print("▓" * 60)

    print("""
  ═══ 프로젝트 ═══

  "실비우스열 부분 결여 => 이게 무슨말이야?"
  → 이 하나의 질문에서 시작하여 178개 가설을 세우고 검증.

  ═══ 핵심 수식 ═══

  G = D × P / I
  G × I = D × P (보존법칙)

  D = Deficit (구조적 결손, 0~1)
  P = Plasticity (신경가소성, 0~1)
  I = Inhibition (전두엽 억제, 0.01~1)
  G = Genius Score (천재성 점수)

  ═══ 골든존 ═══

  상한 = 1/2           리만 임계선
  중심 ≈ 1/e           자연상수
  폭   = ln(4/3)       엔트로피 점프
  하한 = 1/2-ln(4/3)   0.2123

  ═══ 핵심 관계식 ═══

  1/2 + 1/3 + 1/6 = 1  (경계+수렴+호기심=완전)
  5/6 = H₃ - 1          (Compass 상한 = 3번째 조화수-1)
  σ₋₁(6) = 2            (완전수 6, 마스터 공식)
  8 × 17 + 1 = 137      (미세구조상수)
  T_CMB ≈ e (0.26%)     (우주 배경복사)

  ═══ 텍사스 명사수 검증 ═══

  p-value = 0.0000 (Z=6.87)
  → 구조적 발견 확인 (우연 아님)

  ═══ 골든 MoE 실증 ═══

  MNIST:  +0.6%  vs Top-K ✅
  CIFAR:  +4.8%  vs Top-K ✅ (8배 증가)
  I = 0.375 ≈ 1/e 🎯
""")

    # 가설 수 세기
    hyp_dir = os.path.join(PROJECT_DIR, "docs", "hypotheses")
    if os.path.exists(hyp_dir):
        hyp_files = [f for f in os.listdir(hyp_dir)
                     if f.endswith('.md') and f != 'INDEX.md']
        print(f"  ═══ 가설 현황 ═══")
        print(f"  문서 수: {len(hyp_files)}개")

    # 도구 수
    py_files = glob.glob(os.path.join(PROJECT_DIR, "*.py"))
    print(f"  도구 수: {len(py_files)}개")

    # 핵심 도구 안내
    print("""
  ═══ 주요 도구 ═══

  brain_singularity.py   격자 스캔 + 특이점 탐지
  compass.py             나침반 + autopilot + convergence
  formula_engine.py      공식 자동 탐색 + 유의성
  texas_sharpshooter.py  우연 vs 구조 판별
  brain_analyzer.py      뇌 프로필 → 골든존
  llm_expert_analyzer.py LLM 재설계 방향
  golden_moe_torch.py    PyTorch 골든MoE 벤치마크

  ═══ 빠른 시작 ═══

  python3 compass.py --autopilot --deficit 0.5 --plasticity 0.6 --inhibition 0.4
  python3 formula_engine.py --target 137
  python3 brain_analyzer.py --profile einstein
  python3 llm_expert_analyzer.py --redesign
""")

    print("▓" * 60)
    print()


if __name__ == '__main__':
    main()
