import streamlit as st
import datetime
import sqlite3 

WEEK = ('月', '火', '水', '木', '金', '土', '日')


def edit(page_date, user, input_data):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        try:
            query = 'INSERT INTO diary(date, writer, words) VALUES (?, ?, ?);'
            c.execute(query, (page_date, user, input_data))
            conn.commit()

        except sqlite3.IntegrityError:
            query = '''
            UPDATE diary set words = ?
            WHERE date = ? AND writer = ?;
            '''
            c.execute(query, (input_data, page_date, user))
            conn.commit()

        c.close()
        st.info('上記の内容で書き込みました')


def home():
    user = st.session_state['user']
    st.sidebar.header(f'{user}の日記')

    st.title('How was your day?')
    today = datetime.date.today()
    st.subheader(f'{today.month}月{today.day}日（{WEEK[today.weekday()]}）')
    
    page_date = st.date_input('どのページに書き込みますか？', datetime.date(today.year, today.month, today.day))    
    
    st.write('')

    input_option = st.selectbox('入力データの選択', ('直接入力', 'テキストファイル'))
    input_data = None

    if input_option == '直接入力':
        input_data = st.text_area('',placeholder='ここにテキストを入力してください。')
    else:
        uploaded_file = st.file_uploader('テキストファイルをアップロードしてください。', ['txt'])    
        if uploaded_file is not None:
            content = uploaded_file.read()
            input_data = content.decode()

    if input_data is not None:
        st.write('入力データ')
        st.write(input_data)

    if st.button('保存'):
        edit(page_date, user, input_data)


if 'user' not in st.session_state:
    st.info("ログイン後に利用可能です")

else:
    home()