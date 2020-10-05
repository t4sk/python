# coding: utf-8

# 貸借対照表
from lib import csv_to_t_accounts, get_accounts, create_balance_sheet, check_balance_sheet, print_balance_sheet

t_accounts = csv_to_t_accounts("t-accounts.csv")
accounts = get_accounts(t_accounts)

for account in accounts:
    print(account)

balance_sheet = create_balance_sheet(t_accounts)
check_balance_sheet(balance_sheet)

print_balance_sheet(balance_sheet)
