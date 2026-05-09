import streamlit as st
import numpy as np
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(page_title="電力・電圧換算テーブル", layout="wide")

# クレジット表示
st.markdown('<p style="text-align: right; font-size: 14px; color: #666;">開発/制作：緒方</p>', unsafe_allow_html=True)
st.title("📟 dBm ⇄ dBμV ⇄ W 相互換算テーブル")

# --- 計算関数群 ---
def get_dbuv(dbm, z): return dbm + 10 * np.log10(z) + 90
def get_watt(dbm): return 10**((dbm - 30) / 10)
def from_dbuv(dbuv, z): return dbuv - (10 * np.log10(z) + 90)
def from_watt(watt): return 10 * np.log10(watt) + 30 if watt > 0 else -127.0

# --- セッション状態（数値の保持） ---
if 'base_dbm' not in st.session_state:
    st.session_state.base_dbm = 40.0

# --- 条件設定 ---
z = st.radio("インピーダンス Z (Ω)", [50, 75], index=0, horizontal=True)

st.markdown("---")
st.subheader("☁️ 測定値入力（入力後にEnterで確定してください）")
c1, c2, c3 = st.columns(3)

# 1. dBm入力
with c1:
    in_dbm = st.number_input("電力 (dBm)", value=float(st.session_state.base_dbm), step=0.1, format="%.2f", key="input_dbm")
    if in_dbm != round(st.session_state.base_dbm, 2):
        st.session_state.base_dbm = in_dbm
        st.rerun()

# 2. dBμV入力（ここで20.00と入れても動くように修正）
with c2:
    cur_dbuv = get_dbuv(st.session_state.base_dbm, z)
    in_dbuv = st.number_input("電圧 (dBμV)", value=float(cur_dbuv), step=0.1, format="%.2f", key="input_dbuv")
    if abs(in_dbuv - cur_dbuv) > 0.001:
        st.session_state.base_dbm = from_dbuv(in_dbuv, z)
        st.rerun()

# 3. Watt入力
with c3:
    cur_watt = get_watt(st.session_state.base_dbm)
    in_watt = st.number_input("電力 (W)", value=float(cur_watt), step=0.0001, format="%.4f", key="input_watt")
    if abs(in_watt - cur_watt) > 0.00001:
        st.session_state.base_dbm = from_watt(in_watt)
        st.rerun()

# --- テーブル生成 ---
dbm_range = np.around(np.arange(40.0, -127.1, -0.1), 1)
target_val = round(st.session_state.base_dbm, 1)

rows_html = ""
for d in dbm_range:
    dv = get_dbuv(d, z)
    w = get_watt(d)
    w_str = f"{w:.4e}" if w < 0.001 else f"{w:.4f}"
    
    # ターゲット行（青マーカー）の判定
    is_target = d == target_val
    row_id = "id='target-row'" if is_target else ""
    row_style = "style='background-color: #007bff; color: white; font-weight: bold;'" if is_target else ""
    
    rows_html += f"<tr {row_id} {row_style}><td>{d:.1f}</td><td>{dv:.2f}</td><td>{w_str}</td></tr>"

# --- テーブル描画 & 自動スクロールJavaScript ---
table_code = f"""
<div id="scroll-box" style="height: 500px; overflow-y: auto; border: 2px solid #005A9C;">
    <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; text-align: center;">
        <thead style="position: sticky; top: 0; background: #eee; font-size: 18px;">
            <tr><th style="padding:10px; border:1px solid #ddd;">電力 (dBm)</th>
                <th style="padding:10px; border:1px solid #ddd;">電圧 (dBμV)</th>
                <th style="padding:10px; border:1px solid #ddd;">電力 (W)</th></tr>
        </thead>
        <tbody style="font-size: 16px;">
            {rows_html}
        </tbody>
    </table>
</div>

<script>
    function doScroll() {{
        var box = document.getElementById('scroll-box');
        var target = document.getElementById('target-row');
        if (target && box) {{
            // ターゲット行が上から5行目（約200px下）にくるように調整
            box.scrollTop = target.offsetTop - 180;
        }}
    }}
    // 読み込み時と少し遅らせての2段構えで確実に実行
    window.onload = doScroll;
    setTimeout(doScroll, 100);
</script>
"""

components.html(table_code, height=550)

st.info(f"💡 現在の基準値: {st.session_state.base_dbm:.2f} dBm を中心に表示しています")
