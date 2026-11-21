"""オブジェクトで実行できる操作と、作成時の必須項目を表示する"""

import sys

from simple_salesforce.exceptions import SalesforceError, SalesforceResourceNotFound

from salesforce_crud.auth import get_client
from salesforce_crud.schema import describe_object, filter_required_fields

# 確認するオブジェクトの API 参照名
OBJECT_NAME = "Opportunity"

# 表示する操作（describe のキー: 表示名）
OPERATIONS = {
    "createable": "作成 (create)",
    "updateable": "更新 (update)",
    "deletable": "削除 (delete)",
    "undeletable": "削除の取り消し (undelete)",
    "queryable": "参照 (query)",
    "searchable": "検索 (search)",
}

if __name__ == "__main__":
    sf = get_client()
    try:
        result = describe_object(sf, OBJECT_NAME)
    except SalesforceResourceNotFound:
        sys.exit(f"オブジェクトが見つかりません: {OBJECT_NAME}")
    except SalesforceError as e:
        sys.exit(f"describe に失敗しました（HTTP {e.status}）: {e.content}")

    print(f"{result['name']}（{result['label']}）")

    print("\n■ 実行できる操作")
    for key, label in OPERATIONS.items():
        print(f"  {label:<28} {'○' if result[key] else '-'}")

    print("\n■ 作成時の必須項目")
    for field in filter_required_fields(result):
        reference_to = ", ".join(field["referenceTo"])
        print(f"  {field['name']:<30} {field['label']:<20} {field['type']:<12} {reference_to}")
