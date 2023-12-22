import streamlit as st
import pandas as pd

# Streamlitアプリのタイトル
# st.title('検索履歴表示アプリ')

# 検索履歴をセッションステートに保存する関数
def save_search_history(query):
    if 'search_history' not in st.session_state:
        st.session_state.search_history = pd.DataFrame(columns=['Search Query'])
    new_entry = {'Search Query': query}
    st.session_state.search_history = st.session_state.search_history.append(new_entry, ignore_index=True)

# ユーザーがクエリを入力するテキストボックス
# query = st.text_input('検索クエリを入力してください')

# 検索ボタン
# if st.button('検索'):
#     save_search_history(query)

# 検索履歴を表示
if 'search_history' in st.session_state:
    st.set_page_config(layout="wide")
    st.write('検索履歴:')
    st.dataframe(st.session_state.search_history)
