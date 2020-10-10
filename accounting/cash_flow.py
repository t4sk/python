# cash flow
from datetime import datetime
from lib import (
    csv_to_journal_entries, create_balance_sheet, print_balance_sheet,
    filter_journal_entries_by_date_range,
    journal_entries_to_t_accounts,
    date_to_str,
    get_months
)

DATE_FORMAT = "%Y/%m"

def date_to_month_str(date):
    return date.strftime(DATE_FORMAT)


def repeat(c, n):
    _c = ""
    for _ in range(n):
        _c += c
    return _c

def padd_left(s, n, c):
    return repeat(c, n - len(s)) + s

def print_num(num):
    return padd_left(f'{num:,d}', 15, " ")


def print_header():
    date = repeat(" ", 7)
    asset = padd_left("assets", 15, " ")
    liability = padd_left("liability", 15, " ")
    equity = padd_left("equitity", 15, " ")
    revenue = padd_left("revenue", 15, " ")
    expense = padd_left("expense", 15, " ")
    
    print(date, asset, liability, equity, revenue, expense)
    print(repeat("-", 7 + 75 + 5)) 



def main(**kwargs):
    year = kwargs["year"]
    journal_entries = csv_to_journal_entries(kwargs["journal_entries_csv"])

    months = get_months(year)
    balance_sheets = []
    
    for (start, end) in months:
        filtered = filter_journal_entries_by_date_range(
            journal_entries, start, end)
        t_accounts = journal_entries_to_t_accounts(filtered)
        balance_sheets.append(create_balance_sheet(t_accounts))
     
    # print summary
    print_header()
    for i in range(len(months)):
        (start, end) = months[i]
        bs = balance_sheets[i]
        
        print(
            date_to_month_str(start),
            print_num(bs.total_assets),
            print_num(bs.total_liabilities),
            print_num(bs.total_equities),
            print_num(bs.total_revenues),
            print_num(bs.total_expenses)
        )
     
    # print detail
    print()
    for i in range(len(months)):
        (start, end) = months[i]
        bs = balance_sheets[i]    

        print(f'=== {date_to_str(start)} - {date_to_str(end)} ===')
        print_balance_sheet(bs)
        print("\n")
