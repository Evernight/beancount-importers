import beangulp
from beangulp.importers import csv
from beancount.core import data
from beancount.ingest.importers.csv import Importer as IngestImporter, Col as IngestCol

from beancount_importers.bank_classifier import payee_to_account_mapping

Col = csv.Col

# UNCATEGORIZED_EXPENSES_ACCOUNT = "Expenses:Uncategorized:Revolut"
UNCATEGORIZED_EXPENSES_ACCOUNT = "Expenses:FIXME"

def categorizer(txn, row):
    payee = row[4]
    comment = row[4]
    if comment.startswith("To "):
        payee = comment[3:]

    posting_account = None
    if txn.postings[0].units.number < 0:
        # Expenses
        posting_account = payee_to_account_mapping.get(payee)

        # Default by category
        if not posting_account:
            posting_account = UNCATEGORIZED_EXPENSES_ACCOUNT
    else:
        if "Withdrawing savings" in comment:
            posting_account = "Assets:Revolut:Savings"  
        elif "Metal Cashback" in comment:
            posting_account = "Income:Revolut:Cashback"
        elif "Referral reward" in comment:
            posting_account = "Income:Revolut:Referrals"
        else:
            posting_account = "Income:Uncategorized:Revolut"
            # Ignore most incoming transactions as they will mostly duplicate Monzo's
            txn.meta["skip_transaction"] = True

    txn.postings.append(
        data.Posting(posting_account, -txn.postings[0].units, None, None, None, None)
    )

    return txn


IMPORTER = csv.CSVImporter(
    {
        Col.DATE: "Started Date",
        Col.NARRATION: "Description",
        Col.AMOUNT: "Amount",
        Col.PAYEE: "Description",
        Col.CURRENCY: "Currency",
        Col.BALANCE: "Balance",
    },
    "Assets:Revolut:Cash",
    "GBP",
    categorizer=categorizer,
)

def get_ingest_importer(account, currency):
    return IngestImporter(
        {
            IngestCol.DATE: "Started Date",
            IngestCol.NARRATION: "Description",
            IngestCol.AMOUNT: "Amount",
            IngestCol.PAYEE: "Description",
            IngestCol.BALANCE: "Balance",
        },
        account,
        currency,
        categorizer=categorizer,
    )

if __name__ == "__main__":
    ingest = beangulp.Ingest([IMPORTER], [])
    ingest()
