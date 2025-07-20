import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm 

# フォント設定
plt.rcParams['font.family'] = 'MS Gothic'

# 四則演算の問題を生成する関数
def generate_problem(op, min_digits, max_digits):
    digit_min = 10**(min_digits - 1)
    digit_max = 10**max_digits - 1

    if op == '÷':
        # 割り切れる割り算を作成（b * ans = a）
        b = random.randint(digit_min, digit_max)
        ans = random.randint(digit_min, digit_max)
        a = b * ans
        return a, b, ans
    else:
        a = random.randint(digit_min, digit_max)
        b = random.randint(digit_min, digit_max)
        if op == '-':
            if a < b:
                a, b = b, a  # 引き算はマイナス回避
            return a, b, a - b
        elif op == '+':
            return a, b, a + b
        elif op == '×':
            return a, b, a * b

# UIのタイトル
st.title("四則演算トレーニングツール")

# 設定フォーム
with st.form(key="config_form"):
    op = st.selectbox("演算を選択", ['+', '-', '×', '÷'])
    num_questions = st.number_input("出題数", min_value=1, max_value=100, value=10)
    min_digits = st.number_input("最小桁数", min_value=1, max_value=5, value=1)
    max_digits = st.number_input("最大桁数", min_value=min_digits, max_value=9, value=min_digits)
    start_btn = st.form_submit_button("スタート")

# 出題開始
if start_btn:
    st.session_state.problems = []
    st.session_state.answers = []
    st.session_state.op = op
    for _ in range(num_questions):
        a, b, ans = generate_problem(op, min_digits, max_digits)
        st.session_state.problems.append((a, b))
        st.session_state.answers.append(ans)

# 回答セクション
if 'problems' in st.session_state:
    st.subheader("問題")
    user_inputs = []

    for i, (a, b) in enumerate(st.session_state.problems):
        # 問題文を markdown で番号つき表示（例：1) 88 + 70 =）
        st.markdown(f"**{i+1}) {a} {st.session_state.op} {b} =**")
        
        # ラベルなしで入力欄を表示
        user_input = st.number_input(
            label="",
            key=f"user_input_{i}",
            step=1,
            format="%d"
        )
        user_inputs.append(user_input)

    # 採点ボタン
    if st.button("採点"):
        st.session_state.user_inputs = user_inputs
        results = []

        for i in range(len(user_inputs)):
            correct = st.session_state.answers[i]
            user = user_inputs[i]
            is_correct = correct == user
            results.append({
                "問題": f"{st.session_state.problems[i][0]} {st.session_state.op} {st.session_state.problems[i][1]}",
                "あなたの答え": user,
                "正解": correct,
                "正誤": "◯" if is_correct else "×"
            })

        # 結果表示
        df = pd.DataFrame(results)
        df["あなたの答え"] = df["あなたの答え"].astype(int)
        df["正解"] = df["正解"].astype(int)
        st.dataframe(df)

        # 正誤カウント＆グラフ化
        score = sum(1 for row in results if row["正誤"] == "◯")
        st.write(f"正解数: {score} / {len(results)}")

        fig, ax = plt.subplots()
        bars = ax.bar(["正解", "不正解"], 
            [score, len(results) - score],
            color=["green", "red"],
            label=["正解", "不正解"],
        )
        ax.legend() # 凡例追加
        ax.set_title("正解・不正解の結果")
        st.pyplot(fig)

        # CSVダウンロード
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("結果をCSVで保存", data=csv, file_name="results.csv", mime="text/csv")