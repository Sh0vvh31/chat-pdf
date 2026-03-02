FROM python:3.11-slim

WORKDIR /app

# 環境変数の設定
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 依存パッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ソースコードのコピー
COPY . /app/

# Streamlitのデフォルトポート
EXPOSE 8501

# 実行コマンド (Windows Docker環境でのWebSocket切断対策としてファイルウォッチャーを切る)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableWebsocketCompression=false", "--server.fileWatcherType=none"]
