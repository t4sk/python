# coding: utf-8

# 貸借対照表
from lib import csv_to_t_accounts, get_accounts, create_balance_sheet, check_balance_sheet, print_balance_sheet


def main(**kwargs):
    debug = kwargs.get("debug", False)
    check_balance = kwargs.get("check_balance", True)
    
    t_accounts = csv_to_t_accounts(kwargs["t_accounts_csv"])
    accounts = get_accounts(t_accounts)

    if debug:
        for account in accounts:
            print(account)

    balance_sheet = create_balance_sheet(t_accounts)
    if check_balance:
        check_balance_sheet(balance_sheet)

    print_balance_sheet(balance_sheet)
