# from pdf2image import convert_from_path

# import os



# def convert_pdf_to_jpg(pdf_path, output_folder):
#     """
#     Convert a PDF file to JPG images.
#     Parameters:
#     - pdf_path (str): The path to the PDF file to be converted.
#     - output_folder (str): The folder where the JPG images will be saved.
#     Returns:
#     - List of str: The filepaths of the generated JPG images.
#     """

#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
#     jpg_filepaths = []
#     images = convert_from_path(pdf_path)

#     for i, image in enumerate(images):
#         jpg_filepath = os.path.join(output_folder, f"image_{i+1}.jpg")
#         image.save(jpg_filepath, 'JPEG')
#         jpg_filepaths.append(jpg_filepath)



#     return jpg_filepaths

import fitz  # PyMuPDF
import os

def convert_pdf_to_jpg(pdf_path, output_folder, custom_name=None):
    doc = fitz.open(pdf_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Extraer el nombre base del archivo PDF si no se proporciona un nombre personalizado
    base_name = custom_name if custom_name else os.path.splitext(os.path.basename(pdf_path))[0]

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        
        # Utilizar el nombre base y añadir el número de página
        output_image_name = f"{base_name}_page{page_num+1}.jpg"
        output_image_path = os.path.join(output_folder, output_image_name)
        
        try:
            pix.save(output_image_path, output="jpg")
            print(f"Page {page_num+1} saved at {output_image_path}")
            return output_image_path
        except Exception as e:
            print(f"An error occurred while saving page {page_num+1}: {e}")



if __name__ == "__main__":
    pdf_path = "pdfs/42b3387eb82c4e769384f0dd142a9eed.pdf"
    output_folder = "jpgs/"

    convert_pdf_to_jpg(pdf_path, output_folder)