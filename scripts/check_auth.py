"""Salesforce への認証を確認する"""

from salesforce_crud.auth import get_client

if __name__ == "__main__":
    sf = get_client()
    print(f"認証に成功しました: {sf.sf_instance}")
