import beangulp
import dateutil

from beangulp.importers import csv
from beancount.core import data
from beancount.ingest.importers.csv import Importer as IngestImporter, Col as IngestCol

from beancount_importers.bank_classifier import payee_to_account_mapping

Col = csv.Col

# PYTHONPATH=.:beangulp python3 import_wise.py <csv_file> > wise.bean

TRANSACTIONS_CLASSIFIED_BY_ID = {
    "CARD-XXXXXXXXX": "Expenses:Shopping",
}

# UNCATEGORIZED_EXPENSES_ACCOUNT = "Expenses:Uncategorized:Wise"
UNCATEGORIZED_EXPENSES_ACCOUNT = "Expenses:FIXME"

def categorizer(txn, row):
    transaction_id = row[0]
    payee = row[13]
    comment = row[4]
    note = row[17]
    if not payee and comment.startswith("Sent money to "):
        payee = comment[14:]

    posting_account = None
    if txn.postings[0].units.number < 0:
        # Expenses
        posting_account = payee_to_account_mapping.get(payee)

        # Custom
        # if payee == "Some Gym That Sells Food":
        #     if txn.postings[0].units.number < -40:
        #         posting_account = "Expenses:Wellness"
        #     else:
        #         posting_account = "Expenses:EatingOut"

        # Classify transfers
        # if payee.lower() == "your name":
        #     if "Revolut" in comment:
        #         posting_account = "Assets:Revolut:Cash"
        #     else:
        #         posting_account = "Assets:Wise:Cash"
        # elif payee == "Broker":
        #     posting_account = "Assets:Broker:Cash"
        # elif payee.lower() == "some dude":
        #     posting_account = "Liabilities:Shared:SomeDude"

        # if comment.endswith("to my savings jar"):
        #     posting_account = "Assets:Wise:Savings:USD"

        # Specific transactions
        if transaction_id in TRANSACTIONS_CLASSIFIED_BY_ID:
            posting_account = TRANSACTIONS_CLASSIFIED_BY_ID[transaction_id]

        # Default by category
        if not posting_account:
            posting_account = UNCATEGORIZED_EXPENSES_ACCOUNT
    else:
        if transaction_id in TRANSACTIONS_CLASSIFIED_BY_ID:
            posting_account = TRANSACTIONS_CLASSIFIED_BY_ID[transaction_id]
        elif comment.endswith("USD jar"):
            posting_account = "Assets:Wise:Savings:USD"
        else:
            posting_account = 'Income:Uncategorized:Wise'
            pass

    txn.postings.append(
        data.Posting(posting_account, -txn.postings[0].units, None, None, None, None)
    )
    if note:
        txn.meta['comment'] = note

    return txn

def get_importer(account, currency):
    return csv.CSVImporter(
        {
            Col.DATE: "Date",
            Col.NARRATION: "Description",
            Col.AMOUNT: "Amount",
            Col.PAYEE: "Merchant",
            Col.CURRENCY: "Currency",
            Col.REFERENCE_ID: "TransferWise ID",
            Col.BALANCE: "Running Balance",
        },
        account,
        currency,
        categorizer=categorizer,
        dateutil_kwds={"parserinfo": dateutil.parser.parserinfo(dayfirst=True)},
    )

if __name__ == "__main__":
    ingest = beangulp.Ingest([get_importer("Assets:Wise:Cash", "GBP", {})], [])
    ingest()
