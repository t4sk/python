# profit loss
# 損益計算書
from lib import csv_to_t_accounts, create_balance_sheet, check_balance_sheet, print_profit_loss

def main(**kwargs):
    t_accounts = csv_to_t_accounts(kwargs["t_accounts_csv"])

    balance_sheet = create_balance_sheet(t_accounts)
    check_balance_sheet(balance_sheet)

    print_profit_loss(balance_sheet)
