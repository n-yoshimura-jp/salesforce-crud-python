"""scripts/ から呼び出す処理（結果の表示とエラー処理）"""

import sys
from pathlib import Path

from simple_salesforce.exceptions import (
    SalesforceError,
    SalesforceOperationError,
    SalesforceResourceNotFound,
)

from salesforce_crud import bulk, records
from salesforce_crud.auth import get_client


def create(object_name: str, fields: dict) -> None:
    sf = get_client()
    try:
        record_id = records.create_record(sf, object_name, fields)
    except SalesforceError as e:
        sys.exit(f"作成に失敗しました（HTTP {e.status}）: {e.content}")
    print(f"{object_name} を作成しました: Id={record_id}")


def _flatten(record: dict, prefix: str = "") -> dict:
    """関連先の項目（Account.Name など）の入れ子を「Account.Name」のキーに展開する。"""
    row = {}
    for key, value in record.items():
        if key == "attributes":  # レコードのメタ情報は表示しない
            continue
        if isinstance(value, dict):
            row.update(_flatten(value, f"{prefix}{key}."))
        else:
            row[f"{prefix}{key}"] = value
    return row


def query(soql: str) -> None:
    """SOQL を実行し、結果を 1 レコード 1 行で表示する。"""
    sf = get_client()
    try:
        rows = records.query_records(sf, soql)
    except SalesforceError as e:
        sys.exit(f"取得に失敗しました（HTTP {e.status}）: {e.content}")

    for row in rows:
        print("  ".join(f"{name}={value}" for name, value in _flatten(row).items()))
    print(f"件数: {len(rows)}")


def update(object_name: str, record_id: str, fields: dict) -> None:
    if not record_id:
        sys.exit("RECORD_ID を指定してください")

    sf = get_client()
    try:
        status = records.update_record(sf, object_name, record_id, fields)
    except SalesforceResourceNotFound:
        sys.exit(f"{object_name} が見つかりません: Id={record_id}")
    except SalesforceError as e:
        sys.exit(f"更新に失敗しました（HTTP {e.status}）: {e.content}")
    print(f"{object_name} を更新しました: Id={record_id}（HTTP {status}）")


def delete(object_name: str, record_id: str) -> None:
    if not record_id:
        sys.exit("RECORD_ID を指定してください")

    sf = get_client()
    try:
        status = records.delete_record(sf, object_name, record_id)
    except SalesforceResourceNotFound:
        sys.exit(f"{object_name} が見つかりません: Id={record_id}")
    except SalesforceError as e:
        sys.exit(f"削除に失敗しました（HTTP {e.status}）: {e.content}")
    print(f"{object_name} を削除しました: Id={record_id}（HTTP {status}）")


def _read_csv(csv_path: str) -> list[dict]:
    try:
        return bulk.read_csv(csv_path)
    except FileNotFoundError:
        sys.exit(f"CSV が見つかりません: {csv_path}")
    except UnicodeDecodeError:
        sys.exit(f"CSV を UTF-8 で読み込めません: {csv_path}（Excel では「CSV UTF-8 (コンマ区切り)」で保存してください）")
    except ValueError as e:
        sys.exit(str(e))


def _confirm(message: str) -> bool:
    """「yes」と入力されたときだけ True を返す。"""
    return input(f"{message} (yes/no): ").strip() == "yes"


def bulk_load(object_name: str, operation: str, csv_path: str) -> None:
    """CSV のレコードを Bulk API 2.0 で一括作成（insert）・更新（update）・削除（delete）する。

    失敗したレコードは「<元のファイル名>-failed-<ジョブ Id>.csv」に保存する。
    """
    rows = _read_csv(csv_path)
    columns = list(rows[0].keys())
    if operation == "update" and "Id" not in columns:
        sys.exit("一括更新の CSV には Id 列が必要です")
    if operation == "delete" and columns != ["Id"]:
        sys.exit("一括削除の CSV は Id 列だけにしてください")

    # 削除は取り消しにくいため、件数を表示して確認してから実行する
    if operation == "delete" and not _confirm(f"{object_name} を {len(rows)} 件削除します。よろしいですか？"):
        print("中止しました")
        return

    sf = get_client()
    print(f"{object_name} / {operation}: {len(rows)} 件を処理しています...")
    try:
        results = bulk.run_bulk_job(sf, object_name, operation, rows)
    except SalesforceError as e:
        sys.exit(f"一括処理に失敗しました（HTTP {e.status}）: {e.content}")
    except SalesforceOperationError as e:
        sys.exit(f"一括処理に失敗しました: {e}\n[設定] > [一括データ読み込みジョブ] でジョブを確認してください")

    processed = sum(r["numberRecordsProcessed"] for r in results)
    failed = sum(r["numberRecordsFailed"] for r in results)
    for r in results:
        print(f"ジョブ: {r['job_id']}")
    print(f"成功: {processed - failed} 件 / 失敗: {failed} 件")

    # 失敗したレコードはジョブごとに「<元のファイル名>-failed-<ジョブ Id>.csv」に保存する
    path = Path(csv_path)
    for r in results:
        if r["numberRecordsFailed"] > 0:
            failed_path = path.with_name(f"{path.stem}-failed-{r['job_id']}.csv")
            bulk.save_failed_records(sf, object_name, r["job_id"], str(failed_path))
            print(f"失敗したレコードを保存しました: {failed_path}")
