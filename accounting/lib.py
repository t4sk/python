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
    def __init__(self, *kwargs):
        self.assets = kwargs["assets"]
        self.liabities = kwargs["liabilties"]
        self.equities = kwargs["equities"]
        
    def __str__(self):
        assets = 0
        liabilities = 0
        equities = 0
        
        return "assets: {0} | liabilities: {1} + equities: {2} = {3}".format(
            f'{assets:,d}', f'{liabilities:,d}', f'{equities:,d}', f'{liabilities + equities:,d}'
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

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    