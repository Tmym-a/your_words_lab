import streamlit as st
import sqlite3
import pandas as pd
import random

if 'user' not in st.session_state:
    st.info("ログイン後に利用可能です")

else:
    user = st.session_state['user']
    st.sidebar.header(f'{user}の日記')
    st.title('Your Diary')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    query = 'SELECT * FROM diary ;'
    df = pd.read_sql(query, con = conn)
    c.close()
    
    try:
        user_df = df[df['writer']==user]
        date_words = user_df[['date','words']]
        date_words = date_words.sort_values('date')

        chart_x = date_words['date']
        chart_y = [random.randint(-10,10) for _ in range(len(chart_x))]
        chart_df = pd.DataFrame(chart_y, columns=['feeling'])
        chart_df.index = chart_x
        st.write('気分の変動')
        st.line_chart(chart_df)

        st.write('日記')
        st.table(date_words.head(30))

    except KeyError:
        st.warning('まだ日記に何も書いてありません')

