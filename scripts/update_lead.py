"""リード（Lead）の更新"""

from salesforce_crud.commands import update

# 更新するリードの Id
RECORD_ID = ""
# 更新する項目（API 参照名: 新しい値）
FIELDS = {"Company": "Renamed Company"}

if __name__ == "__main__":
    update("Lead", RECORD_ID, FIELDS)
