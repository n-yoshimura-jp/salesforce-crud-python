"""組織で利用可能な標準オブジェクトの一覧を表示する"""

from salesforce_crud.auth import get_client
from salesforce_crud.schema import get_standard_objects

if __name__ == "__main__":
    sf = get_client()
    objects = get_standard_objects(sf)

    print(f"{'API参照名':<40} {'表示ラベル':<30} 検索 作成")
    for obj in objects:
        queryable = "○" if obj["queryable"] else "-"
        createable = "○" if obj["createable"] else "-"
        print(f"{obj['name']:<40} {obj['label']:<30} {queryable:<4} {createable}")
    print(f"\n合計: {len(objects)} 件")
