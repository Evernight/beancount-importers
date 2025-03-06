This repository contains a few simple [beangulp](https://github.com/beancount/beangulp)'s CSVImporter importers for [Beancount](https://github.com/beancount/beancount) for Wise, Monzo, Revolut banks, and Interactive Brokers.
They are also adapted to be used together with [beancount-import](https://github.com/jbms/beancount-import) and configured via YAML files.

The easiest way to use these importers is via https://github.com/Evernight/lazy-beancount

Alternatively you can also follow setup below for standalone configuration.

## Setup
```
pip3 install git+https://github.com/Evernight/beancount-importers
```

## Usage (direct)
Use it to generate beancount file from source csv like this:

    python3 -m beancount_importers.import_wise extract <csv_file>
    python3 -m beancount_importers.import_monzo extract <csv_file>
    python3 -m beancount_importers.import_revolut extract <csv_file>

## Usage (via Beancount-import)
Using it via [beancount-import](https://github.com/jbms/beancount-import) with additional features and an UI

    python3 -m beancount_importers.beancount_import_run \
        --journal_file main.bean \
        --importers_config_file importers_config.yml

Note that ```importers_config.yml``` is an example file, modify it to match your set of accounts.

Then go to the UI at http://localhost:8101/ (by default).
