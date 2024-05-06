#!/usr/bin/env python3

import os
import sys

import click

import beancount_import.webserver

import import_monzo
import import_wise
import import_revolut

@click.command()
@click.option("--data_dir", type=click.Path(), default='beancount_import_data')
@click.option("--output_dir", type=click.Path(), default='beancount_import_output')
@click.argument("target_config")
def main(target_config, data_dir, output_dir):
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
            transactions_output=os.path.join(output_dir, 'monzo', 'transactions.bean')
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
            transactions_output=os.path.join(output_dir, 'wise_usd', 'transactions.bean')
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
            transactions_output=os.path.join(output_dir, 'revolut', 'transactions.bean')
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
            transactions_output=os.path.join(output_dir, 'revolut', 'transactions.bean')
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
            transactions_output=os.path.join(output_dir, 'revolut', 'transactions.bean')
        ),
    }

    beancount_import.webserver.main(
        {},
        journal_input=os.path.join(output_dir, 'main.bean'),
        ignored_journal=os.path.join(output_dir, 'ignored.bean'),
        default_output=import_config[target_config]['transactions_output'],
        open_account_output_map=[
            ('.*', os.path.join(output_dir, 'accounts.bean')),
        ],
        balance_account_output_map=[
            ('.*', os.path.join(output_dir, 'balance_accounts.bean')),
        ],
        price_output=os.path.join(output_dir, 'prices.bean'),
        data_sources=import_config[target_config]['data_sources'],
    )
    
if __name__ == '__main__':
    main()
