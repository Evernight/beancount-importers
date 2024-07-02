from collections import defaultdict
import datetime
from beancount.core import data
import sys

ACCOUNT_PAYEES = {
    "Expenses:Bills": [],
    "Expenses:Projects": [],
    "Expenses:Wellness": [],
    "Expenses:Services": [],
    "Expenses:Donations": [],
    "Expenses:Accommodation": [],
    "Expenses:Education": [],
    "Expenses:Hobbies": [],
    "Expenses:Health": [],
    "Expenses:Groceries": [],
    "Expenses:Shopping": [],
    "Expenses:Transport": [],
    "Expenses:Entertainment": [],
    "Expenses:Travel": [],
    "Expenses:EatingOut": [],
    "Expenses:Taxes": [],
    "Assets:Monzo:Savings": ["Savings Pot"],
    "Assets:Physical:Cash": ["ATM"],
    "Expenses:Gifts": [],
    "Expenses:Work": [],
    "Expenses:Documents": [],
}
payee_to_account_mapping = {}
for account, payee_list in ACCOUNT_PAYEES.items():
    for payee in payee_list:
        payee_to_account_mapping[payee] = account

def filter_refunds(entries):
    entries_by_amount = defaultdict(list)
    for entry in entries:
        if isinstance(entry, data.Balance):
            continue
        if entry.postings[1].account and "Expenses" in entry.postings[1].account and entry.postings[0].units.number < 0:
            entries_by_amount[entry.postings[0].units.number].append(entry)
        for candidate in entries_by_amount[-entry.postings[0].units.number]:
            if "skip_transaction" in entry.meta or "skip_transaction" in candidate.meta:
                continue
            if 'Unclassified' in entry.postings[1].account and entry.date - candidate.date < datetime.timedelta(days=30):
                entry.meta["skip_transaction"] = True
                candidate.meta["skip_transaction"] = True
            else:
                pass
    return entries
