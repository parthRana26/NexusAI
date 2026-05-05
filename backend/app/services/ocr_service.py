import requests
import os
from app.core.config import settings

class OCRService:
    @staticmethod
    def extract_text_from_image(file_path: str) -> str:
        """
        Extract text from image or PDF using OCR.space API.
        """
        try:
            url = "https://api.ocr.space/parse/image"
            with open(file_path, "rb") as f:
                payload = {
                    "apikey": settings.OCR_API_KEY,
                    "language": "eng",
                    "isOverlayRequired": False,
                    "FileType": os.path.splitext(file_path)[1].lower().replace(".", ""),
                    "isTable": True, # Better for financial documents
                }
                files = {"file": f}
                response = requests.post(url, data=payload, files=files)
                result = response.json()

                if result.get("IsErroredOnProcessing"):
                    print(f"OCR Error: {result.get('ErrorMessage')}")
                    return ""

                parsed_results = result.get("ParsedResults")
                if not parsed_results:
                    return ""

                extracted_text = ""
                for res in parsed_results:
                    extracted_text += res.get("ParsedText", "") + "\n"
                
                return extracted_text
        except Exception as e:
            print(f"OCR Service Exception: {e}")
            return ""

ocr_service = OCRService()
