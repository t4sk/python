from lib import (
    csv_to_journal_entries,
    t_accounts_to_csv,
    filter_t_accounts_by_year,
    journal_entries_to_t_accounts
)

def main(**kwargs):
    year = kwargs.get("year", None)
    journal_entries = csv_to_journal_entries(
       kwargs["journal_entries_csv"]
    )

    t_accounts = journal_entries_to_t_accounts(journal_entries)
    if year != None:
        t_accounts = filter_t_accounts_by_year(t_accounts, year=year)
    t_accounts_to_csv(t_accounts, year=year)

    for t_account in t_accounts:
        diff = t_account.debit - t_account.credit
        print(f'=== {t_account.account} | {t_account.debit:,d} | {t_account.credit:,d} | {diff:,d} ===')
        for entry in t_account.entries:
            print(entry)
