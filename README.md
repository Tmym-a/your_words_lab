# Your Words Lab
 「にっぽうであそぼ」というコンセプトで制作した、日報管理システムです。<br >
 スマートフォンからでもご利用いただけます。
<br >
<br >
## 利用手順
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://tmym-a-your-words-lab-start-y3niw8.streamlitapp.com/) <br >

1. 上のバッジをクリックすると、アプリが起動します

2. 下記どちらかの方法でログイン
   - ログイン画面で、ダミーアカウントのユーザー名とパスワードを使用してログイン
      - 標準ユーザーアカウント<br > ユーザー名「guest1」 パスワード「12345678」
      - 管理者アカウント<br >      ユーザー名「admin1」 パスワード「12344321」

   - 新規登録画面から、ゲストアカウントを作成してログイン（メールアドレス等の登録は不要です）
 
3. ステータスに応じて、以下に記載の機能をご利用いただけます
<br >

## 機能一覧
- ゲストアカウント作成、ログイン機能
- 投稿機能
  - 日報の書き込み
  - 書き込み内容をもとにした極性判定（感情分析）
- 閲覧機能
  - 自身の書き込み内容の閲覧
  - 全ユーザーの書き込み内容の閲覧（管理者アカウント限定）
- 解析機能
  - フィルターやストップワードの設定が可能
  - 解析結果をワードクラウドやグラフで視覚的に表示
- 検索機能
<br >

## 使用技術
- Python3
- SQLite3
- Streamlit
- Streamlit Cloud
- Git LFS

## 制作背景
　仕事をしていると毎日書くことになる日報ですが、基本的には書く方も読む方も、仕事上必要だからと事務的にこなしていることが多いと思います。つまり、多くの人にとって日報に触れている時間というのは、決して楽しい時間ではありません。それゆえに、優先したい仕事がある時などは、日報の作業をつい後回しにしたりしがちだと思います。<br >
 
　そこで、日報に関わる時間が少しでも楽しいものになるような、むしろ仕事中の小さな息抜きになるような、そんな日報管理システムがあったら使ってみたいかもしれないと思い、自分で制作することにしました。<br >

　とはいえ、面白さを求めてゲームのようなアプリにしてしまうと、仕事とは関係ない要素を多分に含んだ娯楽アプリになりかねないので、あくまでも日々の活動を記録・管理する日報としての機能をベースとして、表示の工夫により視覚的に楽しめるようなアプリを目指しました。その工夫の一つとして、普段使っている言葉にはその人の人間性が良く表れると思うので、形態素解析やWord2Vecを活用することでそれらの特徴を表現できるアプリに仕上げました。

## 備考
　IT系の仕事の経験がなくWEBアプリの開発自体初めてだったので、何もかもが手探りの状態ではありますが、今後も機能を追加して随時アップデートしていく予定です。<br >

　なお、感情分析については、自作の極性辞書を使用しているものの精度が良くないため、本格的にサービスとして運用するならGoogleの有料APIである Cloud Natural Language API などの利用を検討した方が良さそうです。
