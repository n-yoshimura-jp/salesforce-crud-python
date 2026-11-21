"""取引先（Account）の削除"""

from salesforce_crud.commands import delete

# 削除する取引先の Id
RECORD_ID = ""

if __name__ == "__main__":
    delete("Account", RECORD_ID)
