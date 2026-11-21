"""Salesforce への認証（OAuth 2.0 Client Credentials Flow）"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceAuthenticationFailed

# プロジェクト直下の .env（このファイルは src/salesforce_crud/ にある）
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
REQUIRED_VARS = ("SF_CONSUMER_KEY", "SF_CONSUMER_SECRET", "SF_DOMAIN")


def get_client() -> Salesforce:
    """.env の設定を読み込み、認証済みの Salesforce クライアントを返す。"""
    # override=True: シェルに同名の環境変数があっても .env の値を優先する
    load_dotenv(ENV_FILE, override=True)

    missing = [name for name in REQUIRED_VARS if not os.environ.get(name)]
    if missing:
        sys.exit(f"環境変数が設定されていません: {', '.join(missing)}（.env を確認してください）")

    # Client Credentials Flow では login / test は使えず、My Domain の指定が必須
    if os.environ["SF_DOMAIN"] in ("login", "test"):
        sys.exit("SF_DOMAIN には My Domain（例: mycompany.my）を指定してください")

    try:
        return Salesforce(
            consumer_key=os.environ["SF_CONSUMER_KEY"],
            consumer_secret=os.environ["SF_CONSUMER_SECRET"],
            domain=os.environ["SF_DOMAIN"],
        )
    except SalesforceAuthenticationFailed as e:
        sys.exit(f"認証に失敗しました: {e}")
