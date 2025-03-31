from typing import Dict, List, Any, Type, Optional
from datetime import datetime
import json
from pydantic import BaseModel, ValidationError
from bson import ObjectId

class DataValidator:
    """Utility class for validating data integrity and consistency"""
    
    @staticmethod
    def compare_documents(doc1: Dict[str, Any], doc2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two documents and return differences
        
        Args:
            doc1: First document
            doc2: Second document
            
        Returns:
            Dict containing differences and their values
        """
        differences = {}
        
        # Convert ObjectId to string for comparison
        doc1 = {k: str(v) if isinstance(v, ObjectId) else v for k, v in doc1.items()}
        doc2 = {k: str(v) if isinstance(v, ObjectId) else v for k, v in doc2.items()}
        
        # Compare all fields
        all_keys = set(doc1.keys()) | set(doc2.keys())
        for key in all_keys:
            if key not in doc1:
                differences[key] = {"doc1": None, "doc2": doc2[key]}
            elif key not in doc2:
                differences[key] = {"doc1": doc1[key], "doc2": None}
            elif doc1[key] != doc2[key]:
                differences[key] = {"doc1": doc1[key], "doc2": doc2[key]}
                
        return differences
    
    @staticmethod
    def validate_schema(data: Dict[str, Any], model_class: Type[BaseModel]) -> Optional[str]:
        """
        Validate data against a Pydantic model schema
        
        Args:
            data: Data to validate
            model_class: Pydantic model class
            
        Returns:
            Error message if validation fails, None otherwise
        """
        try:
            model_class(**data)
            return None
        except ValidationError as e:
            return str(e)
    
    @staticmethod
    def check_referential_integrity(
        documents: List[Dict[str, Any]],
        reference_field: str,
        collection_name: str
    ) -> List[Dict[str, Any]]:
        """
        Check referential integrity of documents
        
        Args:
            documents: List of documents to check
            reference_field: Field containing reference IDs
            collection_name: Name of the referenced collection
            
        Returns:
            List of documents with broken references
        """
        broken_refs = []
        
        for doc in documents:
            ref_id = doc.get(reference_field)
            if ref_id and not isinstance(ref_id, (str, ObjectId)):
                broken_refs.append({
                    "document_id": str(doc.get("_id")),
                    "collection": collection_name,
                    "reference_field": reference_field,
                    "invalid_reference": ref_id,
                    "error": "Invalid reference type"
                })
                
        return broken_refs
    
    @staticmethod
    def check_data_corruption(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check for data corruption in documents
        
        Args:
            documents: List of documents to check
            
        Returns:
            List of corrupted documents with error details
        """
        corrupted = []
        
        for doc in documents:
            # Check for invalid ObjectId
            if "_id" in doc and not isinstance(doc["_id"], ObjectId):
                corrupted.append({
                    "document_id": str(doc.get("_id")),
                    "error": "Invalid ObjectId"
                })
                continue
                
            # Check for invalid dates
            for key, value in doc.items():
                if isinstance(value, str):
                    try:
                        datetime.fromisoformat(value)
                    except ValueError:
                        corrupted.append({
                            "document_id": str(doc.get("_id")),
                            "field": key,
                            "value": value,
                            "error": "Invalid date format"
                        })
                        
            # Check for circular references in nested structures
            try:
                json.dumps(doc)
            except (TypeError, ValueError) as e:
                corrupted.append({
                    "document_id": str(doc.get("_id")),
                    "error": f"Circular reference or invalid JSON: {str(e)}"
                })
                
        return corrupted
    
    @staticmethod
    def validate_indexes(
        collection_indexes: List[Dict[str, Any]],
        required_indexes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate that all required indexes exist
        
        Args:
            collection_indexes: List of existing indexes
            required_indexes: List of required indexes
            
        Returns:
            List of missing or invalid indexes
        """
        missing_indexes = []
        
        for required in required_indexes:
            found = False
            for existing in collection_indexes:
                if existing.get("name") == required.get("name"):
                    if existing.get("key") == required.get("key"):
                        found = True
                        break
            if not found:
                missing_indexes.append({
                    "index": required.get("name"),
                    "error": "Missing or invalid index"
                })
                
        return missing_indexes 