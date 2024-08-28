#!/usr/bin/env python3

import os
import sys
from pathlib import Path

import yaml
import click

import beancount_import.webserver

import import_monzo
import import_wise
import import_revolut

def get_importer(type, account, currency):
    if type == 'monzo':
        return import_monzo.get_ingest_importer(account, currency)
    elif type == 'wise':
        return import_wise.get_ingest_importer(account, currency)
    elif type == 'revolut':
        return import_revolut.get_ingest_importer(account, currency)
    else:
        return None

def load_import_config_from_file(filename, data_dir, output_dir):
    with open(filename, 'r') as config_file:
        parsed_config = yaml.safe_load(config_file)
        data_sources = []
        for key, params in parsed_config['importers'].items():
            data_sources.append(
                dict(
                    module='beancount_import.source.generic_importer_source',
                    importer=get_importer(params['importer'], params['account'], params['currency']),
                    account=params['account'],
                    directory=os.path.join(data_dir, key)
                )
            )
        return dict(
            all=dict(
                data_sources=data_sources,
                transactions_output=os.path.join(output_dir, 'transactions.bean')
            )
        )

def get_import_config(data_dir, output_dir):
    import_config = {
        'monzo': dict(
            data_sources=[
                dict(
                    module='beancount_import.source.generic_importer_source',
                    importer=import_monzo.get_ingest_importer('Assets:Monzo:Cash', 'GBP'),
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
                    importer=import_wise.get_ingest_importer('Assets:Wise:Cash', 'USD'),
                    account='Assets:Wise:Cash',
                    directory=os.path.join(data_dir, 'wise_usd')
                )
            ],
            transactions_output=os.path.join(output_dir, 'wise_usd', 'transactions.bean')
        ),
        'wise_gbp': dict(
            data_sources=[
                dict(
                    module='beancount_import.source.generic_importer_source',
                    importer=import_wise.get_ingest_importer('Assets:Wise:Cash', 'GBP'),
                    account='Assets:Wise:Cash',
                    directory=os.path.join(data_dir, 'wise_gbp')
                )
            ],
            transactions_output=os.path.join(output_dir, 'wise_gbp', 'transactions.bean')
        ),
        'wise_eur': dict(
            data_sources=[
                dict(
                    module='beancount_import.source.generic_importer_source',
                    importer=import_wise.get_ingest_importer('Assets:Wise:Cash', 'EUR'),
                    account='Assets:Wise:Cash',
                    directory=os.path.join(data_dir, 'wise_eur')
                )
            ],
            transactions_output=os.path.join(output_dir, 'wise_eur', 'transactions.bean')
        ),
        'revolut_usd': dict(
            data_sources=[
                dict(
                    module='beancount_import.source.generic_importer_source',
                    importer=import_revolut.get_ingest_importer('Assets:Revolut:Cash', 'USD'),
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
                    importer=import_revolut.get_ingest_importer('Assets:Revolut:Cash', 'GBP'),
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
                    importer=import_revolut.get_ingest_importer('Assets:Revolut:Cash', 'EUR'),
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
    "--importers_config_file", 
    type=click.Path(), 
    default=None,
    help="Path to the importers config file"
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
@click.option(
    "--address", 
    default="127.0.0.1", 
    help="Web server address"
)
@click.option(
    "--port", 
    default="8101", 
    help="Web server port"
)
def main(port, address, target_config, output_dir, data_dir, importers_config_file, journal_file):
    import_config = None
    if importers_config_file:
        import_config = load_import_config_from_file(importers_config_file, data_dir, output_dir)
    else:
        import_config = get_import_config(data_dir, output_dir)
    # Create output structure if it doesn't exist
    os.makedirs(os.path.dirname(import_config[target_config]['transactions_output']), exist_ok=True)
    Path(import_config[target_config]['transactions_output']).touch()
    for file in ['accounts.bean', 'balance_accounts.bean', 'prices.bean', 'ignored.bean']:
        Path(os.path.join(output_dir, file)).touch()

    beancount_import.webserver.main(
        {},
        port=port,
        address=address,
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
