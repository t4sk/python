# cash flow
from datetime import datetime
from lib import (
    csv_to_journal_entries, create_balance_sheet, print_balance_sheet,
    filter_journal_entries_by_date_range,
    journal_entries_to_t_accounts,
    date_to_str,
    get_months
)

year = datetime.now().year
journal_entries = csv_to_journal_entries(
    "/home/t4sk/Downloads/accounting-2020.csv"
)

months = get_months(year)

for (start, end) in months:
    filtered = filter_journal_entries_by_date_range(
        journal_entries, start, end)
    t_accounts = journal_entries_to_t_accounts(filtered)
    bs = create_balance_sheet(t_accounts)

    print(f'=== {date_to_str(start)} - {date_to_str(end)} ===')
    print_balance_sheet(bs)
    print("\n")
