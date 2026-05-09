import streamlit as st
import numpy as np
import pandas as pd

# 日本標準時(JST)で計算するなどの設定は維持
st.set_page_config(page_title="電力・電圧換算ツール", layout="wide")

# カスタムCSS：手書き指示の「青マーカー」を再現
st.markdown("""
<style>
    .credit { text-align: right; font-size: 14px; color: #666; }
    .highlight {
        background-color: #d1e7ff; /* 薄い青 */
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="credit">開発/制作：緒方</p>', unsafe_allow_html=True)
st.title("📟 dBm ⇄ dBμV ⇄ W 相互換算")

# --- 設定エリア ---
col_cfg1, col_cfg2 = st.columns([1, 2])

with col_cfg1:
    st.subheader("💡 インピーダンスを選択")
    z = st.radio("Z (Ω)", [50, 75], index=0, horizontal=True)

with col_cfg2:
    st.subheader("☁️ 測定値入力")
    c1, c2, c3 = st.columns(3)
    in_dbm = c1.number_input("測定値 (dBm)", value=40.0, step=0.1, format="%.2f")
    # 入力値を基準に表を構成するため、ここではdBmをメイン入力として扱います

# --- 計算ロジック ---
def calc_values(dbm, z):
    watt = 10**((dbm - 30) / 10)
    # dBμV = dBm + 10*log10(Z) + 90
    dbuv = dbm + 10 * np.log10(z) + 90
    return dbuv, watt

# 40.0dBmから-127.0dBmまで0.1ステップで生成
dbm_range = np.arange(40.0, -127.1, -0.1)
data = []

for d in dbm_range:
    dv, w = calc_values(d, z)
    data.append({
        "電力 (dBm)": round(d, 2),
        "電圧 (dBμV)": round(dv, 2),
        "電力 (W)": f"{w:.4e}" if w < 0.01 else round(w, 4)
    })

df = pd.DataFrame(data)

# --- 表示とハイライト処理 ---
st.markdown("---")
st.write(f"インピーダンス **{z}Ω** で計算中。入力値 **{in_dbm} dBm** の行を青く表示します。")

# 入力値に一番近い行を見つける
target_val = round(in_dbm, 1)

def highlight_row(row):
    # 電力(dBm)が入力値と一致する場合、背景を青くする
    if round(row["電力 (dBm)"], 1) == target_val:
        return ['background-color: #007bff; color: white; font-weight: bold'] * len(row)
    return [''] * len(row)

# スタイル適用
styled_df = df.style.apply(highlight_row, axis=1)

# 表示（データ量が多いので高さを固定）
st.dataframe(styled_df, use_container_width=True, height=600)

st.info("💡 40dBm から -127dBm まで 0.1ステップで計算しています。スクロールして確認してください。")
