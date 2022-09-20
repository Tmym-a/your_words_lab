import streamlit as st
import pandas as pd
import gensim
import pickle
import mojimoji
import unicodedata

# 前処理（単語の正規化）
def preprocessing(text):  
    result = mojimoji.zen_to_han(text, kana=False)
    result = mojimoji.han_to_zen(result, ascii=False)
    result = unicodedata.normalize('NFKC', result)
    return result

if 'user' not in st.session_state:
    st.info("ログイン後に利用可能です")

else:
    with open('fastText.ja.300.vec.pkl',  mode = 'rb') as fp:
        model = pickle.load(fp)

    df = pd.DataFrame(model.most_similar(positive=[u'猫']))
    st.write(df)