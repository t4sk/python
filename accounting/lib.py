import csv
from datetime import datetime, timedelta
from account_types import (
    ASSET_TYPES,
    LIABILITY_TYPES,
    EQUITY_TYPES,
    REVENUE_TYPES,
    EXPENSE_TYPES,
    MISC_PROFIT_TYPES,
    MISC_LOSS_TYPES
)

from IPython.display import Markdown, display


def print_md(s):
    _s = s
    if isinstance(s, list):
        _s = "\n".join(s)
    # WARNING: $ sign is special char
    display(Markdown(_s))

DATE_FORMAT = "%Y/%m/%d"


def str_to_date(date_str):
    return datetime.strptime(date_str, DATE_FORMAT)


def date_to_str(date):
    return date.strftime(DATE_FORMAT)


def is_date(date):
    return type(date) is datetime


def get_months(year):
    months = []

    for i in range(1, 13):
        start = datetime(year, i, 1)
        end = datetime(year + (i // 12), (i % 12) + 1, 1) - timedelta(days=1)
        months.append((start, end))

    return months

# classes


class Entry:
    def __init__(self, **kwargs):
        # credit | debit
        _type = kwargs["type"]
        assert(_type == "credit" or _type == "debit")
        self.type = _type

        self.account = kwargs["account"].strip()
        self.amount = int(kwargs["amount"])
        self.year = int(kwargs["year"])

    def __str__(self):
        return f'{self.type} | {self.account} | {self.amount:,d} | {self.year}'


class JournalEntry:
    def __init__(self, **kwargs):
        _date = kwargs["date"]
        if not is_date(_date):
            _date = str_to_date(_date)
        self.date = _date

        self.entries = []
        self.memo = kwargs["memo"].strip()

    def __str__(self):
        return "{0}\n{1}\n{2}".format(
            date_to_str(self.date),
            [str(e) for e in self.entries],
            self.memo
        )


class TAccountEntry:
    def __init__(self, **kwargs):
        self.account = kwargs["account"].strip()

        _date = kwargs["date"]
        if not is_date(_date):
            _date = str_to_date(_date)
        self.date = _date

        # credit | debit
        _type = kwargs["type"]
        assert(_type == "credit" or _type == "debit")
        self.type = _type

        self.amount = int(kwargs["amount"])
        self.memo = kwargs["memo"].strip()
        self.year = int(kwargs["year"])

    def __str__(self):
        return "| {0} | {1} | {2} | {3} | {4} | {5} |".format(
            self.account,
            date_to_str(self.date),
            self.type,
            f"{self.amount:,d}",
            self.memo,
            self.year
        )


class TAccount:
    def __init__(self, **kwargs):
        self.account = kwargs["account"].strip()
        self.entries = kwargs["entries"]
        self.credit = 0
        self.debit = 0

        for entry in self.entries:
            assert entry.account == self.account, f'account {entry.acount} != {self.account}'
            if entry.type == "credit":
                self.credit += entry.amount
            elif entry.type == "debit":
                self.debit += entry.amount
            else:
                raise Exception(f'invalid entry type {entry.type}')

    def __str__(self):
        return "{0}\n{1}\n{2} {3}".format(
            self.account,
            [str(e) for e in self.entries],
            f"{self.credit:,d}",
            f"{self.debit:,d}"
        )


class BalanceSheet:
    def __init__(self, **kwargs):
        self.assets = kwargs["assets"]
        self.liabilities = kwargs["liabilities"]
        self.equities = kwargs["equities"]
        self.revenues = kwargs["revenues"]
        self.expenses = kwargs["expenses"]
        self.misc_profits = kwargs["misc_profits"]
        self.misc_losses = kwargs["misc_losses"]

        assets = 0
        liabilities = 0
        equities = 0
        revenues = 0
        expenses = 0
        misc_profits = 0
        misc_losses = 0

        for t_account in self.assets:
            assets += t_account.debit - t_account.credit
        for t_account in self.liabilities:
            liabilities += t_account.credit - t_account.debit
        for t_account in self.equities:
            equities += t_account.credit - t_account.debit
        for t_account in self.revenues:
            revenues += t_account.credit - t_account.debit
        for t_account in self.expenses:
            expenses += t_account.debit - t_account.credit
        for t_account in self.misc_profits:
            misc_profits += t_account.credit - t_account.debit
        for t_account in self.misc_losses:
            misc_losses += t_account.debit - t_account.credit

        self.total_assets = assets
        self.total_liabilities = liabilities
        self.total_equities = equities
        self.total_revenues = revenues
        self.total_expenses = expenses
        self.total_misc_profits = misc_profits
        self.total_misc_losses = misc_losses

    def __str__(self):
        return "assets {0} | liabilities {1} + equities {2} + revenues {3} - expenses {4} + (misc profit {5} - misc loss {6}) = {7}".format(
            f'{self.total_assets:,d}',
            f'{self.total_liabilities:,d}',
            f'{self.total_equities:,d}',
            f'{self.total_revenues:,d}',
            f'{self.total_expenses:,d}',
            f'{self.total_misc_profits:,d}',
            f'{self.total_misc_losses:,d}',
            f'{self.total_liabilities + self.total_equities + self.total_revenues - self.total_expenses + self.total_misc_profits - self.total_misc_losses:,d}'
        )


# CSV
CSV_HEADER = 1


def add_entries(journal_entry, row):
    debit = row[1:4]
    credit = row[4:7]
    year = row[9]

    if debit[0] != "":
        journal_entry.entries.append(
            Entry(
                type="debit",
                account=debit[0],
                amount=debit[2],
                year=year
            )
        )
    if credit[0] != "":
        journal_entry.entries.append(
            Entry(
                type="credit",
                account=credit[0],
                amount=credit[2],
                year=year
            )
        )


def csv_to_journal_entries(file_path):
    journal_entries = []

    with open(file_path, newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        # check date is asc
        prev_date = None

        # skip first line
        for i, row in enumerate(reader):
            if i <= CSV_HEADER:
                continue

            date = row[0].strip()

            # new journal entry
            if date != "":
                # check dates asc
                entry_date = str_to_date(date)
                if prev_date:
                    assert prev_date <= entry_date, f'entry dates not asc {prev_date} > {entry_date}'
                prev_date = entry_date

                memo = (row[7] + ' ' + row[8]).strip()

                journal_entry = JournalEntry(date=date, memo=memo)
                add_entries(journal_entry, row)
                journal_entries.append(journal_entry)
            else:
                journal_entry = journal_entries[-1]
                add_entries(journal_entry, row)

    return journal_entries


def filter_journal_entries_by_date_range(journal_entries, start_at, end_at):
    filtered = []

    for journal_entry in journal_entries:
        if start_at <= journal_entry.date <= end_at:
            filtered.append(journal_entry)

    return filtered


def check_balance(journal_entries):
    credit = 0
    debit = 0

    for journal_entry in journal_entries:
        for entry in journal_entry.entries:
            if entry.type == "credit":
                credit += entry.amount
            elif entry.type == "debit":
                debit += entry.amount
            else:
                raise Exception(f'invalid entry type {entry.type}')

    assert credit == debit, f'credit != debit, credit = {credit:,d}, debit = {debit:,d}'
    print(f'credit {credit:,d} debit {debit:,d}')


def group_journal_entries_by_account(journal_entries):
    # account => t_acount_entry[]
    grouped = {}

    for journal_entry in journal_entries:
        date = journal_entry.date
        memo = journal_entry.memo

        for entry in journal_entry.entries:
            account = entry.account

            if not account in grouped:
                grouped[account] = []

            grouped[account].append(
                TAccountEntry(
                    account=account,
                    date=date,
                    type=entry.type,
                    amount=entry.amount,
                    memo=memo,
                    year=entry.year
                )
            )

    return grouped


def journal_entries_to_t_accounts(journal_entries):
    t_accounts = []
    accounts = group_journal_entries_by_account(journal_entries)

    for account, entries in accounts.items():
        t_accounts.append(TAccount(
            account=account,
            entries=entries
        ))

    return t_accounts


def filter_t_accounts_by_year(t_accounts, **kwargs):
    year = kwargs["year"]
    filtered = []

    for t_account in t_accounts:
        entries = list(filter(lambda e: e.year == year, t_account.entries))
        if len(entries) > 0:
            filtered.append(
                TAccount(
                    account=t_account.account,
                    entries=entries
                )
            )

    return filtered

def save_t_accounts_to_csv(t_accounts, **kwargs):
    year = kwargs.get("year", None)
    rows = []

    # header
    rows.append(["", "借方", "貸方", "摘要", "年度"])

    for t_account in t_accounts:
        # title
        rows.append([t_account.account])

        debit = 0
        credit = 0

        for entry in t_account.entries:
            if year != None and year != entry.year:
                continue

            # date, debit, credit, memo
            row = [
                date_to_str(entry.date),
                entry.amount if entry.type == "debit" else "",
                entry.amount if entry.type == "credit" else "",
                entry.memo,
                entry.year
            ]

            if entry.type == "debit":
                debit += entry.amount
            elif entry.type == "credit":
                credit += entry.amount
            else:
                raise Exception(f'invalid entry type {entry.type}')

            rows.append(row)

        # append debit and credit total
        rows.append(["", debit, credit, debit - credit])

    file_name = "t-accounts.csv"
    if year:
        file_name = f't-accounts-{year}.csv'

    with open(file_name, 'w', newline='\n') as file:
        writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for row in rows:
            writer.writerow(row)

        print(f'saved {file_name}')


def csv_to_t_accounts(file_path):
    t_accounts = []

    with open(file_path, newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')

        account = ""
        entries = []

        for i, row in enumerate(reader):
            # skip header
            if i == 0:
                continue
            # row is account header
            if len(row) == 1:
                account = row[0]
            # row is "", debit,credit, diff for account
            elif len(row) == 4:
                (_, debit, crebit, _diff) = row

                t_account = TAccount(
                    account=account,
                    entries=entries
                )

                # check debit, credit
                assert t_account.debit == int(
                    debit), f'debit {t_account.debit} != {debit}'
                assert t_account.debit == int(
                    debit), f'crebit {t_account.credit} != {crebit}'

                t_accounts.append(t_account)
                # reset entries
                entries = []
            else:
                (date, debit, credit, memo, year) = row
                _type = ""
                if debit != "":
                    _type = "debit"
                elif credit != "":
                    _type = "credit"
                else:
                    raise Exception(
                        'expected either debit or crebit to be not empty'
                    )

                amount = 0
                if _type == "debit":
                    amount = int(debit)
                elif _type == "credit":
                    amount = int(credit)
                else:
                    raise Exception(
                        f'invalid type {_type}. expected debit or crebit'
                    )

                entries.append(TAccountEntry(
                    account=account,
                    date=date,
                    type=_type,
                    amount=amount,
                    memo=memo,
                    year=year
                ))

    return t_accounts


def get_accounts(t_accounts):
    accounts = set()

    for t_account in t_accounts:
        account = t_account.account

        if account not in accounts:
            accounts.add(account)

    return accounts


def create_balance_sheet(t_accounts):
    assets = []
    liabilities = []
    equities = []
    revenues = []
    expenses = []
    misc_profits = []
    misc_losses = []

    # csv_to_t_accounts
    for t_account in t_accounts:
        if t_account.account in ASSET_TYPES:
            assets.append(t_account)
        elif t_account.account in LIABILITY_TYPES:
            liabilities.append(t_account)
        elif t_account.account in EQUITY_TYPES:
            equities.append(t_account)
        elif t_account.account in REVENUE_TYPES:
            revenues.append(t_account)
        elif t_account.account in EXPENSE_TYPES:
            expenses.append(t_account)
        elif t_account.account in MISC_PROFIT_TYPES:
            misc_profits.append(t_account)
        elif t_account.account in MISC_LOSS_TYPES:
            misc_losses.append(t_account)
        else:
            raise Exception(
                f'{t_account.account} is not in asset, liability, equity, revenue or expense')

    balance_sheet = BalanceSheet(
        assets=assets,
        liabilities=liabilities,
        equities=equities,
        revenues=revenues,
        expenses=expenses,
        misc_profits=misc_profits,
        misc_losses=misc_losses
    )

    return balance_sheet


def check_balance_sheet(balance_sheet):
    assets = 0
    liabilities = 0
    equities = 0
    revenues = 0
    expenses = 0
    misc_profits = 0
    misc_losses = 0

    for t_account in balance_sheet.assets:
        assets += t_account.debit - t_account.credit
    for t_account in balance_sheet.liabilities:
        liabilities += t_account.credit - t_account.debit
    for t_account in balance_sheet.equities:
        equities += t_account.credit - t_account.debit
    for t_account in balance_sheet.revenues:
        revenues += t_account.credit - t_account.debit
    for t_account in balance_sheet.expenses:
        expenses += t_account.debit - t_account.credit
    for t_account in balance_sheet.misc_profits:
        misc_profits += t_account.credit - t_account.debit
    for t_account in balance_sheet.misc_losses:
        misc_losses += t_account.debit - t_account.credit

    assert assets == balance_sheet.total_assets, "assets"
    assert liabilities == balance_sheet.total_liabilities, "liabilities"
    assert equities == balance_sheet.total_equities, "equities"
    assert revenues == balance_sheet.total_revenues, "revenues"
    assert expenses == balance_sheet.total_expenses, "expenses"
    assert misc_profits == balance_sheet.total_misc_profits, "misc profits"
    assert misc_losses == balance_sheet.total_misc_losses, "misc losses"

    left = assets
    right = liabilities + equities + revenues - expenses + misc_profits - misc_losses

    assert left == right, "assets {0} | liabilities {1} + equities {2} + revenues {3} - expenses {4} + misc profits {5} - misc losses {6} = {7}".format(
        f'{assets:,d}',
        f'{liabilities:,d}',
        f'{equities:,d}',
        f'{revenues:,d}',
        f'{expenses:,d}',
        f'{misc_profits:,d}',
        f'{misc_losses:,d}',
        f'{right:,d}'
    )


def print_balance_sheet(balance_sheet):
    def print_table(title, rows):
        s = [
            f'|{title}||',
            ":--- | ---:",
        ]
        for row in rows:
            s.append(row)
        print_md(s)
    
    rows = []
    for t_account in balance_sheet.assets:
        diff = t_account.debit - t_account.credit
        rows.append(f'| {t_account.account} | {diff:,d} |')
    print_table("資産", rows)

    rows = []
    for t_account in balance_sheet.liabilities:
        diff = t_account.credit - t_account.debit
        rows.append(f'| {t_account.account} | {diff:,d} |')
    print_table("負債", rows)

    rows = []
    for t_account in balance_sheet.equities:
        diff = t_account.credit - t_account.debit
        rows.append(f'| {t_account.account} | {diff:,d} |')
    print_table("資本", rows)

    rows = []
    for t_account in balance_sheet.revenues:
        diff = t_account.credit - t_account.debit
        rows.append(f'| {t_account.account} | {diff:,d} |')
    print_table("収益", rows)
    
    rows = []
    for t_account in balance_sheet.expenses:
        diff = t_account.debit - t_account.credit
        rows.append(f'| {t_account.account} | {diff:,d} |')
    print_table("費用", rows)
    
    rows = []
    for t_account in balance_sheet.misc_profits:
        diff = t_account.credit - t_account.debit
        rows.append(f'| {t_account.account} | {diff:,d} |')
    print_table("雑所得", rows)
    
    rows = []
    for t_account in balance_sheet.misc_losses:
        diff = t_account.debit - t_account.credit
        rows.append(f'| {t_account.account} | {diff:,d} |')
    print_table("雑損失", rows)

    assets = balance_sheet.total_assets
    liabilities = balance_sheet.total_liabilities
    equities = balance_sheet.total_equities
    revenues = balance_sheet.total_revenues
    expenses = balance_sheet.total_expenses
    misc_profits = balance_sheet.total_misc_profits
    misc_losses = balance_sheet.total_misc_losses
    total = liabilities + equities + revenues - expenses + misc_profits - misc_losses

    rows = []
    rows.append(f'| 資産 | {assets:,d} |')
    rows.append(f'| 負債 | {liabilities:,d} |')
    rows.append(f'| 資本 | {equities:,d} |')
    rows.append(f'| 収益 | {revenues:,d} |')
    rows.append(f'| 費用 | {expenses:,d} |')
    rows.append(f'| 雑所得 | {misc_profits:,d} |')
    rows.append(f'| 雑損失 | {misc_losses:,d} |')
    print_table("", rows)
    print(f'負債 + 資本 + 収益 - 費用 + 雑所得 - 雑損失 {total:,d}')


def print_profit_loss(balance_sheet):
    def print_table(rows):
        s = [
            "| account | credit | debit |",
            "| :------ | -----: | ----: |"
        ]
        for row in rows:
            s.append(row)
        print_md(s)

    rows = []
    total_revenue = 0
    for t_account in balance_sheet.revenues:
        total_revenue += t_account.credit - t_account.debit
        rows.append(f'| {t_account.account} | {t_account.credit:,d} | {t_account.debit:,d} |')
    print_table(rows)

    print(f'収益 {total_revenue:,d}')

    rows = []
    total_expense = 0
    for t_account in balance_sheet.expenses:
        total_expense += t_account.debit - t_account.credit
        rows.append(f'| {t_account.account} | {t_account.credit:,d} | {t_account.debit:,d} |')
    print_table(rows)

    print(f'費用 {total_expense:,d}')

    # misc profit / loss
    total_misc_profits = balance_sheet.total_misc_profits
    total_misc_losses = balance_sheet.total_misc_losses
    misc_profit = max(total_misc_profits - total_misc_losses, 0)

    # summary - render markdown
    rows = [
        "| | |",
        ":--- | ---:"
    ]
    rows.append(f'| 利益 | {total_revenue - total_expense:,d} |')
    rows.append(f'| 雑所得 | {total_misc_profits:,d} |')
    rows.append(f'| 雑損失 | {total_misc_losses:,d} |')
    
    print_md(rows)
    
    print(f'収益 - 費用 + max(雑所得 - 雑損失, 0) {total_revenue - total_expense + misc_profit:,d}')
