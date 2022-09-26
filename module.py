import streamlit as st
import sqlite3
import pandas as pd
import pickle
import gensim
import mojimoji
import unicodedata
from abc import ABCMeta


# 管理者の設定
if 'administrators' not in st.session_state:
    st.session_state['administrators'] = ['admin1', 'admin2']

# 初期化
if 'model' not in st.session_state:
    with open('fastText.ja.300.vec.pkl',  mode = 'rb') as fp:
        st.session_state['model'] = pickle.load(fp)

if 'polarity_df' not in st.session_state:
    st.session_state['polarity_df'] = pd.read_pickle('nega_posi_df.pkl')


# 抽象クラスPage(それぞれのページで継承して使う)
class Page(metaclass = ABCMeta):
    def __init__(self, session_state, cor): # corはCorpusクラスのインスタンス（集約）
        self.state = session_state
        self.cor = cor
        self.user = self.get_user()
        self.users = self.get_users()
        self.authority = self.user in self.state['administrators']  

    # ログイン済みユーザー名の取得
    def get_user(self):
        if 'user' not in self.state:
            return None
        else:
            return self.state['user']
            
    # 登録してある全ユーザー名の取得
    def get_users(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        query = 'SELECT username FROM userstable;'
        users = pd.read_sql(query, con = conn).values.ravel()
        c.close()
        return users

    # ログイン済みかどうかの確認
    def check_login_status(self):
        if not self.user:
            st.info("ログイン後に利用可能です")
        else:
            self.main()

    # ページの表示
    def main(self):
        pass


class Corpus():
    def __init__(self, session_state):
        self.state = session_state
        self.model = self.state['model']
        self.polarity = self.state['polarity_df']
        self.polarity_keys = set(self.polarity.index.to_list())

    # 前処理（単語の正規化）
    def preprocessing(self, text):  
        result = mojimoji.zen_to_han(text, kana=False)
        result = mojimoji.han_to_zen(result, ascii=False)
        result = unicodedata.normalize('NFKC', result)
        return result

    # reportsをdfとして取得
    def get_reports_df(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        query = 'SELECT * FROM reports;'
        df = pd.read_sql(query, con = conn)
        c.close()
        return df