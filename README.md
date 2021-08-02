Kade Greenburg 2021

To run these programs, both pdf2json and pdfplumber are required. They can be found here:
https://github.com/modesty/pdf2json
https://github.com/jsvine/pdfplumber

To run all processing at once, the command will take this form:
 './pdf_processing.sh -f path/to/file -r int(resolution) -p true'

 FOR EXAMPLE:
 ./pdf_processing.sh -f pdfs/my_pdf.pdf -r 300 -p true
 
 The above example would run on 'my_pdf.pdf' inside the 'pdfs' directory. The resulting generation resolution of the image would be 300, and separate human readable JSON would be generated.

 '-f' specifies a PDF file; this is required. Specify the path to the file from your current directory.
 
 '-r' specifies a resolution for the PDFs converted to images - this is optional and will default to 150 if no resolution is specified. 

 '-p' determines whether human-readable JSON should be generated. If it is to be generated, use '-p true'. If anything else is used or the flag is dropped, no human-readable JSON will be created.