"""商談（Opportunity）の取得"""

from salesforce_crud.commands import query

# 実行する SOQL
# - 必要な項目だけを SELECT し、LIMIT で件数を絞る（個人情報の取得は最小限にする）
# - 値を埋め込む場合は f-string ではなく format_soql を使う（SOQL インジェクション対策）
#     from simple_salesforce import format_soql
#     SOQL = format_soql("SELECT Id, Name FROM Opportunity WHERE Id = {}", record_id)
SOQL = "SELECT Id, Name, StageName, CloseDate, Account.Name FROM Opportunity ORDER BY CreatedDate DESC LIMIT 10"

if __name__ == "__main__":
    query(SOQL)
