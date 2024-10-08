This repository contains a few simple [beangulp](https://github.com/beancount/beangulp) or beancount-ingest-based importers for [Beancount](https://github.com/beancount/beancount), in particular for Wise, Monzo and Revolut banks.

The easiest way to use these is via https://github.com/Evernight/lazy-beancount. 
Alternatively you can also follow setup below for standalone configuration.

NOTE: instructions below are outdated as project moved to be installable via ```pip```. But probably they should still work.

## Setup
In your local Python installation (or virtual environment / conda):

    pip3 insall beancount
    pip3 insall click

Also:

    git clone https://github.com/beancount/beangulp

## Usage (direct)
Use it to generate beancount file from source csv like this:

    PYTHONPATH=.:beangulp python3 import_wise.py <csv_file> > wise.bean
    PYTHONPATH=.:beangulp python3 import_monzo.py <csv_file> > monzo.bean
    PYTHONPATH=.:beangulp python3 import_revolut.py <csv_file> > revolut.bean

## Usage (via Beancount-import)
Using it via [beancount-import](https://github.com/jbms/beancount-import) with additional features and an UI

Additional setup:

    git clone https://github.com/jbms/beancount-import

To run: 

    PYTHONPATH=.:beangulp python3 beancount_import_run.py wise_usd

or:

    PYTHONPATH=.:beangulp python3 beancount_import_run.py monzo

or similar (see into the ```beancount_import_run.py``` file, it's pretty straightforward).

Then go to the UI at http://localhost:8101/ (by default).

## Explanation
``beancount_import_run.py`` is a simple interface to https://github.com/jbms/beancount-import. I prefer to store outputs from different import files in different directories so the structure of the config is based on that.
It should be pretty straightforward to adjust it for your needs if necessary.
