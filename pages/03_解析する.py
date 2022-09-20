import streamlit as st
import sqlite3
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
import pickle
import gensim
import mojimoji
import unicodedata



fpath = './IPAfont00303/ipam.ttf'
all_parts = ['名詞','代名詞','形状詞','連体詞','副詞','接続詞','感動詞',
            '動詞','形容詞','助動詞','助詞','接頭辞','接尾辞','記号','補助記号']

# 前処理（単語の正規化）
def preprocessing(text):  
    result = mojimoji.zen_to_han(text, kana=False)
    result = mojimoji.han_to_zen(result, ascii=False)
    result = unicodedata.normalize('NFKC', result)
    return result


def morphological_analysis(text, selected_parts, stop_words):
    tagger = MeCab.Tagger()
    node = tagger.parseToNode(text)
    dic = defaultdict(int)
    morpheme_words = []

    while  node:
        surface = node.surface
        surface = preprocessing(surface)

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

    return merged_list, morpheme_words, sorted_items


def show_results(user, options, stop_words):
    comment = st.empty()
    comment.text('Start!')
    latest_iteration = st.empty()
    bar = st.progress(0)

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    query = 'SELECT writer, words FROM diary ;'
    df = pd.read_sql(query, con = conn)
    c.close()

    try:
        user_df = df[df['writer']==user]
        corpus = user_df['words'].values.tolist()

        total_list, series, items = morphological_analysis(' '.join(corpus), options, stop_words)
        full_text = ' '.join(series)
        df = pd.DataFrame(total_list)
        df.columns = ['表層形','品詞','度数']
        # df = df.sort_values('度数', ascending=False)
        keys = [_[0][0] for _ in items]
        values = [_[1] for _ in items[:10]]
        

        wc = WordCloud(background_color='white', width=960, height=640, font_path=fpath)
        wc.generate(full_text)
        wc.to_file('wc.png')

        for i in range(100):
            latest_iteration.text(f'{i+1}% Complete')
            bar.progress(i + 1)
            time.sleep(0.005)
        comment.text('Done!')

        st.subheader('解析結果')
        img = Image.open('wc.png')
        st.image(img, caption='あなたの日記の内容から作成されたワードクラウド', use_column_width=True)
        st.write('')

        fig, ax = plt.subplots()
        ax.bar(keys[:10], values)
        fig.suptitle('出現頻度 TOP10')
        st.pyplot(fig)
        st.write('')

        st.sidebar.header('Below is a DataFrame:')
        st.sidebar.write('該当ワード一覧', df)
        st.sidebar.caption('※ 列名をクリックでソート可能')    


        with open('fastText.ja.300.vec.pkl',  mode = 'rb') as fp:
            model = pickle.load(fp)

        # vectors = [model[key] for key in keys]
        vectors = []
        keys_in_model = []

        for key in keys:
            if key in model.index_to_key:
                vectors.append(model[key])
                keys_in_model.append(key)

        model2d = PCA(n_components=2, whiten=True)
        model2d.fit(np.array(vectors[:30]).T)

        fig, ax = plt.subplots()
        ax.scatter(model2d.components_[0],model2d.components_[1])
        for (x,y), name in zip(model2d.components_.T, keys_in_model[:30]):
            ax.annotate(name, (x,y))
        fig.suptitle('単語ベクトルの分布（上位３０単語まで）')
        st.pyplot(fig)
        st.caption('※ 可視化のため、ベクトル空間を300次元から2次元に次元削減しています')  
        st.write('')

        # n_clusters = len(keys_in_model) // 10 + 1
        n_clusters = int(np.sqrt(len(keys_in_model))) + 1
        kmeans_model = KMeans(n_clusters=n_clusters, verbose=1, random_state=0) 
        kmeans_model.fit(vectors)

        cluster_labels = kmeans_model.labels_
        cluster_to_words = defaultdict(list)
        for cluster_id, word in zip(cluster_labels, keys_in_model):
            cluster_to_words[cluster_id].append(word)

        st.write('')
        st.subheader('似ている言葉のグループ')

        for i, words in enumerate(cluster_to_words.values()):
            cluster_df = pd.DataFrame(words).T
            cluster_df.index = [f'cluster {i}']
            # st.write(f'cluster{i}')
            st.write(cluster_df)
        #     st.table(words)
        # cluster_df = cluster_to_words.values()
        # st.dataframe(cluster_df)
                 

    except ValueError:
        st.warning('解析が実行されない場合は、まだ該当する言葉が書き込まれていません。')
        st.info('''
        出現頻度の棒グラフまでしか表示されない場合は、該当する言葉のうち、単語ベクトルを学習
        済みのものが一つ以下のため、主成分分析やクラスタリングを実行できていません。
        ''')
    


if 'user' not in st.session_state:
    st.info("ログイン後に利用可能です")

else:
    user = st.session_state['user']

    st.title('Analysis of Your Words')
    st.write('形態素解析フォーム')

    with st.form(key='select_form'):
        options = st.multiselect('品詞の選択', all_parts, ['名詞'])
        st.caption('※ 形状詞とは、UniDicの品詞体系で、形容動詞語幹を意味しています。')
        st.text('これまでの書き込み内容を形態素解析し、上記の品詞に該当する言葉を抽出します。')
        st.write('')

        stop_line = st.text_area('ストップワードの入力', placeholder='ここに言葉を読点「、」区切りでいくつか入力すると、それらを除外して解析します。')
        stop_words = stop_line.split('、')
        stop_words = [preprocessing(word) for word in stop_words]
        submit_btn = st.form_submit_button('実行')

    if submit_btn:
        if not options:
            st.error("最低でも一つ以上の品詞を選択して下さい")
        else:
            show_results(user, options, stop_words)
