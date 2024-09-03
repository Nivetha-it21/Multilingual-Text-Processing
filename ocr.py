import cv2
import os
import PyPDF2
from langdetect import detect
import easyocr
import fitz  # PyMuPDF
import io
import numpy as np
from deep_translator import GoogleTranslator

class ImageOCR:
    def __init__(self, file_path):
        self.file_path = file_path

    def convert_to_jpeg(self):
        _, file_extension = os.path.splitext(self.file_path)
        if file_extension.lower() not in ['.jpg', '.jpeg']:
            img = cv2.imread(self.file_path)
            jpeg_image_path = os.path.splitext(self.file_path)[0] + '.jpeg'
            cv2.imwrite(jpeg_image_path, img)
            self.file_path = jpeg_image_path

    def process_pdf_and_summarize(self):
        # Extract text from PDF
        pdf_text = self.extract_text_from_pdf()
        print("Recognized Text from PDF:")
        print(pdf_text)

        # Extract and process images from PDF
        image_text = self.extract_and_process_images_from_pdf()
        combined_text = pdf_text + " " + image_text
        print("Combined Text from PDF and Images:")
        print(combined_text)

        if combined_text.strip():
            original_language = self.detect_language(combined_text)
            print("Original Language:", original_language)

            target_language = self.select_target_language()
            translated_text = self.translate_text(combined_text, target_language)
            print("Translated Text from PDF and Images:")
            print(translated_text)
        else:
            print("No text could be extracted from the PDF or images.")

    def extract_text_from_pdf(self):
        pdf_text = ""
        try:
            with open(self.file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text() + " "
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return pdf_text.strip()

    def translate_text(self, text, target_language='en'):
        try:
            translator = GoogleTranslator(source='auto', target=target_language)
            translated = translator.translate(text)
            return translated
        except Exception as e:
            print(f"Error during translation: {e}")
            return "Translation error"

    def select_target_language(self):
        print("Select a target language for translation:")
        print("1. Hindi")
        print("2. French")
        print("3. Spanish")
        print("4. Chinese")
        print("5. English")
        choice = input("Enter the number of your choice: ")
        languages = {'1': 'hi', '2': 'fr', '3': 'es', '4': 'zh-cn', '5': 'en'}
        return languages.get(choice, 'en')

    def detect_language(self, text):
        try:
            detected_lang = detect(text)
        except Exception as e:
            print(f"Error during language detection: {e}")
            detected_lang = "unknown"
        return detected_lang

    def perform_easyocr(self, image_bytes):
        try:
            reader = easyocr.Reader(['en'], gpu=True)
            result = reader.readtext(image_bytes)
            return " ".join([item[1] for item in result])
        except Exception as e:
            print(f"Error during OCR: {e}")
            return ""

    def extract_and_process_images_from_pdf(self):
        text_from_images = ""
        try:
            with fitz.open(self.file_path) as doc:
                for page in doc:
                    image_list = page.get_images(full=True)
                    for image_index, img in enumerate(image_list):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        # Perform OCR on the image
                        image_text = self.perform_easyocr(io.BytesIO(image_bytes))
                        text_from_images += image_text + " "
        except Exception as e:
            print(f"Error extracting images from PDF: {e}")
        return text_from_images.strip()

if __name__ == "__main__":
    file_path = input("Enter the path of the PDF or image: ")
    ocr_processor = ImageOCR(file_path)

    if file_path.lower().endswith((".pdf", ".jpg", ".jpeg", ".png")):
        ocr_processor.process_pdf_and_summarize()
    else:
        print("Invalid file format. Supported formats: PDF, JPG, JPEG, PNG.")
