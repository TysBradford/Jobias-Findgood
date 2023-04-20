import docx
import os
import PyPDF2
    
def read_cv_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension in ['.doc', '.docx']:
        return read_word_to_string(file_path)
    elif file_extension == '.txt':
        return read_txt_to_string(file_path)
    elif file_extension == '.pdf':
        return read_pdf_to_string(file_path)
    else:
        raise ValueError('Unsupported file format')
    
def read_pdf_to_string(pdf_file):
  with open(pdf_file, 'rb' ) as file:
      pdf_reader = PyPDF2.PdfReader(file)
      pdf_text = ''

      for page_num in range(len(pdf_reader.pages)):
          page = pdf_reader.pages[page_num]
          pdf_text += page.extract_text()

  return pdf_text

def read_word_to_string(doc_file):
    doc = docx.Document(doc_file)
    doc_text = ''

    for paragraph in doc.paragraphs:
        doc_text += paragraph.text + '\n'
    return doc_text

def read_txt_to_string(txt_file):
    with open(txt_file, 'r') as file:
        return file.read()