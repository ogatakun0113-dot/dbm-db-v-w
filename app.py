import streamlit as st
import numpy as np
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="電力・電圧換算テーブル", layout="wide")

st.markdown("""
<style>
    .credit { text-align: right; font-size: 14px; color: #666; }
    /* 青色マーカー用のスタイル */
    .highlight-row {
        background-color: #007bff !important;
        color: white !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="credit">開発/制作：緒方</p>', unsafe_allow_html=True)
st.title("📟 dBm ⇄ dBμV ⇄ W 相互換算テーブル")

# --- 計算・変換用関数 ---
def dbm_to_others(dbm, z):
    watt = 10**((dbm - 30) / 10)
    dbuv = dbm + 10 * np.log10(z) + 90
    return dbuv, watt

def dbuv_to_dbm(dbuv, z):
    return dbuv - (10 * np.log10(z) + 90)

def watt_to_dbm(watt):
    if watt <= 0: return -127.0
    return 10 * np.log10(watt) + 30

# --- 入力エリア ---
st.subheader("💡 条件設定")
z = st.radio("インピーダンス Z (Ω)", [50, 75], index=0, horizontal=True)

st.markdown("---")
st.subheader("☁️ 測定値入力（いずれかに入力してください）")
c1, c2, c3 = st.columns(3)

# セッション状態で入力を管理
if 'base_dbm' not in st.session_state:
    st.session_state.base_dbm = 40.0

# 各入力枠の処理
with c1:
    in_dbm = st.number_input("電力 (dBm)", value=st.session_state.base_dbm, step=0.1, format="%.2f", key="dbm_input")
    st.session_state.base_dbm = in_dbm

with c2:
    # 現在のdBmからdBμVを計算して表示、入力されたら逆算
    current_dbuv, _ = dbm_to_others(st.session_state.base_dbm, z)
    in_dbuv = st.number_input("電圧 (dBμV)", value=float(current_dbuv), step=0.1, format="%.2f", key="dbuv_input")
    if in_dbuv != round(current_dbuv, 2):
        st.session_state.base_dbm = dbuv_to_dbm(in_dbuv, z)

with c3:
    # 現在のdBmからWを計算して表示、入力されたら逆算
    _, current_watt = dbm_to_others(st.session_state.base_dbm, z)
    in_watt = st.number_input("電力 (W)", value=float(current_watt), step=0.001, format="%.4f", key="watt_input")
    if in_watt != round(current_watt, 4):
        st.session_state.base_dbm = watt_to_dbm(in_watt)

# --- データテーブル作成 ---
dbm_range = np.around(np.arange(40.0, -127.1, -0.1), 1)
rows = []
target_idx = 0

for i, d in enumerate(dbm_range):
    dv, w = dbm_to_others(d, z)
    rows.append([d, round(dv, 2), f"{w:.4e}" if w < 0.01 else f"{w:.4f}"])
    # 入力値に一番近いインデックスを特定
    if abs(d - st.session_state.base_dbm) < 0.05:
        target_idx = i

# HTMLテーブルの生成（JavaScriptでの制御用）
table_html = f"""
<div id="table-container" style="height: 500px; overflow-y: auto; border: 1px solid #ccc; background: white;">
    <table style="width: 100%; border-collapse: collapse; font-family: sans-serif;">
        <thead style="position: sticky; top: 0; background: #eee; z-index: 10;">
            <tr>
                <th style="border: 1px solid #ddd; padding: 8px;">電力 (dBm)</th>
                <th style="border: 1px solid #ddd; padding: 8px;">電圧 (dBμV)</th>
                <th style="border: 1px solid #ddd; padding: 8px;">電力 (W)</th>
            </tr>
        </thead>
        <tbody>
"""

for i, row in enumerate(rows):
    bg_style = "background-color: #007bff; color: white; font-weight: bold;" if i == target_idx else ""
    row_id = f'id="target-row"' if i == target_idx else ""
    table_html += f"""
            <tr {row_id} style="{bg_style}">
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{row[0]:.1f}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{row[1]}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{row[2]}</td>
            </tr>
    """

table_html += """
        </tbody>
    </table>
</div>

<script>
    // 少し遅らせて実行することで確実に描画後にスクロールさせる
    setTimeout(function() {
        var container = document.getElementById('table-container');
        var target = document.getElementById('target-row');
        if (target) {
            // ターゲット行がコンテナの上から「行の高さ5倍分」下に来るように計算
            var offset = target.offsetTop - (target.offsetHeight * 5);
            container.scrollTop = offset;
        }
    }, 100);
</script>
"""

# HTMLコンポーネントとして表示
components.html(table_html, height=550)

st.info(f"💡 現在の計算基準: {st.session_state.base_dbm:.2f} dBm / {z}Ω")
