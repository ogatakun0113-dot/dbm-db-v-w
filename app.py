# --- テーブル生成内のループ部分を修正 ---
for i, d in enumerate(dbm_list):
    # -0.04 などが四捨五入で -0.00 になるのを防ぐ
    display_d = d
    if abs(d) < 0.001:  # ほぼ0なら
        display_d = 0.0

    dv = get_dbuv(d, z)
    w = get_watt(d)
    is_target = np.isclose(d, target_dbm, atol=0.001)
    
    row_id_attr = f"id='target-row'" if is_target else f"id='row-{i}'"
    
    if is_target:
        row_style = "background-color: #333; color: yellow; font-weight: bold; font-size: 22px;"
        c1_s = c2_s = c3_s = ""
        # ここで表示を 0.00 に固定
        d_text = f"{abs(display_d):.2f}" if display_d == 0 else f"{display_d:.2f}"
    else:
        row_style = ""
        c1_s = "background-color: #fdf2f2;"
        c2_s = "background-color: #f2fdf2;"
        c3_s = "background-color: #f2f2fd;"
        d_text = f"{abs(display_d):.1f}" if display_d == 0 else f"{display_d:.1f}"

    # ...以下、rows_html への追加処理
