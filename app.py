import streamlit as st
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(page_title="電力・電圧換算テーブル", layout="wide")

# カスタムCSS
st.markdown("""
<style>
    .credit { text-align: right; font-size: 14px; color: #666; }
    /* テーブル全体のスタイル */
    .custom-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 18px; }
    .custom-table th { position: sticky; top: 0; background: #eee; border: 1px solid #ddd; padding: 12px; z-index: 10; }
    .custom-table td { border: 1px solid #ddd; padding: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="credit">開発/制作：緒方</p>', unsafe_allow_html=True)
st.title("📟 dBm ⇄ dBμV ⇄ W 相互換算テーブル")

# --- 計算関数群 ---
def get_dbuv(dbm, z): return dbm + 10 * np.log10(z) + 90
def get_watt(dbm): return 10**((dbm - 30) / 10)
def from_dbuv(dbuv, z): return dbuv - (10 * np.log10(z) + 90)
def from_watt(watt): return 10 * np.log10(watt) + 30 if watt > 0 else -127.0

# --- セッション状態の初期化 ---
if 'base_dbm' not in st.session_state:
    st.session_state.base_dbm = 40.0

# --- 条件設定 ---
z = st.radio("インピーダンス Z (Ω)", [50, 75], index=0, horizontal=True)

st.markdown("---")
st.subheader("☁️ 測定値入力（自動スクロール連動）")
c1, c2, c3 = st.columns(3)

# 3つの入力枠の連動処理
with c1:
    v_dbm = st.number_input("電力 (dBm)", value=float(st.session_state.base_dbm), step=0.1, format="%.2f")
    if v_dbm != round(st.session_state.base_dbm, 2):
        st.session_state.base_dbm = v_dbm
        st.rerun()

with c2:
    cur_dbuv = get_dbuv(st.session_state.base_dbm, z)
    v_dbuv = st.number_input("電圧 (dBμV)", value=float(cur_dbuv), step=0.1, format="%.2f")
    if v_dbuv != round(cur_dbuv, 2):
        st.session_state.base_dbm = from_dbuv(v_dbuv, z)
        st.rerun()

with c3:
    cur_watt = get_watt(st.session_state.base_dbm)
    v_watt = st.number_input("電力 (W)", value=float(cur_watt), step=0.0001, format="%.4f")
    if v_watt != round(cur_watt, 4):
        st.session_state.base_dbm = from_watt(v_watt)
        st.rerun()

# --- テーブルデータの生成 ---
# 40.0 から -127.0 まで 0.1刻み
dbm_range = np.around(np.arange(40.0, -127.1, -0.1), 1)
target_val = round(st.session_state.base_dbm, 1)

table_rows_html = ""
for i, d in enumerate(dbm_range):
    dv = get_dbuv(d, z)
    w = get_watt(d)
    w_str = f"{w:.4e}" if w < 0.001 else f"{w:.4f}"
    
    # 入力値に一番近い行を特定してIDとスタイルを付与
    is_target = "id='target-row' style='background-color: #007bff; color: white; font-weight: bold;'" if d == target_val else ""
    
    table_rows_html += f"""
        <tr {is_target}>
            <td>{d:.1f}</td>
            <td>{dv:.2f}</td>
            <td>{w_str}</td>
        </tr>
    """

# --- JavaScript付きHTMLテーブルの描画 ---
full_html = f"""
<div id="scroll-container" style="height: 600px; overflow-y: auto; border: 2px solid #005A9C; border-radius: 10px;">
    <table class="custom-table">
        <thead>
            <tr>
                <th>電力 (dBm)</th>
                <th>電圧 (dBμV)</th>
                <th>電力 (W)</th>
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
    </table>
</div>

<script>
    function scrollToTarget() {{
        var container = document.getElementById('scroll-container');
        var target = document.getElementById('target-row');
        if (target && container) {{
            // ターゲット行がコンテナの「上から5行目」あたりに来るように位置を調整
            var rowHeight = target.offsetHeight;
            var targetOffset = target.offsetTop;
            container.scrollTop = targetOffset - (rowHeight * 5);
        }}
    }}
    // 画面更新時に実行
    window.onload = scrollToTarget;
    // Streamlitの再描画対策で少し遅らせても実行
    setTimeout(scrollToTarget, 50);
</script>

<style>
    .custom-table {{ width: 100%; border-collapse: collapse; }}
    .custom-table th, .custom-table td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
    .custom-table th {{ position: sticky; top: 0; background-color: #f8f9fa; }}
</style>
"""

components.html(full_html, height=650)

st.info(f"💡 現在の計算基準: {st.session_state.base_dbm:.2f} dBm 付近を5行目に表示中")
