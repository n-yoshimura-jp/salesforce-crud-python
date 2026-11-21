"""取引先（Account）の作成"""

from salesforce_crud.commands import create

# 作成する取引先の項目（API 参照名: 値）
FIELDS = {"Name": "Test Account"}

if __name__ == "__main__":
    create("Account", FIELDS)
