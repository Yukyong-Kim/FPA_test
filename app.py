# 논문1 + 논문2 아이디어


import streamlit as st
import pandas as pd
import re

# ---------------------------
# Function Point Category Mapping
# ---------------------------

def classify_fp(row):
    sentence = row['Requirement'].lower()
    fp_type = []

    if any(verb in sentence for verb in ['insert', 'add', 'register']):
        fp_type.append('EI')
    if any(verb in sentence for verb in ['update', 'modify', 'change']):
        fp_type.append('EI')
    if any(verb in sentence for verb in ['delete', 'remove']):
        fp_type.append('EI')
    if any(verb in sentence for verb in ['search', 'find', 'view', 'lookup']):
        fp_type.append('EQ')
    if any(verb in sentence for verb in ['export', 'print', 'report']):
        fp_type.append('EO')
    if any(noun in sentence for noun in ['database', 'table', 'record']):
        fp_type.append('ILF')

    return ', '.join(set(fp_type)) if fp_type else 'Unclassified'

# ---------------------------
# Effort Estimation
# ---------------------------

def estimate_effort(fp_counts, pr=15):
    # Assume default complexity: each FP = 1 UFP
    ufp = sum(fp_counts.values())
    tcf = 0.83  # static example
    afp = ufp * tcf
    man_hour = afp * pr
    return afp, man_hour

# ---------------------------
# Streamlit App
# ---------------------------

st.title("📊 Natural Language FP Analyzer & Effort Estimator")

uploaded_file = st.file_uploader("요구사항 파일 업로드 (CSV 또는 Excel)", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    if 'Requirement' not in df.columns:
        st.error("'Requirement'라는 열이 필요합니다.")
    else:
        st.subheader("📄 요구사항 목록")
        st.write(df)

        df['FP_Type'] = df.apply(classify_fp, axis=1)
        st.subheader("🔍 분류된 기능점수 유형")
        st.write(df[['Requirement', 'FP_Type']])

        # Count each FP type
        fp_summary = df['FP_Type'].str.get_dummies(sep=', ').sum().to_dict()
        st.subheader("📌 기능점수 요약")
        st.json(fp_summary)

        # Effort estimation
        afp, effort = estimate_effort(fp_summary)
        st.success(f"예상 AFP: {afp:.2f}")
        st.success(f"예상 Man-hour: {effort:.1f}시간 (생산성 계수 PR=15 기준)")

        # Downloadable result
        df['Estimated_FP'] = df['FP_Type']
        result_csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 결과 다운로드 (CSV)",
            data=result_csv,
            file_name="fp_analysis_result.csv",
            mime="text/csv"
        )

else:
    st.info("CSV 또는 Excel 파일을 업로드하세요. 열 이름은 'Requirement'여야 합니다.")
