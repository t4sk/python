import csv

def test_me():
    print("test me")

### classes
class Entry:
    def __init__(self, **kwargs):
        # credit | debit
        self.type = kwargs["type"]
        self.account = kwargs["account"]
        self.amount = kwargs["amount"]
    
    def __str__(self):
        return "{0} {1} {2}".format(self.type, self.account, f"{self.amount:,d}")

class JournalEntry:
    def __init__(self, **kwargs):
        self.date = kwargs["date"]
        self.entries = []
        self.memo = kwargs["memo"]
        
    def __str__(self):
        return "{0}\n{1}\n{2}".format(self.date, [str(e) for e in self.entries], self.memo)

class TAccountEntry:
    def __init__(self, **kwargs):
        self.account = kwargs["account"]
        self.date = kwargs["date"]
        # credit | debit
        self.type = kwargs["type"]
        self.amount = kwargs["amount"]
        self.memo = kwargs["memo"]
    
    def __str__(self):
        return "{0} {1} {2} {3} {4}".format(self.account, self.date, self.type, f"{self.amount:,d}", self.memo)

    
class TAccount:
    def __init__(self, **kwargs):
        self.account = kwargs["account"]
        self.entries = kwargs["entries"]
        self.credit = 0
        self.debit = 0
        
        for entry in self.entries:
            assert entry.account == self.account, f'account {entry.acount} != {account}'
            if entry.type == "credit":
                self.credit += entry.amount
            elif entry.type == "debit":
                self.debit += entry.amount
            else:
                raise Exception(f'invalid entry type {entry.type}')
    
    def __str__(self):
        return "{0}\n{1}\n{2} {3}".format(
            self.account, [str(e) for e in self.entries], f"{self.credit:,d}", f"{self.debit:,d}"
        )

class BalanceSheet:
    def __init__(self, **kwargs):
        self.assets = kwargs["assets"]
        self.liabilities = kwargs["liabilities"]
        self.equities = kwargs["equities"]
        self.revenues = kwargs["revenues"]
        self.expenses = kwargs["expenses"]
        
    def __str__(self):
        assets = 0
        liabilities = 0
        equities = 0
        revenues = 0
        expenses = 0
        
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
        
        return "assets {0} | liabilities {1} + equities {2} + (revenues {3} - expenses {4}) = {5}".format(
            f'{assets:,d}',
            f'{liabilities:,d}',
            f'{equities:,d}',
            f'{revenues:,d}',
            f'{expenses:,d}',
            f'{liabilities + equities + revenues - expenses:,d}'
        )

### CSV
CSV_HEADER = 1

def add_entries(journal_entry, row):
    debit = row[1:4]
    credit = row[4:7]

    if debit[0] != "":
        journal_entry.entries.append(
            Entry(
                type="debit",
                account=debit[0].strip(),
                amount=int(debit[2])
            )
        )
    if credit[0] != "":
        journal_entry.entries.append(
            Entry(
                type="credit",
                account=credit[0].strip(),
                amount=int(credit[2])
            )
        )

def csv_to_journal_entries(file_path):
    journal_entries = []

    with open(file_path, newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        # skip first line
        for i, row in enumerate(reader):
            if i <= CSV_HEADER:
                continue
                
            date = row[0].strip()
            
            # new journal entry
            if date != "":
                memo = (row[7] + ' ' + row[8]).strip()
                
                journal_entry = JournalEntry(date=date, memo=memo)  
                add_entries(journal_entry, row)
                journal_entries.append(journal_entry)
            else:
                journal_entry = journal_entries[-1]
                add_entries(journal_entry, row)
    
    return journal_entries

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

def group_by_account(journal_entries):
    # account => entry[]
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
                    memo=memo
                )
            )

    return grouped
    
def t_accounts_to_csv(t_accounts):
    rows = []
    
    for account, entries in t_accounts.items():
        # title
        rows.append([account])
        
        debit = 0
        credit = 0
        
        for entry in entries:
            # date, debit, credit, memo
            row = [
                entry.date,
                entry.amount if entry.type == "debit" else "",
                entry.amount if entry.type == "credit" else "",
                entry.memo
            ]
            
            if entry.type == "debit":
                debit += entry.amount
            elif entry.type == "credit":
                credit += entry.amount
            else:
                raise Exception(f'invalid entry type {entry.type}')

            rows.append(row)
        
        # append debit, credit total
        # skip, debit total, credit total
        rows.append(["", debit, credit])
    
    with open('t-accounts.csv', 'w', newline='\n') as file:
        writer= csv.writer(file, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        for row in rows:
            writer.writerow(row)
        
        print("saved t-accounts.csv")

def csv_to_t_accounts(file_path):
    t_accounts = []

    with open(file_path, newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        
        account = ""
        entries = []
        
        for row in reader:
            # row is account header
            if len(row) == 1:                    
                account = row[0]
            # row is credit, debit total for account
            elif len(row) == 3:
                (_, debit, crebit) = row
                
                t_account = TAccount(
                    account=account,
                    entries=entries
                )
                
                # check debit, credit
                assert t_account.debit == int(debit), f'debit {t_account.debit} != {debit}'
                assert t_account.debit == int(debit), f'crebit {t_account.crebit} != {crebit}'
                
                t_accounts.append(t_account)
                # reset entries
                entries = []
            else:
                (date, debit, credit, memo) = row
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
                    memo=memo
                ))

    return t_accounts

def get_accounts(t_accounts):
    accounts = set()
    
    for t_account in t_accounts:
        account = t_account.account
        
        if account not in accounts:
            accounts.add(account)
    
    return accounts

def create_balance_sheet(
    t_accounts,
    asset_types,
    liability_types,
    equities_types,
    revenues_types,
    expense_types
):
    assets = []
    liabilities = []
    equities = []
    revenues = []
    expenses = []

    # csv_to_t_accounts
    for t_account in t_accounts:
        if t_account.account in asset_types:
            assets.append(t_account)
        elif t_account.account in liability_types:
            liabilities.append(t_account)
        elif t_account.account in equities_types:
            equities.append(t_account)
        elif t_account.account in revenues_types:
            revenues.append(t_account)
        elif t_account.account in expense_types:
            expenses.append(t_account)
        else:
            raise Exception(f'{t_account.account} is not in asset, liability, equity, revenue or expense')
    
    balance_sheet = BalanceSheet(
        assets=assets,
        liabilities=liabilities,
        equities=equities,
        revenues=revenues,
        expenses=expenses
    )
    
    return balance_sheet
    
def check_balance_sheet(balance_sheet):
    assets = 0
    liabilities = 0
    equities = 0
    revenues = 0
    expenses = 0

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
    
    left = assets
    right = liabilities + equities + revenues - expenses
    
    assert left == right, "assets {0} | liabilities {1} + equities {2} + (revenues {3} - expenses {4}) = {5}".format(
        f'{assets:,d}',
        f'{liabilities:,d}',
        f'{equities:,d}',
        f'{revenues:,d}',
        f'{expenses:,d}',
        f'{right:,d}'
    )
    
def print_balance_sheet(balance_sheet):
    assets = 0
    liabilities = 0
    equities = 0
    revenues = 0
    expenses = 0
    
    print("=== 資産 ===")
    for t_account in balance_sheet.assets:
        diff = t_account.debit - t_account.credit
        assets += diff
        print(f'{t_account.account} {diff:,d}')
    
    print("=== 負債 ===")
    for t_account in balance_sheet.liabilities:
        diff = t_account.credit - t_account.debit
        liabilities += diff
        print(f'{t_account.account} {diff:,d}')
    
    print("=== 資本 ===")
    for t_account in balance_sheet.equities:
        diff = t_account.credit - t_account.debit
        equities += diff
        print(f'{t_account.account} {diff:,d}')
    
    print("=== 収益 ===")
    for t_account in balance_sheet.revenues:
        diff = t_account.credit - t_account.debit
        revenues += diff
        print(f'{t_account.account} {diff:,d}')
    
    print("=== 費用 ===")
    for t_account in balance_sheet.expenses:
        diff = t_account.debit - t_account.credit
        expenses += diff
        print(f'{t_account.account} {diff:,d}')
    
    print("============")
    print(f'資産 {assets:,d}')
    print(f'負債 {liabilities:,d}')
    print(f'資本 {equities:,d}')
    print(f'収益 {revenues:,d}')
    print(f'費用 {expenses:,d}')
    print(f'負債 + 資本 + (収益 - 費用) {liabilities + equities + (revenues - expenses):,d}')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    