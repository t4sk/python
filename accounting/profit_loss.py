# profit loss
# 損益計算書
from lib import csv_to_t_accounts, create_balance_sheet, check_balance_sheet, print_profit_loss

t_accounts = csv_to_t_accounts("t-accounts.csv")

balance_sheet = create_balance_sheet(t_accounts)
check_balance_sheet(balance_sheet)

print_profit_loss(balance_sheet)
