from beangulp.importers import csv
from beancount.parser import printer
from beancount.core import data
from bank_classifier import payee_to_account_mapping, filter_refunds
import dateutil

from beancount.ingest.importers.csv import Importer as IngestImporter, Col as IngestCol

import click
import io

Col = csv.Col

# PYTHONPATH=.:beangulp python3 import_wise.py <csv_file> > wise.bean

TRANSACTIONS_CLASSIFIED_BY_ID = {
    "CARD-XXXXXXXXX": "Expenses:Shopping",
}


def categorizer(txn, row):
    transaction_id = row[0]
    payee = row[13]
    comment = row[4]
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
            posting_account = "Expenses:Uncategorized:Wise"
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

    return txn

IMPORTER = csv.CSVImporter(
    {
        Col.DATE: "Date",
        Col.NARRATION: "Description",
        Col.AMOUNT: "Amount",
        Col.PAYEE: "Merchant",
        Col.CURRENCY: "Currency",
        Col.REFERENCE_ID: "TransferWise ID",
        Col.BALANCE: "Running Balance",
    },
    "Assets:Wise:Cash",
    "GBP",
    categorizer=categorizer,
    dateutil_kwds={"parserinfo": dateutil.parser.parserinfo(dayfirst=True)},
)

def get_ingest_importer_for_currency(currency):
    return IngestImporter(
        {
            IngestCol.DATE: "Date",
            IngestCol.NARRATION: "Description",
            IngestCol.AMOUNT: "Amount",
            IngestCol.PAYEE: "Merchant",
            IngestCol.REFERENCE_ID: "TransferWise ID",
            IngestCol.BALANCE: "Running Balance",
        },
        "Assets:Wise:Cash",
        currency,
        categorizer=categorizer,
        dateutil_kwds={"parserinfo": dateutil.parser.parserinfo(dayfirst=True)},
    )

@click.command()
@click.argument("filename", type=click.Path())
def main(filename):
    entries = IMPORTER.extract(filename)

    entries = filter_refunds(entries)
    entries = [e for e in entries if not e.meta.get("skip_transaction")]

    output = io.StringIO()
    printer.print_entries(entries, file=output)
    print(output.getvalue())


if __name__ == "__main__":
    main()
