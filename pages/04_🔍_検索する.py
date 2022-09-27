import streamlit as st
import pandas as pd
import module


class Corpus4(module.Corpus):
    def __init__(self):
        self.model = self.get_model()

    def result(self, keyword):
        keyword = self.preprocessing(keyword)

        if keyword in self.model.index_to_key:
            col1, col2 = st.columns(2)

            with col1:
                similar_df = pd.DataFrame(self.model.most_similar(positive=[keyword]))
                similar_df = similar_df.set_index(0)
                similar_df.columns = ['cos類似度']
                st.write('Similar words')
                st.table(similar_df)
            with col2:
                opposite_df = pd.DataFrame(self.model.most_similar(negative=[keyword])).iloc[::-1]
                opposite_df = opposite_df.set_index(0)
                opposite_df.columns = ['cos類似度']
                st.write('Opposite words')
                st.table(opposite_df)
        else:
            st.info('申し訳ありません。その単語は登録されていないため検索できません。')


class Page4(module.Page):
    def main(self):
        st.title('Vocabulary')
        st.caption('''
        解析結果などをもとに単語を入力し、普段使っている言葉と同じ方向性を持つ言葉や、真逆の方向性を持つ言葉
        を眺めて、自分の言葉に対する理解を深めましょう。
        ''')     

        col1, col2 = st.columns(2)
        with col1:
            keyword = st.text_input('単語の入力')
        with col2:
            st.write('##')
            button = st.button('調べる')
        st.write('##')

        if button:
            self.cor.result(keyword)


cor = Corpus4()
page = Page4(cor)

page.check_login_status()