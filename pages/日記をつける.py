import streamlit as st
import datetime as dt
from zoneinfo import ZoneInfo
import sqlite3
import MeCab


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



def make_row(word, kana_index=7, lemma_index=6):
    ff = dict(enumerate(word.feature.split(",")))
    return dict(surface=word.surface, kana=ff.get(kana_index), lemma=ff.get(lemma_index), 
            pos1=ff.get(0), pos2=ff.get(1), pos3=ff.get(2), pos4=ff.get(3))


def home():
    user = st.session_state['user']
    st.sidebar.header(f'{user}の日記')

    st.title('How was your day?')

    now = dt.datetime.now(ZoneInfo("Asia/Tokyo"))
    isoformat = now.isoformat()
    c = dt.datetime.fromisoformat(isoformat)
    week_number = dt.date(c.year,c.month,c.day).weekday()

    st.subheader(f'{c.month}月{c.day}日（{WEEK[week_number]}）')
    
    page_date = st.date_input('どのページに書き込みますか？', dt.date(c.year, c.month, c.day))    
    
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

        data = []
        tagger = MeCab.Tagger("-d /home/appuser/venv/lib/python3.9/site-packages/ipadic")
        node = tagger.parseToNode(input_data)
        while node:
            if node.feature.startswith('BOS/EOS'):
                pass
            else:
                data.append(make_row(node))
            node = node.next
            
        st.write('')
        st.write('このページで使用した言葉')
        st.table(data)



if 'user' not in st.session_state:
    st.info("ログイン後に利用可能です")

else:
    home()