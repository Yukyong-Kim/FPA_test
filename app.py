import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="AI 기반 소프트웨어 노력 추정기", layout="centered")

st.title("파일 기반 FPA + Man-hour 추정기")
st.markdown("CSV 또는 Excel 파일로 기능 요청사항을 업로드하면, FPA 분석을 통해 개발 노력을 예측합니다.")

# ---------- 기본 가중치 테이블 ---------- #
fpa_weights = {
    "EI": 3,
    "EO": 4,
    "EQ": 3,
    "ILF": 7,
    "EIF": 5
}

# ---------- 키워드 기반 FPA 자동 태깅 ---------- #
def extract_fpa_elements(text):
    EI_keywords = ["입력", "등록", "작성", "요청"]
    EO_keywords = ["보고서", "출력", "결과", "다운로드"]
    EQ_keywords = ["조회", "검색", "확인"]
    ILF_keywords = ["DB", "데이터베이스", "내부 저장"]
    EIF_keywords = ["외부 시스템", "API", "외부 연동"]

    tags = {"EI": 0, "EO": 0, "EQ": 0, "ILF": 0, "EIF": 0}

    for line in text.split("\n"):
        for word in EI_keywords:
            if word in line:
                tags["EI"] += 1
                break
        for word in EO_keywords:
            if word in line:
                tags["EO"] += 1
                break
        for word in EQ_keywords:
            if word in line:
                tags["EQ"] += 1
                break
        for word in ILF_keywords:
            if word in line:
                tags["ILF"] += 1
                break
        for word in EIF_keywords:
            if word in line:
                tags["EIF"] += 1
                break

    return tags

# ---------- TCF 자동 점수 ---------- #
def estimate_tcf(text):
    complexity_factors = {
        "실시간": 4,
        "고성능": 4,
        "다중 사용자": 3,
        "온라인 입력": 3,
        "보안": 3,
        "재사용": 2,
        "설치": 2,
        "운영": 2
    }
    score = 0
    for keyword, weight in complexity_factors.items():
        if keyword in text:
            score += weight
    return 0.65 + 0.01 * score

# ---------- Effort 계산 ---------- #
def calculate_effort(fpa_tags, tcf, productivity_rate=15):
    ufp = sum(fpa_tags[element] * fpa_weights[element] for element in fpa_tags)
    afp = round(ufp * tcf, 2)
    effort = round(afp * productivity_rate, 2)
    return ufp, afp, effort

# ---------- UI 입력 ---------- #
st.subheader("📥 기능 요청사항 파일 업로드")
file = st.file_uploader("기능 요청사항이 포함된 CSV 또는 Excel 파일을 업로드하세요 (컬럼명: '요구사항')", type=["csv", "xls", "xlsx"])

if file:
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    if "요구사항" not in df.columns:
        st.error("❌ '요구사항'이라는 컬럼명이 포함되어야 합니다.")
    else:
        full_text = "\n".join(df["요구사항"].dropna().astype(str))
        fpa_tags = extract_fpa_elements(full_text)
        tcf = estimate_tcf(full_text)
        ufp, afp, effort = calculate_effort(fpa_tags, tcf)

        st.success("✅ 예측 완료!")
        st.markdown("### 🧾 결과 요약")
        st.write(f"**기능점수(UFP)**: {ufp}")
        st.write(f"**기술 복잡도 계수(TCF)**: {round(tcf, 2)}")
        st.write(f"**조정된 기능점수(AFP)**: {afp}")
        st.write(f"**예상 개발 노력**: {effort} 시간 (man-hours)")

        st.markdown("---")
        st.markdown("### 🔍 기능 요소 감지 결과")
        st.json(fpa_tags)
else:
    st.info("⬆️ CSV 또는 Excel 파일을 업로드하면 결과가 여기에 표시됩니다.")
