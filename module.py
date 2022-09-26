import streamlit as st
import sqlite3
import pandas as pd
import pickle
import gensim
import mojimoji
import unicodedata
from abc import ABCMeta


# 管理者の設定
administrators = ['admin1', 'admin2']


# 抽象クラスPage(それぞれのページで継承して使う)
class Page(metaclass = ABCMeta):
    def __init__(self, cor): # corはCorpusクラスのインスタンス（集約）
        self.state = st.session_state
        self.cor = cor
        self.user = self.get_user()
        self.users = self.get_users()
        self.authority = self.user in administrators 

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
    def get_model(self):
        with open('fastText.ja.300.vec.pkl',  mode = 'rb') as fp:
            return pickle.load(fp)

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