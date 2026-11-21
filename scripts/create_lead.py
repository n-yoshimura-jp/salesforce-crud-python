"""リード（Lead）の作成"""

from salesforce_crud.commands import create

# 作成するリードの項目（API 参照名: 値）
FIELDS = {"LastName": "Test", "Company": "Test Company"}

if __name__ == "__main__":
    create("Lead", FIELDS)
