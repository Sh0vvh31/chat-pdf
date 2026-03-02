FROM python:3.11-slim

WORKDIR /app

# 環境変数の設定 (Python)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 依存パッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ソースコードのコピー (開発時は volume マウントで上書きされる)
COPY . /app/

# コンテナ起動時に FastAPI (uvicorn) もしくは テスト を実行できるように
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
