from lib import (
    csv_to_journal_entries,
    group_journal_entries_by_account,
    t_accounts_to_csv,
    journal_entries_to_t_accounts
)

def main(**kwargs):
    journal_entries = csv_to_journal_entries(
       kwargs["journal_entries_csv"]
    )

    t_accounts = group_journal_entries_by_account(journal_entries)
    t_accounts_to_csv(t_accounts)

    t_accounts = journal_entries_to_t_accounts(journal_entries)

    for t_account in t_accounts:
        print(f'=== {t_account.account} ===')
        for entry in t_account.entries:
            print(entry)
