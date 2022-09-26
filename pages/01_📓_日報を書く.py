import streamlit as st
import datetime as dt
from zoneinfo import ZoneInfo
import sqlite3
import MeCab
import pandas as pd
import module


class Corpus1(module.Corpus):
    def __init__(self):
        self.polarity = pd.read_pickle('nega_posi_df.pkl')
        self.polarity_keys = set(self.polarity.index.to_list())

    def make_row(self, word, kana_index=6, lemma_index=7):
        ff = dict(enumerate(word.feature.split(',')))
        if ff.get(lemma_index) in self.polarity_keys:
            score = self.polarity.loc[ff.get(lemma_index), 'スコア']
        else:
            score = 0
        return dict(表層形=word.surface, カナ=ff.get(kana_index), 原形=ff.get(lemma_index), 
                品詞1=ff.get(0), 品詞2=ff.get(1), 品詞3=ff.get(2), 品詞4=ff.get(3), 極性=score)


class Page1(module.Page):
    def __init__(self, cor):
        super().__init__(cor)
        self.WEEK = ('月', '火', '水', '木', '金', '土', '日')
        self.zone = self.get_zone()
    
    def get_zone(self):
        now = dt.datetime.now(ZoneInfo('Asia/Tokyo'))
        isoformat = now.isoformat()
        zone = dt.datetime.fromisoformat(isoformat)
        return zone    

    def info_today(self):
        zone = self.zone
        week_number = dt.date(zone.year,zone.month,zone.day).weekday()
        return f'今日 : {zone.month}月{zone.day}日（{self.WEEK[week_number]}）'
    
    def get_input_data(self):
        input_option = st.sidebar.selectbox('入力データの選択', ('直接入力', 'テキストファイル'))
        input_data = None

        if input_option == '直接入力':
            input_data = st.text_area('直接入力',placeholder='ここにテキストを入力してください。')
        else:
            uploaded_file = st.file_uploader('テキストファイルをアップロードしてください。', ['txt'])    
            if uploaded_file is not None:
                content = uploaded_file.read()
                input_data = content.decode()
        return input_data

    def edit(self, total_score):
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            try:
                query = 'INSERT INTO reports(date, writer, words, feelings, variables) VALUES (?, ?, ?, ?, ?);'
                c.execute(query, (self.page_date, self.user, self.input_data, total_score, self.input_number))
                conn.commit()

            except sqlite3.IntegrityError:
                query = '''
                UPDATE reports set words = ?, feelings = ?, variables = ?
                WHERE date = ? AND writer = ?;
                '''
                c.execute(query, (self.input_data, total_score, self.input_number, self.page_date, self.user))
                conn.commit()
            c.close()
            st.info('上記の内容で書き込みました')      
                
    def result(self):
        total_score = 0
        data = []   
        tagger = MeCab.Tagger()
        node = tagger.parseToNode(self.input_data)

        while node:
            if node.feature.startswith('BOS/EOS'):
                pass
            else:
                row = self.cor.make_row(node)
                total_score += row['極性']
                data.append(row)
            node = node.next

        self.edit(total_score)         
        st.write('')
        st.write('このページで使用した言葉')
        st.table(data)
        st.write('数値:', self.input_number)
        st.write('極性判定:', total_score)

    def main(self):
        st.title('How was your day?')

        st.sidebar.subheader(self.info_today())
        st.sidebar.header(f'{self.user}の日報')
        self.page_date = st.sidebar.date_input('どのページに書き込みますか？', dt.date(self.zone.year, self.zone.month, self.zone.day))  

        st.subheader(self.page_date)
        self.input_data = self.get_input_data()

        if self.input_data is not None:
            st.write('入力データ')
            st.write(self.input_data)
        st.write('##')
        self.input_number = st.slider('数値（訪問件数など）を入力できます', 0, 10, 0)

        if st.button('保存'):
            self.result()  


cor = Corpus1()
page = Page1(cor)

page.check_login_status()
