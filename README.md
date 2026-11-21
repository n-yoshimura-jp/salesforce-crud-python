# salesforce-crud-python

Python から Salesforce のレコード（取引先・リード・商談）を作成・取得・更新・削除（CRUD）するスクリプト集です。
CSV を使った一括作成・更新・削除（Bulk API 2.0）にも対応しています。
ライブラリは [simple-salesforce](https://github.com/simple-salesforce/simple-salesforce)、認証は OAuth 2.0 Client Credentials Flow を使います。

## 動作環境

| 項目 | バージョン |
|---|---|
| Python | 3.13 以上（`.python-version` で 3.13 を指定） |
| [uv](https://docs.astral.sh/uv/)（推奨）または pip | パッケージ管理・実行に使用 |
| simple-salesforce | 1.12.11 以上 |
| python-dotenv | 1.2.4 以上 |

## ディレクトリ構成

```
salesforce-crud-python/
├── src/salesforce_crud/        # 共通処理（パッケージ）
│   ├── auth.py                 # 認証（.env の読み込み）
│   ├── records.py              # オブジェクト共通の CRUD 関数
│   ├── schema.py               # 必須項目・オブジェクト一覧の取得
│   ├── bulk.py                 # CSV の一括処理（Bulk API 2.0）
│   └── commands.py             # scripts/ から呼ぶ処理（表示・エラー処理）
├── scripts/                    # 実行用スクリプト
├── samples/                    # 一括処理用のサンプル CSV（ダミーデータ）
├── data/                       # 一括処理に使う実際の CSV（Git 管理外）
├── docs/standard_objects.txt   # 公式の標準オブジェクト一覧へのリンク
├── .env.example                # .env のテンプレート
├── pyproject.toml              # プロジェクト設定・依存パッケージ
├── uv.lock                     # 依存パッケージのバージョン固定（uv 用）
├── requirements.txt            # 依存パッケージのバージョン固定（pip 用。uv.lock から生成）
└── LICENSE                     # MIT License
```

## セットアップ

### 1. リポジトリの取得

```sh
git clone https://github.com/n-yoshimura-jp/salesforce-crud-python.git
cd salesforce-crud-python
```

### 2. Salesforce 側の設定

1. 設定 → External Client App（または Connected App）を作成し、OAuth を有効にする。
   - OAuth スコープは `api` のみ（最小権限）。
2. 「Client Credentials Flow を有効化」をオンにし、**実行ユーザー（Run As）** を設定する。
   - API でのレコード操作はこのユーザーの権限で行われるため、必要な権限だけを持つ連携用ユーザーを推奨。
3. Consumer Key / Consumer Secret を控える。

### 3. 依存パッケージのインストール

**uv の場合（推奨）**

```sh
uv sync
```

**pip の場合**

```sh
python3.13 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install --require-hashes -r requirements.txt
pip install --no-deps -e .             # src/salesforce_crud をインポートできるようにする
```

- `requirements.txt` には各パッケージのハッシュ値が記載されており、`--require-hashes` で改ざんされたパッケージのインストールを防ぎます。

### 4. `.env` の設定

テンプレートをコピーして、値を記入します。

```sh
cp .env.example .env
```

| 変数 | 内容 |
|---|---|
| `SF_CONSUMER_KEY` | Consumer Key |
| `SF_CONSUMER_SECRET` | Consumer Secret |
| `SF_DOMAIN` | My Domain の前半部分（`https://mycompany.my.salesforce.com` なら `mycompany.my`） |

- `SF_DOMAIN` に `login` / `test` は使えません（Client Credentials Flow では My Domain が必須）。
- シェルに同名の環境変数があっても `.env` の値が優先されます。

### 5. 認証の確認

```sh
uv run python scripts/check_auth.py
# => 認証に成功しました: mycompany.my.salesforce.com
```

## 使い方

すべてプロジェクト直下で `uv run python scripts/<スクリプト名>` の形で実行します。
pip でインストールした場合は、venv を有効にしてから `python scripts/<スクリプト名>` で実行します。
操作する値は、各スクリプト冒頭の変数を書き換えて指定します。

`create_*`・`update_*`・`delete_*`・`bulk_*` は組織のデータを変更します。`get_*`・`describe_object`・`list_*`・`check_auth` は読み取りだけです。

### CRUD スクリプト

| 操作 | 取引先（Account） | リード（Lead） | 商談（Opportunity） | 変数 |
|---|---|---|---|---|
| 作成 | `create_account.py` | `create_lead.py` | `create_opportunity.py` | `FIELDS`（項目と値） |
| 取得 | `get_account.py` | `get_lead.py` | `get_opportunity.py` | `SOQL`（実行する SOQL） |
| 更新 | `update_account.py` | `update_lead.py` | `update_opportunity.py` | `RECORD_ID`、`FIELDS`（更新する項目と値） |
| 削除 | `delete_account.py` | `delete_lead.py` | `delete_opportunity.py` | `RECORD_ID` |

例: 商談を作成して更新・削除する

```sh
uv run python scripts/create_opportunity.py
# => Opportunity を作成しました: Id=006xxxxxxxxxxxxxxx

# update_opportunity.py / delete_opportunity.py の RECORD_ID に上の Id を記入してから実行
uv run python scripts/update_opportunity.py
uv run python scripts/delete_opportunity.py
```

`FIELDS` の書き方（API 参照名: 値。日付は `YYYY-MM-DD`、選択リストは API 値）:

```python
FIELDS = {"Name": "Test Opportunity", "StageName": "Prospecting", "CloseDate": "2026-12-31"}
```

### 取得（SOQL）の書き方

`get_*.py` の `SOQL` に実行する SOQL を書きます。結果は 1 レコード 1 行で表示され、関連先の項目は `Account.Name=...` の形で表示されます。2000 件を超える場合も続きを自動で取得します。

```python
SOQL = "SELECT Id, Name, StageName, CloseDate, Account.Name FROM Opportunity ORDER BY CreatedDate DESC LIMIT 10"
```

**セキュリティ上の注意**

- **値を埋め込むときは `format_soql` を使う。** f-string で直接埋め込むと、`'` を含む値で条件を書き換えられる（SOQL インジェクション）。`format_soql` は値をエスケープする。

  ```python
  from simple_salesforce import format_soql

  SOQL = format_soql("SELECT Id, Name FROM Lead WHERE Company = {}", company)
  ```

- **オブジェクト名・項目名は `format_soql` でもエスケープされない。** 外部から受け取る場合は、許可したリストに含まれるか確認する。`{:literal}` 指定はエスケープを無効にするため、外部からの値には使わない。
- **必要な項目だけを SELECT し、`LIMIT` で件数を絞る。** リードの `Email` / `Phone` などの個人情報は必要なときだけ取得し、出力を保存したファイルはコミット・共有しない。
- 取得できる範囲は、Client Credentials の**実行ユーザーの権限**（オブジェクト権限・項目レベルセキュリティ・共有設定）で決まる。実行ユーザーには必要最小限の権限だけを付与する。

### CSV から一括作成・更新・削除（Bulk API 2.0）

| 操作 | スクリプト | CSV の列 | 例 |
|---|---|---|---|
| 一括作成 | `bulk_create.py` | 作成する項目 | `data/leads.csv` |
| 一括更新 | `bulk_update.py` | `Id` ＋ 変更する項目 | `data/leads-update.csv` |
| 一括削除 | `bulk_delete.py` | `Id` だけ | `data/leads-delete.csv` |

1. `data/` フォルダを作り、`samples/` のサンプル CSV をコピーして編集します（`data/` は Git 管理外です）。

   ```sh
   mkdir -p data
   cp samples/*.csv data/
   ```

2. スクリプト冒頭の `OBJECT_NAME`（例: `"Lead"`）と `CSV_PATH` を書き換えて実行します。
   - 一括更新・一括削除の `Id` は、`get_lead.py` などで確認した実際の Id に書き換えてください（サンプルの `00Qxxxxxxxxxxxxxxx` はダミーです）。

```sh
uv run python scripts/bulk_create.py
# => Lead / insert: 2 件を処理しています...
#    ジョブ: 750xxxxxxxxxxxxxxx
#    成功: 2 件 / 失敗: 0 件
```

- CSV の 1 行目（ヘッダー）は項目の API 参照名にします。文字コードは UTF-8（Excel では「CSV UTF-8 (コンマ区切り)」で保存）。
- 失敗した行は、エラー内容（`sf__Error` 列）付きで `data/<元のファイル名>-failed-<ジョブ Id>.csv` に保存されます。
- 一括更新では、空欄のセルは変更されません。値を消したいときは `#N/A` と書きます。
- 一括削除は、実行前に件数を表示して確認します。`yes` と入力したときだけ削除します（ごみ箱に移動し、15 日以内なら復元可能）。
- 1 ファイルの上限は 100 MB です。超える場合はファイルを分割してください。
- `data/` と、`samples/` 以外の `*.csv` は、個人情報を含む可能性があるため `.gitignore` で除外しています。`samples/` には実データを置かないでください。

### 操作・必須項目・オブジェクト一覧の確認

| スクリプト | 内容 | 変数 |
|---|---|---|
| `describe_object.py` | 指定したオブジェクトで実行できる操作（作成・更新・削除など）と必須項目を表示 | `OBJECT_NAME` |
| `list_required_fields.py` | 指定したオブジェクトの必須項目を表示（複数指定可） | `OBJECT_NAMES` |
| `list_standard_objects.py` | 組織で利用可能な標準オブジェクトの一覧を表示 | なし |

- 必須項目 = 作成可能・null 不可・作成時の既定値なしの項目です。**入力規則やページレイアウトによる必須は含まれません。**
- 一覧をファイルに残す場合: `uv run python scripts/list_standard_objects.py > objects.txt`

## オブジェクトを追加する

1. `list_required_fields.py` の `OBJECT_NAMES` に追加して実行し、必須項目を確認する。
2. `scripts/` の既存ファイル（例: `create_lead.py`）をコピーし、オブジェクト名と変数を書き換える。

```python
# scripts/create_contact.py
"""取引先責任者（Contact）の作成"""

from salesforce_crud.commands import create

FIELDS = {"LastName": "Test"}

if __name__ == "__main__":
    create("Contact", FIELDS)
```

CRUD の処理本体（`src/salesforce_crud/records.py`）は全オブジェクト共通のため、変更不要です。

## トラブルシューティング

| メッセージ | 対処 |
|---|---|
| `環境変数が設定されていません: ...` | `.env` に表示された変数を記入する |
| `SF_DOMAIN には My Domain ... を指定してください` | `SF_DOMAIN` を `mycompany.my` の形式にする |
| `認証に失敗しました: ...` | Consumer Key / Secret、Client Credentials Flow の有効化、実行ユーザーの設定を確認する |
| `RECORD_ID を指定してください` | スクリプト冒頭の `RECORD_ID` に Id を記入する |
| `... が見つかりません: Id=...` | Id が正しいか、削除済みでないか、実行ユーザーに参照権限があるかを確認する |
| `取得に失敗しました（HTTP 400）: ...INVALID_FIELD...` / `...MALFORMED_QUERY...` | SOQL の項目名・構文を確認する（カスタム項目は末尾に `__c`） |
| `作成に失敗しました（HTTP 400）: ...REQUIRED_FIELD_MISSING...` | 必須項目が不足している。`list_required_fields.py` で確認する |
| `...FIELD_CUSTOM_VALIDATION_EXCEPTION...` | 入力規則に違反している。設定 → オブジェクトマネージャー → 入力規則 を確認する |
| `CSV を UTF-8 で読み込めません: ...` | CSV を UTF-8 で保存し直す（Shift_JIS は不可） |
| `一括処理に失敗しました: ...` | 設定 → 一括データ読み込みジョブ でジョブの状態とエラーを確認する |

## 依存パッケージの更新（開発者向け）

依存パッケージは `pyproject.toml` と `uv.lock` で管理しています。変更したら `requirements.txt` も生成し直してください。

```sh
uv add <パッケージ名>       # 追加（uv lock --upgrade で全体を更新）
uv export --format requirements-txt --no-emit-project --no-dev -o requirements.txt
```

## セキュリティ上の注意

- `.env` は `.gitignore` 済みです。コミット・共有しないでください。
- Consumer Secret が漏洩した可能性がある場合は、Salesforce 側で直ちにシークレットを再生成（ローテーション）してください。
- 動作確認は本番組織ではなく、Developer Edition や Sandbox で行ってください。
- `.gitignore` で除外しているもの: `.env` / `.env.*`（`.env.example` を除く）、`data/`、`samples/` 以外の `*.csv`、`.venv/`、`__pycache__/`、`.DS_Store` など。
- コミット前に `git status` で、`.env` や実データの CSV が含まれていないことを確認してください。

## 参考リンク

- [simple-salesforce](https://github.com/simple-salesforce/simple-salesforce)
- [Salesforce Standard Objects](https://developer.salesforce.com/docs/platform/object-reference/references/standard-objects/sforce-api-objects-list.html)
- [TypeScript 版（salesforce-crud-typescript）](https://github.com/n-yoshimura-jp/salesforce-crud-typescript)

## ライセンス

[MIT License](LICENSE)

このコードは無保証です。本番環境の Salesforce 組織で使う前に、Developer Edition や Sandbox で動作を確認してください。
