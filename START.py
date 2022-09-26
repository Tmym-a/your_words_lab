import streamlit as st
import sqlite3 
import hashlib


conn = sqlite3.connect('database.db')
c = conn.cursor()

def hash(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
	if hash(password) == hashed_text:
		return hashed_text
	return False

def create_tables():
	query = '''
	CREATE TABLE 
	IF NOT EXISTS userstable(username TEXT NOT NULL PRIMARY KEY, password TEXT);
	'''
	c.execute(query)

	query = '''
	CREATE TABLE 
	IF NOT EXISTS reports(date TEXT, writer TEXT, words TEXT, feelings REAL, variables INTEGER, PRIMARY KEY(date, writer));
	'''
	c.execute(query)

def user_registration(username, password):
	query = 'INSERT INTO userstable(username, password) VALUES (?, ?);'
	c.execute(query, (username, password))
	conn.commit()

def login_user(username,password):
	query = '''
	SELECT * FROM userstable 
	WHERE username = ? AND password = ?;
	'''
	c.execute(query, (username, password))
	record = c.fetchall()
	return record

def start_menu():
	st.title('Who Writes?')

	menu = ['ログイン', '新規登録']
	choice = st.sidebar.radio('ログインメニュー', menu)

	if choice == 'ログイン':
		create_tables()
		st.subheader('ログイン画面です')
		username = st.text_input('ユーザー名を入力してください')
		password = st.text_input('パスワードを入力してください', type = 'password')

		if st.button('ログイン'):
			hashed = hash(password)
			result = login_user(username, check_hashes(password, hashed))

			if result:
				st.session_state['user'] = result[0][0]
				st.balloons()
				st.success('ようこそ！ {}さん'.format(st.session_state['user']))
				c.close()
	
			else:
				st.warning('ユーザー名かパスワードが間違っています')

	elif choice == '新規登録':
		st.subheader('新しいユーザーを登録します')
		new_user = st.text_input('ユーザー名を入力してください')
		new_password = st.text_input('パスワードを入力してください', type = 'password')

		if st.button('新規登録'):
			create_tables()
			try:
				user_registration(new_user,hash(new_password))
				st.success('アカウントの作成に成功しました')
				st.info('ログイン画面からログインしてください')

			except sqlite3.IntegrityError:
				st.warning('同じ名前のユーザーが存在します')


if __name__ == '__main__':
	if 'user' not in st.session_state:
		start_menu()
	else:
		st.success('ログイン済みです')
		st.sidebar.success('Select a page above.')
		if st.button('ログアウト'):
			del st.session_state['user']
			st.experimental_rerun()

# streamlit run START.py