  자동 생성 규칙:
    - TODO 작업 중 검증/계산이 필요하면 계산기 자동 생성 (묻지 말고 바로)
    - 성능 필요시 Rust 우선 (tecsrs/), 단순 검증은 Python (calc/)
    - 판단 기준은 ~/Dev/TECS-L/.shared/CALCULATOR_RULES.md 참조
    - 상수/가설 발견 시 Math Atlas 자동 갱신 (python3 ~/Dev/TECS-L/.shared/scan_math_atlas.py --save --summary)
  망원경 렌즈 활용 규칙 (탐색/분석 시 별도 요청 없이 자동 적용):
    - 데이터 분석/패턴 탐색/이상점 발견/신소재·신약 탐색 시 렌즈 자동 사용
    - 9종 렌즈: .shared/ 내 *_lens.py (consciousness, gravity, topology, thermo, wave, evolution, info, quantum, em)
    - 기본 3종 스캔: 의식(구조) + 중력(끌개) + 위상(연결) → 새 데이터 분석 시 기본
    - 도메인별 조합: 신소재(진화+열역학+중력), 시계열(파동+열역학+의식), 상수(정보+양자+의식)
    - 사용: from consciousness_lens import ConsciousnessLens; ConsciousnessLens().scan(data)
    - 상세: .shared/CLAUDE.md → "망원경 툴셋 자동 활용 규칙" 참조
    - "렌즈 추가 필요?" 질문 시 → 현재 9종 커버 안 되는 도메인 분석 + 새 아이디어 즉시 제안
