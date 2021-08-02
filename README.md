Kade Greenburg 2021

To run these programs, both pdf2json and pdfplumber are required. They can be found here:
https://github.com/modesty/pdf2json
https://github.com/jsvine/pdfplumber

To run all processing at once, the command will take this form: ./pdf_processing -f path/to/file -r resolution (int) -p true. -f specifies a file; this is required. -r specifies a resolution for the PDFs converted to images - this is optional and will default to 150 if no resolution is specified. -p determines whether human-readable JSON should be generated. If set to true "as in '-p true'", the JSON will be pretty printed. If anything else is used or the flag is dropped, no pretty printed JSON will be generated.