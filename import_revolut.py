from beangulp.importers import csv
from beancount.parser import printer
from beancount.core import data
from bank_classifier import payee_to_account_mapping

from beancount.ingest.importers.csv import Importer as IngestImporter, Col as IngestCol

import click
import io

Col = csv.Col

CATEGORY_TO_ACCOUNT_MAPPING = {
    "Eating out": "Expenses:EatingOut",
    "Groceries": "Expenses:Groceries",
    "Shopping": "Expenses:Shopping",
    "Accommodation": "Expenses:Accommodation",
    "Bills": "Expenses:Bills",
    "Hobbies": "Expenses:Hobbies",
    "Wellness": "Expenses:Wellness",
    "Transport": "Expenses:Transport",
    "Travel": "Expenses:Travel",
    "Entertainment": "Expenses:Entertainment",
    "Donations": "Expenses:Donations",
}


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
            posting_account = "Expenses:RevolutUnclassified"
    else:
        if "Withdrawing savings" in comment:
            posting_account = "Assets:Revolut:Savings"  
        elif "Metal Cashback" in comment:
            posting_account = "Income:Revolut:Cashback"
        elif "Referral reward" in comment:
            posting_account = "Income:Revolut:Referrals"
        else:
            posting_account = "Income:RevolutUnclassified"
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

def get_ingest_importer_for_currency(currency):
    return IngestImporter(
        {
            IngestCol.DATE: "Started Date",
            IngestCol.NARRATION: "Description",
            IngestCol.AMOUNT: "Amount",
            IngestCol.PAYEE: "Description",
            IngestCol.BALANCE: "Balance",
        },
        "Assets:Revolut:Cash",
        currency,
        categorizer=categorizer,
    )

@click.command()
@click.argument("filename", type=click.Path())
def main(filename):
    entries = IMPORTER.extract(filename)
    entries = [e for e in entries if not e.meta.get("skip_transaction")]

    output = io.StringIO()
    printer.print_entries(entries, file=output)
    print(output.getvalue())


if __name__ == "__main__":
    main()
