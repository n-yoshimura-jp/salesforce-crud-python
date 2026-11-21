"""商談（Opportunity）の作成"""

from salesforce_crud.commands import create

# 作成する商談の項目（API 参照名: 値）
FIELDS = {"Name": "Test Opportunity", "StageName": "Prospecting", "CloseDate": "2026-12-31"}

if __name__ == "__main__":
    create("Opportunity", FIELDS)
