"""CSV を使った一括処理（Bulk API 2.0）

object_name にはオブジェクトの API 参照名（Account、Lead、Opportunity など）を指定する。
"""

import csv
from pathlib import Path

from simple_salesforce import Salesforce

# Bulk API 2.0 の 1 ジョブあたりのアップロード上限（100 MB）
MAX_UPLOAD_BYTES = 100 * 1024 * 1024


def read_csv(csv_path: str) -> list[dict]:
    """CSV を読み込み、1 行 1 件の dict のリストを返す（1 行目は API 参照名のヘッダー）。

    文字コードは UTF-8。先頭の BOM（Excel の「CSV UTF-8」形式）は取り除く。
    UTF-8 として不正なバイト列（Shift_JIS など）は UnicodeDecodeError になる。
    """
    path = Path(csv_path)
    size = path.stat().st_size
    if size > MAX_UPLOAD_BYTES:
        raise ValueError(f"CSV が 100 MB を超えています（{size} bytes）。ファイルを分割してください")

    # newline="": セル内の改行を正しく扱うため（csv モジュールの推奨）
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    if not records:
        raise ValueError(f"CSV にデータ行がありません: {csv_path}")
    for number, record in enumerate(records, start=1):
        # ヘッダーより列が多い行は、余った値が None キーに入る
        if None in record:
            raise ValueError(f"CSV の {number} 件目のデータの列数がヘッダーより多くなっています")
    return records


def run_bulk_job(sf: Salesforce, object_name: str, operation: str, records: list[dict]) -> list[dict]:
    """Bulk API 2.0 のジョブを実行し、完了まで待ってジョブごとの結果を返す。

    operation は "insert" / "update" / "delete" のいずれか。
    データが大きい場合はライブラリが複数のジョブに分割するため、結果はリストで返る。
    各要素のキー: job_id, numberRecordsProcessed（失敗を含む処理件数）, numberRecordsFailed, numberRecordsTotal
    """
    bulk_object = getattr(sf.bulk2, object_name)
    if operation == "insert":
        return bulk_object.insert(records=records)
    if operation == "update":
        return bulk_object.update(records=records)
    if operation == "delete":
        # delete の CSV は Id 列だけにする必要がある（それ以外はライブラリがエラーにする）
        return bulk_object.delete(records=records)
    raise ValueError(f"operation が不正です: {operation}")


def save_failed_records(sf: Salesforce, object_name: str, job_id: str, failed_path: str) -> None:
    """ジョブで失敗したレコード（sf__Id / sf__Error 列 + 元のデータ）を CSV に保存する。

    file を指定すると、Salesforce が返す UTF-8 のバイト列をそのまま保存する
    （file を省略して文字列で受け取ると、文字コードの判定を誤って日本語が文字化けする）。
    """
    getattr(sf.bulk2, object_name).get_failed_records(job_id, file=failed_path)
