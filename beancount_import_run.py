#!/usr/bin/env python3

import os
import sys
from pathlib import Path

import click

import beancount_import.webserver

import import_monzo
import import_wise
import import_revolut

def get_import_config(data_dir, output_dir):
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
    import_config_all = dict(
        data_sources=[],
        transactions_output=os.path.join(output_dir, 'transactions.bean')
    )
    for k, v in import_config.items():
        import_config_all['data_sources'].extend(v['data_sources'])

    import_config['all'] = import_config_all
    return import_config
    
@click.command()
@click.option(
    "--journal_file", 
    type=click.Path(), 
    default='main.bean',
    help="Path to your main ledger file"
)
@click.option(
    "--data_dir", 
    type=click.Path(), 
    default='beancount_import_data', 
    help="Directory with your import data (e.g. bank statements in csv)"
)
@click.option(
    "--output_dir", 
    type=click.Path(), 
    default='beancount_import_output',
    help="Where to put output files (don't forget to include them in your main ledger)"
)
@click.option(
    "--target_config", 
    default="all", 
    help="Note that specifying particular config will also result in transactions " + 
    "being imported into specific output file for that config"
)
def main(target_config, journal_file, data_dir, output_dir):
    # Create output structure if it doesn't exist
    import_config = get_import_config(data_dir, output_dir)
    os.makedirs(os.path.dirname(import_config[target_config]['transactions_output']), exist_ok=True)
    Path(import_config[target_config]['transactions_output']).touch()
    Path(os.path.join(output_dir, 'accounts.bean')).touch()
    Path(os.path.join(output_dir, 'balance_accounts.bean')).touch()
    Path(os.path.join(output_dir, 'prices.bean')).touch()
    Path(os.path.join(output_dir, 'ignored.bean')).touch()

    beancount_import.webserver.main(
        {},
        journal_input=journal_file,
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
