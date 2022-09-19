import streamlit as st
import sqlite3
import pandas as pd
import time
import MeCab
from wordcloud import WordCloud
from collections import defaultdict
from PIL import Image


fpath = './IPAfont00303/ipam.ttf'
all_parts = ['名詞','代名詞','形状詞','連体詞','副詞','接続詞','感動詞',
            '動詞','形容詞','助動詞','助詞','接頭辞','接尾辞','記号',]


def morphological_analysis(text, selected_parts, stop_words):
    tagger = MeCab.Tagger()
    node = tagger.parseToNode(text)
    dic = defaultdict(int)
    morpheme_words = []

    while  node:
        if node.feature.startswith('BOS/EOS') or node.surface in stop_words:
            pass
        else:
            f = node.feature.split(',')
            surface = node.surface
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


if 'user' not in st.session_state:
    st.info("ログイン後に利用可能です")

else:
    user = st.session_state['user']

    st.title('Analysis of Your Words')
    st.write('形態素解析フォーム')

    with st.form(key='select_form'):
        options = st.multiselect('品詞の選択', all_parts, ['名詞','代名詞','形状詞','副詞','動詞','形容詞'])
        st.text('これまでの書き込み内容を形態素解析し、上記の品詞に該当する言葉を抽出します。')
        stop_line = st.text_area('ストップワードの入力', placeholder='ここに言葉を読点「、」区切りでいくつか入力すると、それらを除外して解析します。')
        stop_words = stop_line.split('、')
        submit_btn = st.form_submit_button('実行')

    if submit_btn:
        if not options:
            st.error("最低でも一つ以上の品詞を選択して下さい")
        else:
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
                # series = [_[0][0] for _ in items]
                full_text = ' '.join(series)
                df = pd.DataFrame(total_list)
                df.columns = ['表層形','品詞','度数']
                # df = df.sort_values('度数', ascending=False)

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
                st.caption('※ 形状詞とは、UniDicの品詞体系で、形容動詞語幹を意味しています。')

                st.sidebar.header('Below is a DataFrame:')
                st.sidebar.write('使用頻度の高い言葉', df.head(100))
                st.sidebar.caption('※ 列名をクリックでソート可能')              

            except ValueError:
                st.warning('まだ、該当する言葉は書き込まれていません')
        