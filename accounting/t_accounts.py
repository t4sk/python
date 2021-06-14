from lib import (
    csv_to_journal_entries,
    save_t_accounts_to_csv,
    filter_t_accounts_by_year,
    journal_entries_to_t_accounts,
    print_md
)

def print_entries(rows):
    s = [
        "| account | date | debit / credit | amount | memo | year |",
        "| :--- | :--- | :--- | ---: | :--- | --- |"
    ]
    for row in rows:
        s.append(row)
        #print(row)
    print_md(s)
    

def main(**kwargs):
    show_entries = kwargs.get("show_entries", True)
    year = kwargs.get("year", None)
    account = kwargs.get("account", "")
    journal_entries = csv_to_journal_entries(
       kwargs["journal_entries_csv"]
    )

    t_accounts = journal_entries_to_t_accounts(journal_entries)
    if year != None:
        t_accounts = filter_t_accounts_by_year(t_accounts, year=year)
    save_t_accounts_to_csv(t_accounts, year=year)
    
    for t_account in t_accounts:
        print(t_account.account)

    # filter by account
    if account != "":
        t_accounts = list(filter(lambda t_account: t_account.account == account, t_accounts)) 

    for t_account in t_accounts:
        diff = t_account.debit - t_account.credit
        print(f'=== {t_account.account} | {t_account.debit:,d} | {t_account.credit:,d} | {diff:,d} ===')

        if show_entries:
            rows = []
            for entry in t_account.entries:
                rows.append(str(entry))
            print_entries(rows)
