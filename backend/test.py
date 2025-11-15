from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
img = Image.open('path/to/sample_image.png')  # Use a test image
text = pytesseract.image_to_string(img)
print(text)
