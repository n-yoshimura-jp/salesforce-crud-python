"""オブジェクト共通の CRUD 処理

object_name にはオブジェクトの API 参照名（Account、Lead、Opportunity など）を指定する。
"""

from simple_salesforce import Salesforce


def create_record(sf: Salesforce, object_name: str, fields: dict) -> str:
    """レコードを作成し、作成されたレコードの Id を返す。"""
    result = getattr(sf, object_name).create(fields)
    return result["id"]


def query_records(sf: Salesforce, soql: str) -> list[dict]:
    """SOQL を実行し、該当するレコードをすべて返す（2000 件を超える場合も続きを取得する）。

    soql に値を埋め込む場合は、f-string ではなく simple_salesforce.format_soql を使うこと。
    """
    return sf.query_all(soql)["records"]


def update_record(sf: Salesforce, object_name: str, record_id: str, fields: dict) -> int:
    """レコードを更新し、HTTP ステータスコードを返す（成功時は 204）。"""
    return getattr(sf, object_name).update(record_id, fields)


def delete_record(sf: Salesforce, object_name: str, record_id: str) -> int:
    """レコードを削除し、HTTP ステータスコードを返す（成功時は 204）。"""
    return getattr(sf, object_name).delete(record_id)
