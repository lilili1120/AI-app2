# Pythonの公式イメージを使用
FROM python:3.11

# 作業ディレクトリを設定
WORKDIR /app

# 必要なファイルをコピー
COPY requirements.txt requirements.txt
COPY app.py app.py

# ライブラリをインストール
RUN pip install -r requirements.txt

# アプリを起動
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
