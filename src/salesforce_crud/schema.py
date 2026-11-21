"""オブジェクト・項目の定義情報（describe）の取得"""

from simple_salesforce import Salesforce


def describe_object(sf: Salesforce, object_name: str) -> dict:
    """オブジェクトの定義情報（表示ラベル、実行できる操作、項目の一覧など）を返す。"""
    return getattr(sf, object_name).describe()


def filter_required_fields(describe_result: dict) -> list[dict]:
    """describe の結果から、作成時に値の指定が必要な項目だけを返す。

    作成可能・null 不可・作成時の既定値なし の項目を必須とみなす。
    入力規則による必須は含まれない。
    """
    return [
        field
        for field in describe_result["fields"]
        if field["createable"] and not field["nillable"] and not field["defaultedOnCreate"]
    ]


def get_required_fields(sf: Salesforce, object_name: str) -> tuple[str, list[dict]]:
    """オブジェクトの表示ラベルと、作成時に値の指定が必要な項目の一覧を返す。"""
    result = describe_object(sf, object_name)
    return result["label"], filter_required_fields(result)


def get_standard_objects(sf: Salesforce) -> list[dict]:
    """組織で利用可能な標準オブジェクト（カスタムオブジェクト以外）の一覧を返す。"""
    return [obj for obj in sf.describe()["sobjects"] if not obj["custom"]]
