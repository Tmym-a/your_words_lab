import streamlit as st
import pandas as pd
import gensim
import pickle
import mojimoji
import unicodedata

with open('fastText.ja.300.vec.pkl',  mode = 'rb') as fp:
    model = pickle.load(fp)
    
# 前処理（単語の正規化）
def preprocessing(text):  
    result = mojimoji.zen_to_han(text, kana=False)
    result = mojimoji.han_to_zen(result, ascii=False)
    result = unicodedata.normalize('NFKC', result)
    return result


if 'user' not in st.session_state:
    st.info("ログイン後に利用可能です")

else:
    st.title('Your Words Laboratory')
    st.caption('解析結果などをもとに単語を入力し、普段使っている言葉と同じ方向性を持つ言葉や、真逆の方向性を持つ言葉を眺めて、自分の言葉に対する理解を深めましょう。')


    col1, col2 = st.columns(2)
    with col1:
        keyword = st.text_input('単語の入力')
    with col2:
        '##'
        button = st.button('調べる')
    '##'
    if button:
        keyword = preprocessing(keyword)
        if keyword in model.index_to_key:
            col1, col2 = st.columns(2)
            with col1:
                similar_df = pd.DataFrame(model.most_similar(positive=[keyword]))
                similar_df = similar_df.set_index(0)
                similar_df.columns = ['cos類似度']
                st.write('Similar words')
                st.table(similar_df)
            with col2:
                opposite_df = pd.DataFrame(model.most_similar(negative=[keyword])).iloc[::-1]
                opposite_df = opposite_df.set_index(0)
                opposite_df.columns = ['cos類似度']
                st.write('Opposite words')
                st.table(opposite_df)
        else:
            st.info('申し訳ありません。その単語は登録されていないため検索できません。')