import pdfplumber
pdf_file_path = f'/Users/chenyue/Desktop/Haizi_Poem_Explorer/HaiziPoems.pdf'
txt_file_path = f'/Users/chenyue/Desktop/Haizi_Poem_Explorer/HaiziPoems_PureText.txt'
with pdfplumber.open(pdf_file_path) as pdf:
    with open(txt_file_path,mode='w') as text:
        for page in pdf.pages[48:872]:
            text.write(page.extract_text())
    