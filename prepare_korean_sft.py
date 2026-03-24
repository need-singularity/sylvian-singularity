#!/usr/bin/env python3
"""
한국어 대화 SFT 데이터 준비 스크립트
ConsciousLM 700M (byte-level, vocab=256) 용

사용법:
    pip install datasets
    python3 prepare_korean_sft.py

출력: data/korean_sft.bin (numpy uint8)
"""

import os
import sys
import json
import numpy as np
from collections import Counter

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------
OUTPUT_DIR = "data"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "korean_sft.bin")
MIN_CONVERSATIONS = 100_000
TARGET_BYTES = 50 * 1024 * 1024  # 50MB

# 특수 토큰 (UTF-8 바이트로 인코딩됨)
USER_TOKEN = "<|user|>"
ASSISTANT_TOKEN = "<|assistant|>"
EOS_TOKEN = "<|eos|>"

# ---------------------------------------------------------------------------
# 데이터셋 소스 정의
# ---------------------------------------------------------------------------
SOURCES = [
    {
        "name": "beomi/KoAlpaca-v1.1a",
        "split": "train",
        "format": "koalpaca",
    },
    {
        "name": "kyujinpy/KOR-OpenOrca-Platypus-v3",
        "split": "train",
        "format": "openorca",
    },
    {
        "name": "squarelike/OpenOrca-gugugo-ko",
        "split": "train",
        "format": "gugugo",
    },
    {
        "name": "nlpai-lab/kullm-v2",
        "split": "train",
        "format": "openorca",
    },
]


def format_ko_chatgpt(example):
    """heegyu/ko-chatgpt-data 형식 -> 대화 문자열."""
    # 필드: instruction, output (또는 input/output)
    user_msg = example.get("instruction", "") or example.get("input", "")
    if not user_msg:
        return None
    assistant_msg = example.get("output", "")
    if not assistant_msg:
        return None

    # input 필드가 별도로 있으면 instruction 뒤에 붙임
    extra_input = example.get("input", "")
    if extra_input and extra_input != user_msg:
        user_msg = f"{user_msg}\n{extra_input}"

    return f"{USER_TOKEN} {user_msg.strip()} {ASSISTANT_TOKEN} {assistant_msg.strip()} {EOS_TOKEN}"


def format_openorca(example):
    """kyujinpy/KOR-OpenOrca-Platypus-v3 형식."""
    # 필드: instruction, input, output
    user_msg = example.get("instruction", "")
    extra = example.get("input", "")
    if extra:
        user_msg = f"{user_msg}\n{extra}" if user_msg else extra
    if not user_msg:
        return None
    assistant_msg = example.get("output", "")
    if not assistant_msg:
        return None
    return f"{USER_TOKEN} {user_msg.strip()} {ASSISTANT_TOKEN} {assistant_msg.strip()} {EOS_TOKEN}"


def format_koalpaca(example):
    """beomi/KoAlpaca-v1.1a 형식."""
    # 필드: instruction, output
    user_msg = example.get("instruction", "")
    if not user_msg:
        return None
    assistant_msg = example.get("output", "")
    if not assistant_msg:
        return None
    return f"{USER_TOKEN} {user_msg.strip()} {ASSISTANT_TOKEN} {assistant_msg.strip()} {EOS_TOKEN}"


def format_gugugo(example):
    """squarelike/OpenOrca-gugugo-ko 형식."""
    # 필드: system_prompt, question, response
    user_msg = example.get("question", "")
    if not user_msg:
        return None
    assistant_msg = example.get("response", "")
    if not assistant_msg:
        return None
    return f"{USER_TOKEN} {user_msg.strip()} {ASSISTANT_TOKEN} {assistant_msg.strip()} {EOS_TOKEN}"


FORMATTERS = {
    "ko_chatgpt": format_ko_chatgpt,
    "openorca": format_openorca,
    "koalpaca": format_koalpaca,
    "gugugo": format_gugugo,
}


def load_and_format_source(source_info):
    """단일 소스에서 데이터를 로드하고 포맷팅."""
    from datasets import load_dataset

    name = source_info["name"]
    split = source_info["split"]
    fmt = source_info["format"]
    formatter = FORMATTERS[fmt]

    print(f"\n{'='*60}")
    print(f"  Loading: {name} (split={split})")
    print(f"{'='*60}")

    try:
        ds = load_dataset(name, split=split)
    except Exception as e:
        print(f"  [WARN] Failed to load {name}: {e}")
        print(f"  Skipping this source.")
        return []

    print(f"  Raw examples: {len(ds):,}")

    # 사용 가능한 필드 확인
    if len(ds) > 0:
        print(f"  Fields: {list(ds[0].keys())}")

    conversations = []
    skipped = 0
    for example in ds:
        text = formatter(example)
        if text is None:
            skipped += 1
            continue
        # 최소 길이 필터 (너무 짧은 대화 제거)
        if len(text.encode("utf-8")) < 20:
            skipped += 1
            continue
        conversations.append(text)

    print(f"  Formatted: {len(conversations):,} conversations")
    print(f"  Skipped: {skipped:,}")

    return conversations


def compute_stats(conversations, byte_data):
    """데이터 통계 계산 및 출력."""
    total_bytes = len(byte_data)
    total_convs = len(conversations)

    # 바이트 길이 분포
    lengths = [len(c.encode("utf-8")) for c in conversations]
    lengths_arr = np.array(lengths)

    print(f"\n{'='*60}")
    print(f"  데이터 통계")
    print(f"{'='*60}")
    print(f"  총 대화 수:     {total_convs:>12,}")
    print(f"  총 바이트:      {total_bytes:>12,} ({total_bytes/1024/1024:.1f} MB)")
    print(f"  평균 길이:      {lengths_arr.mean():>12.0f} bytes/conv")
    print(f"  중앙값 길이:    {np.median(lengths_arr):>12.0f} bytes/conv")
    print(f"  최소 길이:      {lengths_arr.min():>12,} bytes")
    print(f"  최대 길이:      {lengths_arr.max():>12,} bytes")
    print(f"  표준편차:       {lengths_arr.std():>12.0f} bytes")

    # 길이 분포 히스토그램 (ASCII)
    print(f"\n  길이 분포 (bytes):")
    bins = [0, 100, 200, 500, 1000, 2000, 5000, 10000, 50000, float("inf")]
    labels = ["<100", "100-200", "200-500", "500-1K", "1K-2K", "2K-5K", "5K-10K", "10K-50K", "50K+"]
    max_bar = 40
    counts = []
    for i in range(len(bins) - 1):
        c = int(np.sum((lengths_arr >= bins[i]) & (lengths_arr < bins[i+1])))
        counts.append(c)
    max_count = max(counts) if counts else 1
    for label, count in zip(labels, counts):
        bar_len = int(count / max_count * max_bar)
        bar = "#" * bar_len
        pct = count / total_convs * 100
        print(f"    {label:>8s} | {bar:<{max_bar}s} {count:>8,} ({pct:5.1f}%)")

    # 바이트 값 분포 (한글은 0xEA-0xED 범위)
    byte_counts = Counter(byte_data)
    korean_bytes = sum(byte_counts.get(b, 0) for b in range(0xEA, 0xEE))
    ascii_bytes = sum(byte_counts.get(b, 0) for b in range(0x20, 0x7F))
    print(f"\n  바이트 분포:")
    print(f"    한글 범위 (0xEA-0xED): {korean_bytes:>12,} ({korean_bytes/total_bytes*100:.1f}%)")
    print(f"    ASCII 범위 (0x20-0x7E): {ascii_bytes:>12,} ({ascii_bytes/total_bytes*100:.1f}%)")
    print(f"    기타:                   {total_bytes-korean_bytes-ascii_bytes:>12,}")

    # 목표 달성 여부
    print(f"\n  목표 달성:")
    conv_ok = total_convs >= MIN_CONVERSATIONS
    byte_ok = total_bytes >= TARGET_BYTES
    print(f"    대화 수 >= {MIN_CONVERSATIONS:,}: {'OK' if conv_ok else 'FAIL'} ({total_convs:,})")
    print(f"    바이트 >= {TARGET_BYTES/1024/1024:.0f}MB: {'OK' if byte_ok else 'FAIL'} ({total_bytes/1024/1024:.1f}MB)")

    if not conv_ok:
        print(f"\n  [WARN] 대화 수 부족. 데이터 반복으로 보충합니다.")
    if not byte_ok:
        print(f"\n  [WARN] 바이트 수 부족. 데이터 반복으로 보충합니다.")


def preview_samples(conversations, n=3):
    """샘플 미리보기."""
    print(f"\n{'='*60}")
    print(f"  샘플 미리보기 ({n}개)")
    print(f"{'='*60}")
    import random
    random.seed(42)
    indices = random.sample(range(len(conversations)), min(n, len(conversations)))
    for i, idx in enumerate(indices):
        text = conversations[idx]
        # 너무 길면 잘라서 표시
        display = text[:500] + "..." if len(text) > 500 else text
        byte_repr = text.encode("utf-8")[:80]
        print(f"\n  --- Sample {i+1} (idx={idx}, {len(text.encode('utf-8')):,} bytes) ---")
        print(f"  Text: {display}")
        print(f"  Bytes[:80]: {list(byte_repr)}")


def main():
    print("=" * 60)
    print("  한국어 대화 SFT 데이터 준비")
    print(f"  ConsciousLM 700M (byte-level, vocab=256)")
    print(f"  출력: {OUTPUT_PATH}")
    print("=" * 60)

    # datasets 라이브러리 확인
    try:
        from datasets import load_dataset
    except ImportError:
        print("\n  [ERROR] 'datasets' 패키지가 필요합니다.")
        print("  설치: pip install datasets")
        sys.exit(1)

    # 모든 소스에서 데이터 수집
    all_conversations = []
    source_stats = []

    for source in SOURCES:
        convs = load_and_format_source(source)
        source_stats.append((source["name"], len(convs)))
        all_conversations.extend(convs)

    print(f"\n{'='*60}")
    print(f"  소스별 수집 결과")
    print(f"{'='*60}")
    for name, count in source_stats:
        print(f"    {name:<45s} {count:>8,}")
    print(f"    {'─'*45} {'─'*8}")
    print(f"    {'TOTAL':<45s} {len(all_conversations):>8,}")

    if len(all_conversations) == 0:
        print("\n  [ERROR] 수집된 대화가 없습니다. 네트워크 연결을 확인하세요.")
        sys.exit(1)

    # 셔플
    import random
    random.seed(42)
    random.shuffle(all_conversations)

    # 대화 수가 부족하면 반복으로 보충
    if len(all_conversations) < MIN_CONVERSATIONS:
        print(f"\n  대화 수 보충: {len(all_conversations):,} -> {MIN_CONVERSATIONS:,}")
        repeats = (MIN_CONVERSATIONS // len(all_conversations)) + 1
        all_conversations = (all_conversations * repeats)[:MIN_CONVERSATIONS]
        random.shuffle(all_conversations)

    # UTF-8 바이트로 변환
    print(f"\n  UTF-8 바이트 변환 중...")
    # 대화 사이에 줄바꿈 2개로 구분 (바이트 레벨에서 구분자 역할)
    separator = b"\n\n"
    byte_parts = []
    for conv in all_conversations:
        byte_parts.append(conv.encode("utf-8"))
    combined = separator.join(byte_parts)

    # 바이트 수가 부족하면 반복
    if len(combined) < TARGET_BYTES:
        print(f"  바이트 보충: {len(combined):,} -> {TARGET_BYTES:,}")
        repeats = (TARGET_BYTES // len(combined)) + 1
        combined = (separator.join(byte_parts) + separator) * repeats
        combined = combined[:TARGET_BYTES]

    # numpy uint8로 변환 및 저장
    byte_data = np.frombuffer(combined, dtype=np.uint8).copy()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    byte_data.tofile(OUTPUT_PATH)
    print(f"\n  저장 완료: {OUTPUT_PATH}")
    print(f"  파일 크기: {os.path.getsize(OUTPUT_PATH):,} bytes ({os.path.getsize(OUTPUT_PATH)/1024/1024:.1f} MB)")

    # 통계 출력
    compute_stats(all_conversations, byte_data)

    # 샘플 미리보기
    preview_samples(all_conversations)

    # 검증: 저장된 파일 다시 읽어서 확인
    print(f"\n{'='*60}")
    print(f"  검증: 저장된 파일 로드 테스트")
    print(f"{'='*60}")
    loaded = np.fromfile(OUTPUT_PATH, dtype=np.uint8)
    print(f"  Loaded shape: {loaded.shape}")
    print(f"  dtype: {loaded.dtype}")
    print(f"  Range: [{loaded.min()}, {loaded.max()}]")
    # 첫 200바이트를 디코딩해서 확인
    sample_bytes = bytes(loaded[:200])
    try:
        decoded = sample_bytes.decode("utf-8", errors="replace")
        print(f"  First 200 bytes decoded: {decoded[:200]}")
    except Exception as e:
        print(f"  Decode error: {e}")

    print(f"\n  완료!")
    print(f"  사용법: data = np.fromfile('{OUTPUT_PATH}', dtype=np.uint8)")
    print(f"         data = torch.tensor(data, dtype=torch.long)")


if __name__ == "__main__":
    main()
