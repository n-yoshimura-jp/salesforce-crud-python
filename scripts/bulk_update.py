"""CSV からレコードを一括更新する（Bulk API 2.0）"""

from salesforce_crud.commands import bulk_load

# 更新するオブジェクト（API 参照名）
OBJECT_NAME = "Lead"
# 読み込む CSV（Id 列と、更新する項目の列。文字コードは UTF-8）
# - CSV にない項目は変更されない。空欄のセルも変更されない（値を消すときは #N/A と書く）
CSV_PATH = "data/leads-update.csv"

if __name__ == "__main__":
    bulk_load(OBJECT_NAME, "update", CSV_PATH)
