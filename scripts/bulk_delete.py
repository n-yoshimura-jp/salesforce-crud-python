"""CSV のレコードを一括削除する（Bulk API 2.0）

実行前に件数を表示し、yes と入力したときだけ削除する。
削除したレコードはごみ箱に移動する（15 日以内ならごみ箱から復元できる）。
"""

from salesforce_crud.commands import bulk_load

# 削除するオブジェクト（API 参照名）
OBJECT_NAME = "Lead"
# 読み込む CSV（Id 列だけ。文字コードは UTF-8）
CSV_PATH = "data/leads-delete.csv"

if __name__ == "__main__":
    bulk_load(OBJECT_NAME, "delete", CSV_PATH)
