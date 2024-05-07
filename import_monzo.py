from beangulp.importers import csv
from beancount.parser import printer
from beancount.core import data
import dateutil
from bank_classifier import payee_to_account_mapping, filter_refunds
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

TRANSACTIONS_CLASSIFIED_BY_ID = {
}


def categorizer(txn, row):
    transaction_id = row[0]
    payee = row[4]
    monzo_category = row[6]
    comment = row[11]

    posting_account = None
    if txn.postings[0].units.number <= 0:
        # Expenses
        posting_account = payee_to_account_mapping.get(payee)

        # Default by category
        if not posting_account:
            posting_account = CATEGORY_TO_ACCOUNT_MAPPING.get(
                monzo_category, "Expenses:Uncategorized:Monzo"
            )
    else:
        if payee == "Savings Pot" or payee == "Savings Monzo Pot":
            posting_account = "Assets:Monzo:Savings"
        # elif '<your name>' in payee.lower():
        #     txn.meta["skip_transaction"] = True
        if not posting_account:
            posting_account = "Income:Uncategorized:Monzo"

    # Specific transactions
    if transaction_id in TRANSACTIONS_CLASSIFIED_BY_ID:
        posting_account = TRANSACTIONS_CLASSIFIED_BY_ID[transaction_id]

    txn.postings.append(
        data.Posting(posting_account, -txn.postings[0].units, None, None, None, None)
    )

    return txn

IMPORTER = csv.CSVImporter(
    {
        Col.DATE: "Date",
        Col.NARRATION: "Description",
        Col.AMOUNT: "Amount",
        Col.PAYEE: "Name",
        Col.CURRENCY: "Currency",
        Col.REFERENCE_ID: "Transaction ID",
        Col.CATEGORY: "Category",
    },
    "Assets:Monzo:Cash",
    "GBP",
    categorizer=categorizer,
    dateutil_kwds={"parserinfo": dateutil.parser.parserinfo(dayfirst=True)},
)

IMPORTER_INGEST = IngestImporter(
    {
        IngestCol.DATE: "Date",
        IngestCol.NARRATION: "Description",
        IngestCol.AMOUNT: "Amount",
        IngestCol.PAYEE: "Name",
        IngestCol.REFERENCE_ID: "Transaction ID",
        IngestCol.CATEGORY: "Category",
    },
    "Assets:Monzo:Cash",
    "GBP",
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
