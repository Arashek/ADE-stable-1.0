import pytesseract
from PIL import Image
import numpy as np
import cv2
from typing import Dict, Any, Optional
import logging
from pathlib import Path

class OCRService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_languages = pytesseract.get_languages()
        
    async def process_image(self, image_path: Path) -> Dict[str, Any]:
        """
        Process an image to extract text using OCR
        """
        try:
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError("Failed to read image")

            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Perform OCR
            ocr_result = pytesseract.image_to_data(
                processed_image,
                output_type=pytesseract.Output.DICT,
                lang='eng'
            )
            
            # Process results
            processed_result = self._process_ocr_result(ocr_result)
            
            return {
                "text": processed_result["text"],
                "confidence": processed_result["confidence"],
                "blocks": processed_result["blocks"],
                "language": "eng",
                "processing_time": processed_result["processing_time"]
            }
            
        except Exception as e:
            self.logger.error(f"OCR processing failed: {str(e)}")
            raise

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image to improve OCR accuracy
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to preprocess the image
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Apply dilation to connect text components
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            gray = cv2.dilate(gray, kernel, iterations=1)
            
            # Apply median blur to remove noise
            gray = cv2.medianBlur(gray, 3)
            
            # Apply erosion to remove noise
            gray = cv2.erode(gray, kernel, iterations=1)
            
            return gray
            
        except Exception as e:
            self.logger.error(f"Image preprocessing failed: {str(e)}")
            return image

    def _process_ocr_result(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw OCR results into a structured format
        """
        try:
            # Extract text blocks
            blocks = []
            current_block = []
            current_line = []
            
            for i in range(len(ocr_result["text"])):
                if ocr_result["text"][i].strip():
                    current_line.append({
                        "text": ocr_result["text"][i],
                        "confidence": ocr_result["conf"][i],
                        "box": {
                            "x": ocr_result["left"][i],
                            "y": ocr_result["top"][i],
                            "width": ocr_result["width"][i],
                            "height": ocr_result["height"][i]
                        }
                    })
                elif current_line:
                    current_block.append(current_line)
                    current_line = []
                    
                if ocr_result["block_num"][i] != ocr_result["block_num"][i-1] if i > 0 else False:
                    if current_line:
                        current_block.append(current_line)
                    if current_block:
                        blocks.append(current_block)
                    current_block = []
                    current_line = []
            
            # Add any remaining lines and blocks
            if current_line:
                current_block.append(current_line)
            if current_block:
                blocks.append(current_block)
            
            # Calculate overall confidence
            confidences = [conf for conf in ocr_result["conf"] if conf != -1]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Combine text
            text = " ".join([word for word in ocr_result["text"] if word.strip()])
            
            return {
                "text": text,
                "confidence": avg_confidence,
                "blocks": blocks,
                "processing_time": ocr_result.get("processing_time", 0)
            }
            
        except Exception as e:
            self.logger.error(f"OCR result processing failed: {str(e)}")
            raise

    async def detect_language(self, image_path: Path) -> str:
        """
        Detect the language of text in an image
        """
        try:
            image = Image.open(image_path)
            lang = pytesseract.image_to_osd(image)
            return lang.split('\n')[0].split(':')[1].strip()
        except Exception as e:
            self.logger.error(f"Language detection failed: {str(e)}")
            return "eng"

    def get_supported_languages(self) -> list:
        """
        Get list of supported languages
        """
        return self.supported_languages

    async def process_image_with_language(
        self,
        image_path: Path,
        language: str
    ) -> Dict[str, Any]:
        """
        Process an image with a specific language
        """
        if language not in self.supported_languages:
            raise ValueError(f"Unsupported language: {language}")
            
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError("Failed to read image")

            processed_image = self._preprocess_image(image)
            
            ocr_result = pytesseract.image_to_data(
                processed_image,
                output_type=pytesseract.Output.DICT,
                lang=language
            )
            
            return self._process_ocr_result(ocr_result)
            
        except Exception as e:
            self.logger.error(f"OCR processing failed for language {language}: {str(e)}")
            raise 