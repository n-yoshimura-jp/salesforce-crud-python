"""リード（Lead）の削除"""

from salesforce_crud.commands import delete

# 削除するリードの Id
RECORD_ID = ""

if __name__ == "__main__":
    delete("Lead", RECORD_ID)
