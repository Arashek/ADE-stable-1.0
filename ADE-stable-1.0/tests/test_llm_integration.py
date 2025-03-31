import unittest
import numpy as np
from pathlib import Path
import tempfile
import shutil
from datetime import datetime, timedelta

from src.core.llm.llm_client import LLMClient, ErrorAnalysis
from src.core.llm.vector_store import VectorStore, ErrorEmbedding

class TestLLMIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.json"
        self.index_path = Path(self.temp_dir) / "test.index"
        
        # Initialize clients
        self.llm_client = LLMClient(str(self.config_path))
        self.vector_store = VectorStore(str(self.index_path))
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        
    def test_llm_error_analysis(self):
        """Test LLM error analysis functionality."""
        # Test error message
        error_message = "TypeError: 'NoneType' object is not subscriptable"
        stack_trace = [
            "File 'test.py', line 10, in process_data",
            "result = data['key']",
            "TypeError: 'NoneType' object is not subscriptable"
        ]
        patterns = [
            {
                "type": "type_error",
                "description": "Attempting to access dictionary key on None value"
            }
        ]
        context = {
            "file": "test.py",
            "function": "process_data",
            "line": 10
        }
        
        # Get analysis from LLM
        analysis = self.llm_client.analyze_error(
            error_message,
            stack_trace,
            patterns,
            context
        )
        
        # Verify analysis structure
        self.assertIsInstance(analysis, ErrorAnalysis)
        self.assertIsInstance(analysis.primary_cause, str)
        self.assertIsInstance(analysis.contributing_factors, list)
        self.assertIsInstance(analysis.suggested_fixes, list)
        self.assertIsInstance(analysis.confidence_score, float)
        self.assertIsInstance(analysis.reasoning, str)
        
        # Verify analysis content
        self.assertTrue(len(analysis.primary_cause) > 0)
        self.assertTrue(len(analysis.contributing_factors) > 0)
        self.assertTrue(len(analysis.suggested_fixes) > 0)
        self.assertTrue(0 <= analysis.confidence_score <= 1)
        
    def test_vector_store_operations(self):
        """Test vector store operations."""
        # Create test data
        error_id = "test_error_1"
        embedding = np.random.rand(1536).astype(np.float32)
        metadata = {
            "error_type": "TypeError",
            "message": "Test error message",
            "file": "test.py",
            "line": 10
        }
        
        # Test adding error
        self.vector_store.add_error(error_id, embedding, metadata)
        
        # Test retrieving error
        retrieved = self.vector_store.get_error(error_id)
        self.assertIsInstance(retrieved, ErrorEmbedding)
        self.assertEqual(retrieved.error_id, error_id)
        np.testing.assert_array_equal(retrieved.embedding, embedding)
        self.assertEqual(retrieved.metadata, metadata)
        
        # Test finding similar errors
        similar_errors = self.vector_store.find_similar_errors(
            embedding,
            k=1,
            threshold=0.8
        )
        self.assertEqual(len(similar_errors), 1)
        self.assertEqual(similar_errors[0]["error_id"], error_id)
        
        # Test updating error
        new_metadata = {"line": 20}
        self.vector_store.update_error(error_id, metadata=new_metadata)
        updated = self.vector_store.get_error(error_id)
        self.assertEqual(updated.metadata["line"], 20)
        
        # Test deleting error
        self.vector_store.delete_error(error_id)
        self.assertIsNone(self.vector_store.get_error(error_id))
        
    def test_vector_store_persistence(self):
        """Test vector store persistence."""
        # Add test data
        error_id = "test_error_2"
        embedding = np.random.rand(1536).astype(np.float32)
        metadata = {"test": "data"}
        self.vector_store.add_error(error_id, embedding, metadata)
        
        # Save index
        self.vector_store.save_index()
        
        # Create new vector store instance
        new_store = VectorStore(str(self.index_path))
        
        # Verify data persistence
        retrieved = new_store.get_error(error_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.error_id, error_id)
        np.testing.assert_array_equal(retrieved.embedding, embedding)
        self.assertEqual(retrieved.metadata, metadata)
        
    def test_error_analysis_integration(self):
        """Test integration between LLM and vector store."""
        # Create test error
        error_message = "ValueError: Invalid input"
        stack_trace = ["File 'test.py', line 5, in validate_input"]
        patterns = [{"type": "validation_error", "description": "Invalid input format"}]
        context = {"input_type": "string", "expected_format": "email"}
        
        # Get LLM analysis
        analysis = self.llm_client.analyze_error(
            error_message,
            stack_trace,
            patterns,
            context
        )
        
        # Create embedding (simulated)
        embedding = np.random.rand(1536).astype(np.float32)
        
        # Store in vector store
        error_id = "test_error_3"
        metadata = {
            "error_message": error_message,
            "analysis": {
                "primary_cause": analysis.primary_cause,
                "contributing_factors": analysis.contributing_factors,
                "suggested_fixes": analysis.suggested_fixes,
                "confidence_score": analysis.confidence_score
            },
            "context": context
        }
        
        self.vector_store.add_error(error_id, embedding, metadata)
        
        # Verify storage and retrieval
        retrieved = self.vector_store.get_error(error_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.metadata["error_message"], error_message)
        self.assertEqual(
            retrieved.metadata["analysis"]["primary_cause"],
            analysis.primary_cause
        )
        
    def test_batch_error_analysis(self):
        """Test batch error analysis functionality."""
        # Create test errors
        errors = [
            {
                "message": "TypeError: 'NoneType' object is not subscriptable",
                "type": "TypeError",
                "context": {"file": "test1.py", "line": 10}
            },
            {
                "message": "ValueError: Invalid input format",
                "type": "ValueError",
                "context": {"file": "test2.py", "line": 15}
            }
        ]
        
        # Get batch analysis
        analyses = self.llm_client.analyze_errors_batch(errors)
        
        # Verify results
        self.assertEqual(len(analyses), 2)
        for analysis in analyses:
            self.assertIsInstance(analysis, ErrorAnalysis)
            self.assertTrue(len(analysis.primary_cause) > 0)
            self.assertTrue(len(analysis.contributing_factors) > 0)
            self.assertTrue(len(analysis.suggested_fixes) > 0)
            self.assertTrue(0 <= analysis.confidence_score <= 1)

    def test_error_fix_generation(self):
        """Test error fix generation functionality."""
        # Create test error
        error = {
            "message": "IndexError: list index out of range",
            "type": "IndexError",
            "location": "test.py:20",
            "context": {
                "list_length": 0,
                "attempted_index": 5
            }
        }
        
        # Generate fix
        fix = self.llm_client.generate_error_fix(error)
        
        # Verify fix structure
        self.assertIsInstance(fix, dict)
        self.assertIn("code", fix)
        self.assertIn("explanation", fix)
        self.assertIn("considerations", fix)
        self.assertIn("alternatives", fix)
        
        # Verify content
        self.assertTrue(len(fix["code"]) > 0)
        self.assertTrue(len(fix["explanation"]) > 0)
        self.assertIsInstance(fix["considerations"], list)
        self.assertIsInstance(fix["alternatives"], list)

    def test_error_prevention_suggestions(self):
        """Test error prevention suggestions functionality."""
        # Create test patterns
        patterns = [
            {
                "type": "null_pointer",
                "frequency": 5,
                "description": "Accessing properties of null objects"
            },
            {
                "type": "index_error",
                "frequency": 3,
                "description": "Accessing invalid array indices"
            }
        ]
        
        # Get prevention suggestions
        suggestions = self.llm_client.suggest_error_prevention(patterns)
        
        # Verify suggestions structure
        self.assertIsInstance(suggestions, dict)
        self.assertIn("strategies", suggestions)
        self.assertIn("best_practices", suggestions)
        self.assertIn("code_examples", suggestions)
        self.assertIn("monitoring", suggestions)
        
        # Verify content
        self.assertIsInstance(suggestions["strategies"], list)
        self.assertIsInstance(suggestions["best_practices"], list)
        self.assertIsInstance(suggestions["code_examples"], list)
        self.assertIsInstance(suggestions["monitoring"], list)

    def test_vector_store_clustering(self):
        """Test error clustering functionality."""
        # Add test data
        for i in range(10):
            error_id = f"test_error_{i}"
            embedding = np.random.rand(1536).astype(np.float32)
            metadata = {
                "error_type": "test_error",
                "severity": i % 3,
                "location": f"test_{i}.py"
            }
            self.vector_store.add_error(error_id, embedding, metadata)
        
        # Perform clustering
        clusters = self.vector_store.cluster_errors(n_clusters=3)
        
        # Verify cluster structure
        self.assertIn("clusters", clusters)
        self.assertIn("statistics", clusters)
        self.assertIsInstance(clusters["clusters"], dict)
        self.assertIsInstance(clusters["statistics"], dict)
        
        # Verify cluster statistics
        stats = clusters["statistics"]
        self.assertIn("total_clusters", stats)
        self.assertIn("total_errors", stats)
        self.assertIn("cluster_sizes", stats)
        self.assertIn("cluster_centroids", stats)

    def test_error_trend_analysis(self):
        """Test error trend analysis functionality."""
        # Add test data with timestamps
        now = datetime.utcnow()
        for i in range(5):
            error_id = f"trend_error_{i}"
            embedding = np.random.rand(1536).astype(np.float32)
            metadata = {
                "error_type": "test_error",
                "severity": i % 3,
                "location": f"test_{i}.py"
            }
            # Set timestamps within last 7 days
            timestamp = now - timedelta(days=i)
            self.vector_store.add_error(error_id, embedding, metadata)
        
        # Analyze trends
        trends = self.vector_store.analyze_error_trends(time_window=7)
        
        # Verify trend structure
        self.assertIn("time_window", trends)
        self.assertIn("total_errors", trends)
        self.assertIn("error_types", trends)
        self.assertIn("trends", trends)
        
        # Verify trend data
        self.assertEqual(trends["time_window"], 7)
        self.assertEqual(trends["total_errors"], 5)
        self.assertIsInstance(trends["trends"], dict)

    def test_metadata_filtering(self):
        """Test metadata filtering functionality."""
        # Add test data with different metadata
        for i in range(5):
            error_id = f"filter_error_{i}"
            embedding = np.random.rand(1536).astype(np.float32)
            metadata = {
                "error_type": "test_error",
                "severity": i % 3,
                "location": f"test_{i}.py",
                "component": "frontend" if i < 2 else "backend"
            }
            self.vector_store.add_error(error_id, embedding, metadata)
        
        # Test filtering
        criteria = {"component": "frontend"}
        matches = self.vector_store.filter_by_metadata(criteria)
        
        # Verify filter results
        self.assertEqual(len(matches), 2)
        for match in matches:
            self.assertEqual(match["metadata"]["component"], "frontend")
            self.assertIn("error_id", match)
            self.assertIn("metadata", match)
            self.assertIn("timestamp", match)
            self.assertIn("embedding", match)

    def test_error_statistics(self):
        """Test error statistics functionality."""
        # Add test data
        for i in range(5):
            error_id = f"stats_error_{i}"
            embedding = np.random.rand(1536).astype(np.float32)
            metadata = {
                "error_type": "test_error",
                "severity": i % 3,
                "location": f"test_{i}.py",
                "component": "frontend" if i < 2 else "backend"
            }
            self.vector_store.add_error(error_id, embedding, metadata)
        
        # Get basic statistics
        stats = self.vector_store.get_error_statistics()
        
        # Verify basic statistics
        self.assertIn("total_errors", stats)
        self.assertIn("error_types", stats)
        self.assertIn("severity_distribution", stats)
        self.assertIn("timestamp_range", stats)
        
        # Get grouped statistics
        grouped_stats = self.vector_store.get_error_statistics(group_by="component")
        
        # Verify grouped statistics
        self.assertIn("grouped_statistics", grouped_stats)
        self.assertEqual(len(grouped_stats["grouped_statistics"]), 2)
        for component_stats in grouped_stats["grouped_statistics"].values():
            self.assertIn("count", component_stats)
            self.assertIn("error_types", component_stats)
            self.assertIn("severity_distribution", component_stats)

if __name__ == '__main__':
    unittest.main() 