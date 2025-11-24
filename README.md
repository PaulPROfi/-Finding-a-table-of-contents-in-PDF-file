# Description
A script that extracts the first 10 pages of a PDF document, converts them to text, and, using a simple ML model based on the Random Forest algorithm, determines whether the first 10 pages of the document contain a table of contents, and if so, on which page it is located.

## Required Libraries
- Tkinter
- Pdf2image (poppler)
- Pytesseract
- Os
- Shutil
- Re
- Numpy
- Sklern
- 
##How to use
To use the script, you will need Python 3.12.3, the necessary libraries, and installed Poppler and Tesseract (their links must also be added to the system PATH).  

The script is launched via "ReadPDFfiles.py". After that, using the Tkinter library, you will be prompted to select a PDF file in which you need to find the table of contents. Once you select it, the first 10 pages will be converted to images using Pdf2image. These images   are then converted to text using Tesseract OCR. The extracted text is sent to the ML model script (toc_model.py) for analysis, where, based on primitive examples, it determines whether a page is a table of contents or not. The output is a list of the first 10 pages   indicating whether each page is a table of contents or regular text, along with the confidence level for each page.  
