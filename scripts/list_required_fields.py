"""オブジェクトの必須項目（作成時に値の指定が必要な項目）を表示する"""

import sys

from simple_salesforce.exceptions import SalesforceError, SalesforceResourceNotFound

from salesforce_crud.auth import get_client
from salesforce_crud.schema import get_required_fields

# 確認するオブジェクトの API 参照名（取引先: Account、商談: Opportunity、リード: Lead など）
OBJECT_NAMES = ["Account", "Opportunity", "Lead"]

if __name__ == "__main__":
    sf = get_client()
    for object_name in OBJECT_NAMES:
        try:
            label, fields = get_required_fields(sf, object_name)
        except SalesforceResourceNotFound:
            print(f"[{object_name}] オブジェクトが見つかりません", file=sys.stderr)
            continue
        except SalesforceError as e:
            sys.exit(f"[{object_name}] describe に失敗しました（HTTP {e.status}）: {e.content}")

        print(f"=== {object_name}（{label}）の必須項目 ===")
        for field in fields:
            print(f"  {field['name']:<30} {field['label']:<20} {field['type']}")
        print()
