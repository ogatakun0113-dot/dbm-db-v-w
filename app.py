import streamlit as st
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(page_title="電力・電圧換算テーブル", layout="wide")

st.markdown('<p style="text-align: right; font-size: 14px; color: #666;">開発/制作：緒方</p>', unsafe_allow_html=True)
st.title("📟 dBm ⇄ dBμV ⇄ W 相互換算テーブル")

# --- 計算ロジック ---
def get_dbuv(dbm, z): return dbm + 10 * np.log10(z) + 90
def get_watt(dbm): return 10**((dbm - 30) / 10)
def from_dbuv(dbuv, z): return dbuv - (10 * np.log10(z) + 90)
def from_watt(watt): return 10 * np.log10(watt) + 30 if watt > 0 else -250.0

# --- セッション管理 ---
if 'base_dbm' not in st.session_state:
    st.session_state.base_dbm = 40.0

# --- 入力コールバック ---
def update_dbm(): st.session_state.base_dbm = st.session_state.kb_dbm
def update_dbuv(): st.session_state.base_dbm = from_dbuv(st.session_state.kb_dbuv, st.session_state.z_val)
def update_watt(): st.session_state.base_dbm = from_watt(st.session_state.kb_watt)

# --- 操作エリア ---
z = st.radio("インピーダンス Z (Ω)", [50, 75], index=0, horizontal=True, key="z_val")

st.markdown("---")
st.subheader("☁️ 測定値入力（Enterで確定）")

# 【重要】入力枠の「中身」に色を付けるためのCSS
st.markdown("""
<style>
    /* 1つ目の枠 (dBm): 赤 */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) input {
        background-color: #fdf2f2 !important;
        color: #b91c1c !important;
        border: 2px solid #fecaca !important;
    }
    /* 2つ目の枠 (dBμV): 緑 */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) input {
        background-color: #f2fdf2 !important;
        color: #15803d !important;
        border: 2px solid #bbf7d0 !important;
    }
    /* 3つ目の枠 (Watt): 青 */
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) input {
        background-color: #f2f2fd !important;
        color: #1d4ed8 !important;
        border: 2px solid #bfdbfe !important;
    }
    /* ラベルの文字も少し太く */
    label p { font-weight: bold; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

cur_dbuv = get_dbuv(st.session_state.base_dbm, z)
cur_watt = get_watt(st.session_state.base_dbm)

with c1:
    st.number_input("電力 (dBm)", value=float(st.session_state.base_dbm), step=0.1, format="%.2f", key="kb_dbm", on_change=update_dbm)
with c2:
    st.number_input("電圧 (dBμV)", value=float(cur_dbuv), step=0.1, format="%.2f", key="kb_dbuv", on_change=update_dbuv)
with c3:
    st.number_input("電力 (W)", value=float(cur_watt), step=0.0001, format="%.4f", key="kb_watt", on_change=update_watt)

# --- テーブル生成 ---
dbm_range = np.around(np.arange(40.0, -250.1, -0.1), 1)
target_val = round(st.session_state.base_dbm, 1)

rows_html = ""
for d in dbm_range:
    dv = get_dbuv(d, z)
    w = get_watt(d)
    w_display = f"{w:.4f}" if w >= 0.0010 else "----"
    dv_display = f"{dv:.2f}" if dv >= -107.00 else "----"
    
    is_target = d == target_val
    row_id = "id='target-row'" if is_target else ""
    
    if is_target:
        row_style = "background-color: #007bff; color: white; font-weight: bold;"
        c1_s = c2_s = c3_s = ""
    else:
        row_style = ""
        c1_s = "background-color: #fdf2f2;"
        c2_s = "background-color: #f2fdf2;"
        c3_s = "background-color: #f2f2fd;"

    rows_html += f"""
        <tr {row_id} style="{row_style}">
            <td style="width:33%; border:1px solid #ddd; padding:12px; {c1_s}">{d:.1f}</td>
            <td style="width:34%; border:1px solid #ddd; padding:12px; {c2_s}">{dv_display}</td>
            <td style="width:33%; border:1px solid #ddd; padding:12px; {c3_s}">{w_display}</td>
        </tr>
    """
    if w < 0.0010 and dv < -107.00 and d < target_val: break

# --- 表示 & JS ---
table_code = f"""
<div id="scroll-box" style="height: 520px; overflow-y: auto; border: 2px solid #444; border-radius: 8px;">
    <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; text-align: center; table-layout: fixed;">
        <thead>
            <tr style="position: sticky; top: 0; background: #444; color: white; z-index: 10;">
                <th style="padding:15px; border:1px solid #555;">電力 (dBm)</th>
                <th style="padding:15px; border:1px solid #555;">電圧 (dBμV)</th>
                <th style="padding:15px; border:1px solid #555;">電力 (W)</th>
            </tr>
        </thead>
        <tbody style="font-size: 18px;">{rows_html}</tbody>
    </table>
</div>
<script>
    function jump() {{
        var b = document.getElementById('scroll-box');
        var r = document.getElementById('target-row');
        if (r && b) {{ b.scrollTop = r.offsetTop - 150; }}
    }}
    window.onload = jump;
    setTimeout(jump, 150);
</script>
"""

components.html(table_code, height=580)
