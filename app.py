import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import datetime  #時間管理用

# ───────── フォント設定 ─────────
font_path = "NotoSansJP-Regular.ttf"
jp_font = fm.FontProperties(fname=font_path)
plt.rcParams["font.family"] = jp_font.get_name()

# ───────── 四則演算の問題を生成 ─────────
def generate_problem(op, min_digits, max_digits):
    digit_min = 10 ** (min_digits - 1)
    digit_max = 10 ** max_digits - 1

    if op == "÷":
        b = random.randint(digit_min, digit_max)
        ans = random.randint(digit_min, digit_max)
        a = b * ans
        return a, b, ans
    else:
        a = random.randint(digit_min, digit_max)
        b = random.randint(digit_min, digit_max)
        if op == "-" and a < b:
            a, b = b, a
        if op == "+":
            return a, b, a + b
        elif op == "-":
            return a, b, a - b
        elif op == "×":
            return a, b, a * b

# ───────── UI ─────────
st.title("四則演算トレーニングツール")

with st.form("config_form"):
    op  = st.selectbox("演算を選択", ["+", "-", "×", "÷"])
    n   = st.number_input("出題数", 1, 100, 10, step=1, format="%d")
    d1  = st.number_input("最小桁数", 1, 5, 1,  step=1, format="%d")
    d2  = st.number_input("最大桁数", d1, 9, d1, step=1, format="%d")
    start = st.form_submit_button("スタート")

# ───────── 問題生成 ─────────
if start:
    # --- 出題内容を初期化 ---
    st.session_state.prob = []
    st.session_state.ans  = []
    st.session_state.op   = op
    st.session_state.start_time = datetime.datetime.now()

    # --- 入力値の初期化もここで定義 ---
    for i in range(1, n + 1):
        st.session_state[f"in_{i}"] = 0  # ← 直接0をセット（これが本質）

    # --- 問題と答えを生成 ---
    for _ in range(n):
        a, b, c = generate_problem(op, d1, d2)
        st.session_state.prob.append((a, b))
        st.session_state.ans.append(c)

    # --- rerunフラグで次の描画に備える ---
    st.session_state.rerun_flag = True

# --- rerun 実行 ---
if st.session_state.get("rerun_flag", False):
    st.session_state.rerun_flag = False
    st.rerun()

# ───────── 回答欄 ─────────
if "prob" in st.session_state:
    st.subheader("問題")
    inputs = []
    for i, (a, b) in enumerate(st.session_state.prob, 1):
        st.markdown(f"**{i}) {a} {st.session_state.op} {b} =**")
        val = st.number_input(
            "",
            key=f"in_{i}",
            value=0,  # 初期値だけを設定
            step=1,
            format="%d"
        )

        inputs.append(val)

    # ───────── 採点 ─────────
    if st.button("採点"):
        res, correct_ct = [], 0
        for i, user in enumerate(inputs):
            correct = st.session_state.ans[i]
            ok = (user == correct)
            if ok: correct_ct += 1
            res.append({
                "問題": f"{st.session_state.prob[i][0]} {st.session_state.op} {st.session_state.prob[i][1]}",
                "あなたの答え": int(user),
                "正解": correct,
                "判定": "◯" if ok else "×"
            })

        df = pd.DataFrame(res)
        st.dataframe(df)
        st.write(f"正解数: {correct_ct}/{len(res)}")

        # ───────── 経過時間の表示 ─────────
        if "start_time" in st.session_state:
            elapsed = datetime.datetime.now() - st.session_state.start_time
            h, m, s = str(elapsed).split(":")
            st.write(f"所要時間: {int(float(h))}時間 {int(float(m))}分 {int(float(s))}秒")

        # ───────── グラフ（日本語→画像化で豆腐回避） ─────────
        fig, ax = plt.subplots()
        ax.bar("正解",     correct_ct,          color="green", label="正解")
        ax.bar("不正解",   len(res)-correct_ct, color="red",   label="不正解")
        ax.set_title("正解・不正解の結果", fontproperties=jp_font)
        ax.legend(prop=jp_font)

        # 豆腐対策
        for label in ax.get_xticklabels():
            label.set_fontproperties(jp_font)

        st.pyplot(fig)

        # ───────── CSV ダウンロード ─────────
        st.download_button(
            "結果をCSVで保存",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="results.csv",
            mime="text/csv"
        )