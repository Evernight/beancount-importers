#!/usr/bin/env python3

import os
import sys

import import_monzo
import import_wise
import import_revolut

data_dir = os.path.join(os.path.dirname(__file__), 'beancount_import_data')
journal_dir = os.path.dirname(__file__)

import_config = {
    'monzo': dict(
        data_sources=[
            dict(
                module='beancount_import.source.generic_importer_source',
                importer=import_monzo.IMPORTER_INGEST,
                account='Assets:Monzo:Cash',
                directory=os.path.join(data_dir, 'monzo')
            )
        ],
        transactions_output=os.path.join(journal_dir, 'beancount_import_beans', 'monzo', 'transactions.bean')
    ),
    'wise_usd': dict(
        data_sources=[
            dict(
                module='beancount_import.source.generic_importer_source',
                importer=import_wise.get_ingest_importer_for_currency('USD'),
                account='Assets:Wise:Cash',
                directory=os.path.join(data_dir, 'wise_usd')
            )
        ],
        transactions_output=os.path.join(journal_dir, 'beancount_import_beans', 'wise_usd', 'transactions.bean')
    ),
    'revolut_usd': dict(
        data_sources=[
            dict(
                module='beancount_import.source.generic_importer_source',
                importer=import_revolut.get_ingest_importer_for_currency('USD'),
                account='Assets:Revolut:Cash',
                directory=os.path.join(data_dir, 'revolut_usd')
            )
        ],
        transactions_output=os.path.join(journal_dir, 'beancount_import_beans', 'revolut', 'transactions.bean')
    ),
    'revolut_gbp': dict(
        data_sources=[
            dict(
                module='beancount_import.source.generic_importer_source',
                importer=import_revolut.get_ingest_importer_for_currency('GBP'),
                account='Assets:Revolut:Cash',
                directory=os.path.join(data_dir, 'revolut_gbp')
            )
        ],
        transactions_output=os.path.join(journal_dir, 'beancount_import_beans', 'revolut', 'transactions.bean')
    ),
    'revolut_eur': dict(
        data_sources=[
            dict(
                module='beancount_import.source.generic_importer_source',
                importer=import_revolut.get_ingest_importer_for_currency('EUR'),
                account='Assets:Revolut:Cash',
                directory=os.path.join(data_dir, 'revolut_eur')
            )
        ],
        transactions_output=os.path.join(journal_dir, 'beancount_import_beans', 'revolut', 'transactions.bean')
    ),
}

def run_reconcile(account, extra_args):
    import beancount_import.webserver

    beancount_import.webserver.main(
        extra_args,
        journal_input=os.path.join(journal_dir, 'main.bean'),
        ignored_journal=os.path.join(journal_dir, 'beancount_import_beans', 'ignored.bean'),
        default_output=import_config[account]['transactions_output'],
        open_account_output_map=[
            ('.*', os.path.join(journal_dir, 'beancount_import_beans', 'accounts.bean')),
        ],
        balance_account_output_map=[
            ('.*', os.path.join(journal_dir, 'beancount_import_beans', 'balance_accounts.bean')),
        ],
        price_output=os.path.join(journal_dir, 'beancount_import_beans', 'prices.bean'),
        data_sources=import_config[account]['data_sources'],
    )


if __name__ == '__main__':
    account = sys.argv[1]
    run_reconcile(account, sys.argv[2:])
