import streamlit as st
import sqlite3
import pandas as pd


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
        st.table(date_words.head(30))

    except KeyError:
        st.warning('まだ日記に何も書いてありません')

