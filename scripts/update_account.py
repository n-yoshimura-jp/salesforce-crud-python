"""取引先（Account）の更新"""

from salesforce_crud.commands import update

# 更新する取引先の Id
RECORD_ID = ""
# 更新する項目（API 参照名: 新しい値）
FIELDS = {"Name": "Renamed Account"}

if __name__ == "__main__":
    update("Account", RECORD_ID, FIELDS)
