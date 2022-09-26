import streamlit as st
import time
import MeCab
from wordcloud import WordCloud
from collections import defaultdict
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import module


class Corpus3(module.Corpus):
    def __init__(self, session_state):
        super().__init__(session_state)
        self.fpath = './IPAfont00303/ipam.ttf'

    def morphological_analysis(self, text, selected_parts, stop_words):
        tagger = MeCab.Tagger()
        node = tagger.parseToNode(text)
        dic = defaultdict(int)
        morpheme_words = []

        while  node:
            surface = node.surface
            surface = self.preprocessing(surface)

            if node.feature.startswith('BOS/EOS') or surface in stop_words:
                pass
            else:
                f = node.feature.split(',')      
                pos1 = f[0]

                if pos1 in selected_parts and surface != '':
                    dic[(surface, pos1)] += 1
                    morpheme_words.append(surface)

            node = node.next
            
        sorted_items = sorted(dic.items(), key = lambda x: -x[1])
        merged_list = []

        for k, v in sorted_items:
            merged_list.append([k[0], k[1], v])

        self.full_text = ' '.join(morpheme_words)
        self.df = pd.DataFrame(merged_list)
        self.df.columns = ['表層形','品詞','度数']
        self.keys = [_[0][0] for _ in sorted_items]
        self.values = [_[1] for _ in sorted_items[:10]]

    def unsupervised_learning(self):
        vectors = []
        self.keys_in_model = []

        for key in self.keys:
            if key in self.model.index_to_key:
                vectors.append(self.model[key])
                self.keys_in_model.append(key)
        # 主成分分析
        self.model2d = PCA(n_components=2, whiten=True)
        self.model2d.fit(np.array(vectors[:30]).T)

        # クラスタリング
        n_clusters = int(np.sqrt(len(self.keys_in_model))) + 1
        kmeans_model = KMeans(n_clusters=n_clusters, verbose=1, random_state=0) 
        kmeans_model.fit(vectors)

        self.cluster_labels = kmeans_model.labels_

    def get_wc_img(self):
        wc = WordCloud(background_color='white', width=960, height=720, font_path=self.fpath)
        wc.generate(self.full_text)
        wc.to_file('wc.png')    
        img = Image.open('wc.png')
        return img
    
    def draw_TOP10_chart(self):
        fig, ax = plt.subplots()
        ax.bar(self.keys[:10], self.values)
        fig.suptitle('出現頻度 TOP10')
        st.pyplot(fig)

    def vector_plot(self):
        model2d = self.model2d
        fig, ax = plt.subplots()
        ax.scatter(model2d.components_[0],model2d.components_[1])

        for (x,y), name in zip(model2d.components_.T, self.keys_in_model[:30]):
            ax.annotate(name, (x,y))
        fig.suptitle('単語ベクトルの分布（上位３０単語まで）')
        st.pyplot(fig)

    def get_cluster_to_words(self):
        cluster_to_words = defaultdict(list)
        for cluster_id, word in zip(self.cluster_labels, self.keys_in_model):
            cluster_to_words[cluster_id].append(word)
        return cluster_to_words


class Page3(module.Page):
    def __init__(self, session_state, cor):
        super().__init__(session_state, cor)
        self.all_parts = ['名詞','代名詞','形状詞','連体詞','副詞','接続詞','感動詞',
                        '動詞','形容詞','助動詞','助詞','接頭辞','接尾辞','記号','補助記号']

    def get_user_df(self, input_users):
        df = self.cor.get_reports_df()[['writer', 'words']]

        if self.authority:
            if not input_users:
                user_df = df
            else:
                user_df = df.query('writer in @input_users')
        else:           
            user_df = df[df['writer']==self.user]
        
        return user_df

    def display_tabs(self):
        comment = st.empty()
        comment.text('Start!')

        st.subheader('解析結果')

        with st.spinner('Wait for it...'):         
            tab1, tab2, tab3, tab4 = st.tabs(['🌩 Word cloud', '📊 TOP10', '📉 Vectors', '💥 Clusters'])
            
            with tab1:
                img = self.cor.get_wc_img()
                st.image(img, caption='あなたの日記の内容から作成されたワードクラウド', use_column_width=True)

            with tab2:
                self.cor.draw_TOP10_chart()

            st.sidebar.header('Below is a DataFrame:')
            st.sidebar.write('🗃 該当ワード一覧', self.cor.df.head(1000))
            st.sidebar.caption('※ 列名をクリックでソート可能')  
            
            comment.text('Done!')

        self.cor.unsupervised_learning() 

        with tab3:
            self.cor.vector_plot()
            st.caption('※ 可視化のため、ベクトル空間を300次元から2次元に次元削減しています')  

        with tab4:
            st.write('似ている言葉のグループ')
            cluster_to_words = self.cor.get_cluster_to_words()

            for i, words in enumerate(cluster_to_words.values()):
                cluster_df = pd.DataFrame(words).T
                cluster_df.index = [f'cluster {i}']
                st.write(cluster_df)


    def main(self):
        st.title('Your Words Laboratory')

        with st.expander('形態素解析フォーム', expanded=True):
            with st.form(key='select_form'):
                options = st.multiselect('品詞の選択', self.all_parts, ['名詞'])
                st.caption('※ 形状詞とは、UniDicの品詞体系で、形容動詞語幹を意味しています。')
                st.text('これまでの書き込み内容を形態素解析し、上記の品詞に該当する言葉を抽出します。')
                st.write('')

                stop_line = st.text_input('ストップワードの入力', placeholder='ここに読点「、」区切りで言葉を入力すると、それらを除外して解析します。')
                stop_words = stop_line.split('、')
                stop_words = [self.cor.preprocessing(word) for word in stop_words]

                if self.authority:
                    input_users = st.multiselect('ユーザー名でフィルター', self.users) 
                else:
                    input_users = [self.user]
                    
                submit_btn = st.form_submit_button('実行')

        if submit_btn:
            if not options:
                st.error("最低でも一つ以上の品詞を選択して下さい")
            
            else:
                try:
                    user_df = self.get_user_df(input_users)
                    target_corpus = user_df['words'].values.tolist()
                    self.cor.morphological_analysis(' '.join(target_corpus), options, stop_words)
                    
                    self.display_tabs()

                except ValueError:
                    st.warning('解析が実行されない場合は、まだ該当する言葉が書き込まれていません。')
                    st.info('''
                    主成分分析とクラスタリングの結果のみが表示されない場合は、該当する言葉のうち、
                    単語ベクトルを学習済みのものが二つ未満のため、処理をスキップしています。
                    ''')
            

cor = Corpus3(st.session_state)
page = Page3(st.session_state, cor)

page.check_login_status()
