import streamlit as st
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(page_title="電力・電圧換算テーブル", layout="wide")

st.markdown('<p style="text-align: right; font-size: 14px; color: #666;">開発/制作：緒方</p>', unsafe_allow_html=True)
st.title("📟 dBm ⇄ dBμV ⇄ W 相互換算テーブル")

# --- 計算関数 ---
def get_dbuv(dbm, z): return dbm + 10 * np.log10(z) + 90
def get_watt(dbm): return 10**((dbm - 30) / 10)
def from_dbuv(dbuv, z): return dbuv - (10 * np.log10(z) + 90)
def from_watt(watt): return 10 * np.log10(watt) + 30 if watt > 0 else -127.0

# --- セッション状態 ---
if 'base_dbm' not in st.session_state:
    st.session_state.base_dbm = 40.0

# --- コールバック関数 ---
def update_from_dbm(): st.session_state.base_dbm = st.session_state.kb_dbm
def update_from_dbuv(): st.session_state.base_dbm = from_dbuv(st.session_state.kb_dbuv, st.session_state.z_val)
def update_from_watt(): st.session_state.base_dbm = from_watt(st.session_state.kb_watt)

# --- 入力エリア ---
z = st.radio("インピーダンス Z (Ω)", [50, 75], index=0, horizontal=True, key="z_val")

st.markdown("---")
st.subheader("☁️ 測定値入力（Enterで確定）")
c1, c2, c3 = st.columns(3)

cur_dbuv = get_dbuv(st.session_state.base_dbm, z)
cur_watt = get_watt(st.session_state.base_dbm)

with c1:
    st.number_input("電力 (dBm)", value=float(st.session_state.base_dbm), step=0.1, format="%.2f", key="kb_dbm", on_change=update_from_dbm)
with c2:
    st.number_input("電圧 (dBμV)", value=float(cur_dbuv), step=0.1, format="%.2f", key="kb_dbuv", on_change=update_from_dbuv)
with c3:
    st.number_input("電力 (W)", value=float(cur_watt), step=0.0001, format="%.4f", key="kb_watt", on_change=update_from_watt)

# --- テーブルHTML生成 ---
dbm_range = np.around(np.arange(40.0, -127.1, -0.1), 1)
target_val = round(st.session_state.base_dbm, 1)

rows_html = ""
for d in dbm_range:
    dv = get_dbuv(d, z)
    w = get_watt(d)
    w_display = f"{w:.4f}" if w >= 0.0010 else "----"
    
    is_target = d == target_val
    row_id = "id='target-row'" if is_target else ""
    
    # スタイルの直接指定（確実な色付けのため）
    if is_target:
        row_style = "background-color: #007bff; color: white; font-weight: bold;"
        c1_style = c2_style = c3_style = ""
    else:
        row_style = ""
        c1_style = "background-color: #fdf2f2; color: #333;" # 赤系
        c2_style = "background-color: #f2fdf2; color: #333;" # 緑系
        c3_style = "background-color: #f2f2fd; color: #333;" # 青系

    rows_html += f"""
        <tr {row_id} style="{row_style}">
            <td style="width:33%; border:1px solid #ddd; padding:10px; {c1_style}">{d:.1f}</td>
            <td style="width:34%; border:1px solid #ddd; padding:10px; {c2_style}">{dv:.2f}</td>
            <td style="width:33%; border:1px solid #ddd; padding:10px; {c3_style}">{w_display}</td>
        </tr>
    """

# --- 表示 & 自動スクロールJS ---
table_code = f"""
<div id="scroll-box" style="height: 500px; overflow-y: auto; border: 2px solid #444; border-radius: 8px;">
    <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; text-align: center; table-layout: fixed;">
        <thead>
            <tr style="position: sticky; top: 0; background: #444; color: white; z-index: 10;">
                <th style="padding:12px; border:1px solid #555; width:33%;">電力 (dBm)</th>
                <th style="padding:12px; border:1px solid #555; width:34%;">電圧 (dBμV)</th>
                <th style="padding:12px; border:1px solid #555; width:33%;">電力 (W)</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
</div>
<script>
    function doScroll() {{
        var box = document.getElementById('scroll-box');
        var target = document.getElementById('target-row');
        if (target && box) {{
            box.scrollTop = target.offsetTop - 180; 
        }}
    }}
    window.onload = doScroll;
    setTimeout(doScroll, 150); 
</script>
"""

components.html(table_code, height=560)
st.info(f"💡 現在の基準: {st.session_state.base_dbm:.2f} dBm / 電力(W) 0.0010未満は「----」")
