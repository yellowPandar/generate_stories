# generate_stories
chatGPTを用いて物語を生成する

## 機能
* UIからキーワードを入力する
* そのキーワードを元にChatGPTで300字以内の物語を作成する
* 同時に、キーワードからDream Studioを用いて挿絵を作成する

## 使用するツール
* ChatGPT4(物語作成と挿絵生成するためのプロンプト作成に使用)
* Dream Studio(画像AI.挿絵生成)
* streamlit(PythonでWebアプリケーションを作成)

## 使い方
1. Google Colaboratory で、物語作成.ipynbを開く
2. ChatGPTのAPIキーを作成する
3. Dream StudioのAPIキーを作成する
4. 物語作成.ipynbを実行する
5. 物語作成.ipynbで生成したURLにアクセスする
6. UIからキーワードを入力する
7. 実行結果（おはなしと挿絵）が出力される


## 実行結果
* 生成結果の例
![「嵐の日のうさぎ」で物語生成した結果](./アウトプット例.png)
