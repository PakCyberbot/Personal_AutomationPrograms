import fitz  # PyMuPDF
import os
from PIL import Image

def pdf_to_image(pdf_path, output_folder, dpi=300):
    pdf_document = fitz.open(pdf_path)

    page = pdf_document.load_page(0)

    pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]

    image_options = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))

    temp_image_path = os.path.join(output_folder, f"{pdf_filename}_temp.png")
    image_options.save(temp_image_path)

    image = Image.open(temp_image_path)
    image.save(os.path.join(output_folder, f"{pdf_filename}.png"), dpi=(dpi, dpi))

    pdf_document.close()

    os.remove(temp_image_path)

def convert_pdfs_in_directory(directory):
    files = os.listdir(directory)

    pdf_files = [file for file in files if file.endswith(".pdf")]

    for pdf_file in pdf_files:
        pdf_path = os.path.join(directory, pdf_file)
        output_directory = "output_images"  

        os.makedirs(output_directory, exist_ok=True)

        pdf_to_image(pdf_path, output_directory, dpi=300)

if __name__ == "__main__":
    current_directory = os.getcwd() 
    input_pdf_path = os.path.join(current_directory,'PDF_FILES')
    if not os.path.exists(input_pdf_path):
        os.mkdir(input_pdf_path)

    convert_pdfs_in_directory(input_pdf_path)
