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


def generate_list(text, selected_parts):
    m = MeCab.Tagger()
    parts = m.parse(text)
    dic = defaultdict(int)
    wp_list = []
    wordlist = []

    for part in parts.split('\n')[:-1]:
        word_part = [part.split('\t')[0], part.split('\t')[4].split('-')[0]]
        p = word_part[1]

        if p in selected_parts:
            wp_list.append(word_part)
            wordlist.append(word_part[0])
            dic[tuple(word_part)] += 1

    merged_list = []

    for k, v in dic.items():
        merged_list.append([k[0], k[1], v])

    return merged_list, wordlist


if 'user' not in st.session_state:
    st.info("ログイン後に利用可能です")

else:
    user = st.session_state['user']

    st.title('Analysis of Your Words')
    st.write('形態素解析フォーム')

    with st.form(key='select_form'):
        options = st.multiselect("品詞の選択", all_parts, ['名詞','代名詞','形状詞','副詞','動詞','形容詞'])
        st.text('これまでの書き込み内容を形態素解析し、上記の品詞に該当する言葉を抽出します。')
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
                accumulation = user_df['words'].values.tolist()

                total_list, series = generate_list(' '.join(accumulation), options)
                full_text = ' '.join(series)
                df = pd.DataFrame(total_list)
                df.columns = ['表層形','品詞','度数']
                df = df.sort_values('度数', ascending=False)

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
                st.sidebar.write('使用頻度の高い言葉', df)
                st.sidebar.caption('※ 列名をクリックでソート可能')              

            except ValueError:
                st.warning('まだ、該当する言葉は書き込まれていません')
        