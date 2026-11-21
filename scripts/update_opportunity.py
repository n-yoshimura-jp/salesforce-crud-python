"""商談（Opportunity）の更新"""

from salesforce_crud.commands import update

# 更新する商談の Id
RECORD_ID = ""
# 更新する項目（API 参照名: 新しい値）
FIELDS = {"StageName": "Qualification"}

if __name__ == "__main__":
    update("Opportunity", RECORD_ID, FIELDS)
