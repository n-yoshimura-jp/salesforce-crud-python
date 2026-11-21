"""CSV からレコードを一括作成する（Bulk API 2.0）"""

from salesforce_crud.commands import bulk_load

# 作成先のオブジェクト（API 参照名: Account / Contact / Lead など）
OBJECT_NAME = "Lead"
# 読み込む CSV（1 行目は API 参照名のヘッダー、文字コードは UTF-8）
CSV_PATH = "data/leads.csv"

if __name__ == "__main__":
    bulk_load(OBJECT_NAME, "insert", CSV_PATH)
