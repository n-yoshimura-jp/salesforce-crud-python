"""商談（Opportunity）の削除"""

from salesforce_crud.commands import delete

# 削除する商談の Id
RECORD_ID = ""

if __name__ == "__main__":
    delete("Opportunity", RECORD_ID)
