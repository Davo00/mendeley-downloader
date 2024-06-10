# Mendeley API Python Downloader #

## Functionality

Unfortunatly there is no Bulk download feature in Mendeley as of now and you may not access the PDFs in your local storage.
This project is a workaround to download all files in your Library at once. Very basic.

## How to run

Project is based on https://github.com/Mendeley/mendeley-api-python-example.git

Register an app at https://dev.mendeley.com/ use `http://localhost:5000/oauth` as redirect URL

1. Create a `config.yml` by copying the example file and insterting cliend id/secret of your app
2. Run the python file after the installation of the requirements.
3. Visit `http://localhost:5000`

Use Python 3.8 or older, otherwise you will encounter issues with the mendeley SDK
