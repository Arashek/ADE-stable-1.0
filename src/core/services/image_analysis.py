import cv2
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
import tensorflow as tf
from PIL import Image
import io

class ImageAnalysisService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.labels = []
        self._load_model()
        
    def _load_model(self):
        """
        Load the pre-trained model for image analysis
        """
        try:
            # Load MobileNetV2 model
            self.model = tf.keras.applications.MobileNetV2(
                weights='imagenet',
                include_top=True
            )
            
            # Load ImageNet labels
            with open('imagenet_labels.txt', 'r') as f:
                self.labels = [line.strip() for line in f.readlines()]
                
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            raise

    async def analyze_image(self, image_path: Path) -> Dict[str, Any]:
        """
        Analyze image content and extract features
        """
        try:
            # Read and preprocess image
            image = await self._preprocess_image(image_path)
            
            # Perform analysis
            analysis_results = {
                "objects": await self._detect_objects(image),
                "faces": await self._detect_faces(image),
                "text": await self._detect_text(image),
                "colors": await self._analyze_colors(image),
                "metadata": await self._extract_metadata(image_path)
            }
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Image analysis failed: {str(e)}")
            raise

    async def _preprocess_image(self, image_path: Path) -> np.ndarray:
        """
        Preprocess image for analysis
        """
        try:
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError("Failed to read image")
            
            # Convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize if needed
            max_dimension = 1024
            height, width = image.shape[:2]
            if max(height, width) > max_dimension:
                scale = max_dimension / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            return image
            
        except Exception as e:
            self.logger.error(f"Image preprocessing failed: {str(e)}")
            raise

    async def _detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect objects in the image using MobileNetV2
        """
        try:
            # Prepare image for model
            img_array = tf.keras.preprocessing.image.img_to_array(image)
            img_array = tf.expand_dims(img_array, 0)
            img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
            
            # Get predictions
            predictions = self.model.predict(img_array)
            
            # Get top 5 predictions
            top_indices = np.argsort(predictions[0])[-5:][::-1]
            
            results = []
            for idx in top_indices:
                results.append({
                    "label": self.labels[idx],
                    "confidence": float(predictions[0][idx])
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Object detection failed: {str(e)}")
            return []

    async def _detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect faces in the image
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Load face detection model
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            results = []
            for (x, y, w, h) in faces:
                results.append({
                    "box": {
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h)
                    },
                    "confidence": 1.0  # Haar cascade doesn't provide confidence
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Face detection failed: {str(e)}")
            return []

    async def _detect_text(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect text regions in the image
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply thresholding
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(
                binary,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            results = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter small regions
                if w < 20 or h < 20:
                    continue
                
                # Calculate aspect ratio
                aspect_ratio = w / h
                if aspect_ratio < 0.1 or aspect_ratio > 10:
                    continue
                
                results.append({
                    "box": {
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h)
                    },
                    "confidence": 1.0
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Text detection failed: {str(e)}")
            return []

    async def _analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze dominant colors in the image
        """
        try:
            # Reshape image to list of pixels
            pixels = image.reshape(-1, 3)
            
            # Convert to float32
            pixels = np.float32(pixels)
            
            # Define criteria for k-means
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 100, 0.2)
            
            # Perform k-means clustering
            _, labels, centers = cv2.kmeans(pixels, 5, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers to uint8
            centers = np.uint8(centers)
            
            # Get color counts
            unique_labels, counts = np.unique(labels, return_counts=True)
            
            # Calculate percentages
            total_pixels = sum(counts)
            color_percentages = (counts / total_pixels) * 100
            
            # Create results
            results = []
            for i, (color, percentage) in enumerate(zip(centers, color_percentages)):
                results.append({
                    "rgb": color.tolist(),
                    "percentage": float(percentage)
                })
            
            return {
                "dominant_colors": results,
                "total_colors": len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Color analysis failed: {str(e)}")
            return {"dominant_colors": [], "total_colors": 0}

    async def _extract_metadata(self, image_path: Path) -> Dict[str, Any]:
        """
        Extract image metadata
        """
        try:
            with Image.open(image_path) as img:
                metadata = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "info": img.info
                }
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    metadata["exif"] = {
                        str(tag): str(value)
                        for tag, value in exif.items()
                    }
                
                return metadata
                
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {str(e)}")
            return {}

    async def generate_thumbnail(
        self,
        image_path: Path,
        size: tuple = (200, 200)
    ) -> bytes:
        """
        Generate a thumbnail of the image
        """
        try:
            with Image.open(image_path) as img:
                # Calculate aspect ratio
                aspect_ratio = img.width / img.height
                
                # Calculate new dimensions
                if aspect_ratio > 1:
                    new_width = size[0]
                    new_height = int(size[0] / aspect_ratio)
                else:
                    new_height = size[1]
                    new_width = int(size[1] * aspect_ratio)
                
                # Resize image
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=85)
                img_byte_arr = img_byte_arr.getvalue()
                
                return img_byte_arr
                
        except Exception as e:
            self.logger.error(f"Thumbnail generation failed: {str(e)}")
            raise 