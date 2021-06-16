Kade Greenburg 2021

To run these programs, both pdf2json and pdfplumber are required. They can be found here:
https://github.com/modesty/pdf2json
https://github.com/jsvine/pdfplumber

To run all utilities as one command, the script 'pdf_processing.sh' will do the trick. It has two flags: -f, which specifies the file path to a given PDF, and -r, which specifies a resolution for the outputted PDF as a PNG. While the -r flag is optional, the -f flag must be specified or an error will occur.