import streamlit as st
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(page_title="電力・電圧換算テーブル", layout="wide")

# --- メニュー戻るアイコン & 制作クレジット ---
header_cols = st.columns([1, 5, 2])
with header_cols[0]:
    # 戻るアイコンボタン
    st.link_button("🔙 メニューへ戻る", "https://7fjndw39dicdzckugyepb2.streamlit.app/", use_container_width=True)

with header_cols[2]:
    st.markdown('<p style="text-align: right; font-size: 14px; color: #666; margin-top: 10px;">開発/制作：緒方</p>', unsafe_allow_html=True)

st.title("📟 dBm ⇄ dBμV ⇄ W 相互換算テーブル")

# --- 計算ロジック ---
def get_dbuv(dbm, z): return dbm + 10 * np.log10(z) + 90
def get_watt(dbm): return 10**((dbm - 30) / 10)
def from_dbuv(dbuv, z): return dbuv - (10 * np.log10(z) + 90)
def from_watt(watt): 
    if watt <= 0: return -400.0
    return 10 * np.log10(watt) + 30

# --- セッション管理 ---
if 'base_dbm' not in st.session_state:
    st.session_state.base_dbm = 40.0

# --- 入力コールバック ---
def update_dbm(): st.session_state.base_dbm = st.session_state.kb_dbm
def update_dbuv(): st.session_state.base_dbm = from_dbuv(st.session_state.kb_dbuv, st.session_state.z_val)
def update_watt(): st.session_state.base_dbm = from_watt(st.session_state.kb_watt)

# --- 操作エリア ---
z = st.radio("インピーダンス Z (Ω)", [50, 75], index=0, horizontal=True, key="z_val", on_change=update_dbuv)

st.markdown("---")
st.subheader("☁️ 測定値入力（Enterで確定）")

st.markdown("""
<style>
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) input { background-color: #ff4b4b !important; color: white !important; font-weight: bold !important; border: 2px solid #b91c1c !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) input { background-color: #28a745 !important; color: white !important; font-weight: bold !important; border: 2px solid #14532d !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) input { background-color: #007bff !important; color: white !important; font-weight: bold !important; border: 2px solid #1e3a8a !important; }
    label p { color: #333; font-weight: 900 !important; font-size: 18px !important; }
</style>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
target_dbm = st.session_state.base_dbm
target_dbuv = get_dbuv(target_dbm, z)
target_watt = get_watt(target_dbm)

with c1: 
    st.number_input("電力 (dBm)", value=float(target_dbm), step=0.1, format="%.2f", key="kb_dbm", on_change=update_dbm)
with c2: 
    st.number_input("電圧 (dBμV)", value=float(target_dbuv), step=0.1, format="%.2f", key="kb_dbuv", on_change=update_dbuv)
with c3: 
    st.number_input("電力 (W)", value=float(target_watt), step=0.0001, format="%.4f", key="kb_watt", on_change=update_watt)

# --- テーブル生成 ---
start_dbm = np.round(target_dbm + 10.0, 1)
end_dbm = np.round(target_dbm - 10.0, 1)
dbm_list = [np.round(x, 1) for x in np.arange(start_dbm, end_dbm, -0.1)]

if not any(abs(target_dbm - d) < 0.0001 for d in dbm_list):
    dbm_list.append(target_dbm)
dbm_list = sorted(list(set(dbm_list)), reverse=True)

rows_html = ""
for i, d in enumerate(dbm_list):
    dv = get_dbuv(d, z)
    w = get_watt(d)
    is_target = abs(d - target_dbm) < 0.0001
    row_id_attr = "id='target-row'" if is_target else f"id='row-{i}'"
    
    if is_target:
        row_style = "background-color: #333; color: yellow; font-weight: bold; font-size: 22px;"
        c1_s = c2_s = c3_s = ""
        d_disp, dv_disp = f"{d:.2f}", f"{dv:.2f}"
    else:
        row_style = ""
        c1_s, c2_s, c3_s = "background-color: #fdf2f2;", "background-color: #f2fdf2;", "background-color: #f2f2fd;"
        d_disp, dv_disp = f"{d:.1f}", f"{dv:.2f}"

    rows_html += f"""
        <tr {row_id_attr} style="{row_style}">
            <td style="width:33%; border:1px solid #ddd; padding:12px; {c1_s}">{d_disp}</td>
            <td style="width:34%; border:1px solid #ddd; padding:12px; {c2_s}">{dv_disp}</td>
            <td style="width:33%; border:1px solid #ddd; padding:12px; {c3_s}">{w:.4f}</td>
        </tr>
    """

# --- 表示コンポーネント (JSによる自動スクロール付) ---
table_code = f"""
<div style="display: flex; gap: 10px; align-items: flex-start;">
    <div id="scroll-box" style="height: 535px; flex-grow: 1; overflow-y: auto; border: 3px solid #333; border-radius: 8px; scroll-behavior: smooth;">
        <table id="target-table" style="width: 100%; border-collapse: collapse; font-family: sans-serif; text-align: center; table-layout: fixed;">
            <thead>
                <tr style="position: sticky; top: 0; background: #333; color: white; z-index: 10;">
                    <th style="padding:15px; border:1px solid #555;">電力 (dBm)</th>
                    <th style="padding:15px; border:1px solid #555;">電圧 (dBμV)</th>
                    <th style="padding:15px; border:1px solid #555;">電力 (W)</th>
                </tr>
            </thead>
            <tbody style="font-size: 18px;">{rows_html}</tbody>
        </table>
    </div>
    
    <div style="display: flex; flex-direction: column; gap: 8px;">
        <button onclick="goTop()" style="padding:10px; cursor:pointer; font-weight:bold; background:#eee; border:1px solid #ccc; border-radius:4px;">TOP ▲</button>
        <div style="height: 5px;"></div>
        <button onclick="scrollStep(-10)" style="padding:15px 10px; cursor:pointer; font-weight:bold; background:#e1f5fe; border:1px solid #0288d1; border-radius:4px;">10行 ▲</button>
        <button onclick="scrollStep(10)" style="padding:15px 10px; cursor:pointer; font-weight:bold; background:#e1f5fe; border:1px solid #0288d1; border-radius:4px;">10行 ▼</button>
        <div style="height: 5px;"></div>
        <button onclick="goBottom()" style="padding:10px; cursor:pointer; font-weight:bold; background:#eee; border:1px solid #ccc; border-radius:4px;">BTM ▼</button>
    </div>
</div>

<script>
    const box = document.getElementById('scroll-box');
    function jumpToTarget() {{
        const r = document.getElementById('target-row');
        if (r) {{
            box.scrollTop = r.offsetTop - (box.clientHeight / 2) + (r.clientHeight / 2);
        }}
    }}
    function scrollStep(n) {{ box.scrollBy({{ top: 50 * n, behavior: 'smooth' }}); }}
    function goTop() {{ box.scrollTo({{ top: 0, behavior: 'smooth' }}); }}
    function goBottom() {{ box.scrollTo({{ top: box.scrollHeight, behavior: 'smooth' }}); }}

    window.onload = jumpToTarget;
    setTimeout(jumpToTarget, 50);
    setTimeout(jumpToTarget, 300);
</script>
"""

# エラー箇所：heightの改行を修正
components.html(table_code, height=580)

# --- 画面下部中央に「戻る」ボタンを配置 ---
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    # リンクを統一しました
    st.link_button("🏠\n\n戻る", "https://7fjndw39dicdzckugyepb2.streamlit.app/", use_container_width=True)

# ボタンのカスタムスタイル
st.markdown("""
    <style>
    div.stLinkButton > a {
        background-color: #00BFFF !important;
        color: white !important;
        border-radius: 10px;
        text-align: center;
        border: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
