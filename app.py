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
def update_dbm(): 
    st.session_state.base_dbm = st.session_state.kb_dbm

def update_dbuv(): 
    # 入力されたdBµVから正確なdBmを逆算して保持
    st.session_state.base_dbm = from_dbuv(st.session_state.kb_dbuv, st.session_state.z_val)

def update_watt(): 
    # 入力されたWから正確なdBmを逆算して保持
    st.session_state.base_dbm = from_watt(st.session_state.kb_watt)

# --- 操作エリア ---
z = st.radio("インピーダンス Z (Ω)", [50, 75], index=0, horizontal=True, key="z_val")

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

# 現在の基準dBmから正確な値を計算（表示用）
cur_dbm = st.session_state.base_dbm
cur_dbuv = get_dbuv(cur_dbm, z)
cur_watt = get_watt(cur_dbm)

with c1:
    st.number_input("電力 (dBm)", value=float(cur_dbm), step=0.1, format="%.2f", key="kb_dbm", on_change=update_dbm)
with c2:
    st.number_input("電圧 (dBμV)", value=float(cur_dbuv), step=0.1, format="%.2f", key="kb_dbuv", on_change=update_dbuv)
with c3:
    st.number_input("電力 (W)", value=float(cur_watt), step=0.0001, format="%.4f", key="kb_watt", on_change=update_watt)

# --- テーブル生成 ---
# 入力された正確な値を表に組み込むため、前後の0.1ステップ値を生成
step = 0.1
target_dbm = st.session_state.base_dbm
start_dbm = np.floor(target_dbm * 10) / 10 + (step * 50) # 入力値の前後を表示範囲にする
if start_dbm > 40.0: start_dbm = 40.0

# 0.1刻みのベースリストを作成
dbm_list = np.around(np.arange(start_dbm, -250.1, -step), 1).tolist()

# 入力値(target_dbm)がリストに存在しない（端数がある）場合、適切な位置に挿入
if not any(np.isclose(target_dbm, d) for d in dbm_list):
    dbm_list.append(target_dbm)
    dbm_list.sort(reverse=True)

rows_html = ""
for d in dbm_list:
    dv = get_dbuv(d, z)
    w = get_watt(d)
    
    # ターゲット行の判定（誤差を考慮）
    is_target = np.isclose(d, target_dbm)
    
    w_display = f"{w:.4f}" if w >= 0.0001 else "----"
    dv_display = f"{dv:.2f}" if dv >= -107.00 else "----"
    
    if is_target:
        row_id = "id='target-row'"
        row_style = "background-color: #333; color: yellow; font-weight: bold; font-size: 22px;"
        c1_s = c2_s = c3_s = ""
        # 入力値そのものを正確に表示
        d_display = f"{d:.2f}" 
    else:
        row_id = ""
        row_style = ""
        c1_s = "background-color: #fdf2f2;"
        c2_s = "background-color: #f2fdf2;"
        c3_s = "background-color: #f2f2fd;"
        d_display = f"{d:.1f}"

    rows_html += f"""
        <tr {row_id} style="{row_style}">
            <td style="width:33%; border:1px solid #ddd; padding:12px; {c1_s}">{d_display}</td>
            <td style="width:34%; border:1px solid #ddd; padding:12px; {c2_s}">{dv_display}</td>
            <td style="width:33%; border:1px solid #ddd; padding:12px; {c3_s}">{w_display}</td>
        </tr>
    """
    # 描画負荷軽減のため、ターゲットより大幅に低い値で打ち切り
    if d < (target_dbm - 10) and w < 0.0001: break

# --- 表示 & JS ---
table_code = f"""
<div id="scroll-box" style="height: 520px; overflow-y: auto; border: 3px solid #333; border-radius: 8px;">
    <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; text-align: center; table-layout: fixed;">
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
