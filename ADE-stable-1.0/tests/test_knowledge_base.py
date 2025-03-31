import unittest
from datetime import datetime
import tempfile
import os
from pathlib import Path

from src.core.analysis.error_knowledge_base import (
    ErrorKnowledgeBase, ErrorPattern, ErrorSolution
)
from src.core.analysis.similarity_search import SimilaritySearch, SearchResult

class TestErrorKnowledgeBase(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.knowledge_base = ErrorKnowledgeBase(storage_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_add_pattern(self):
        """Test adding error patterns to the knowledge base."""
        pattern = ErrorPattern(
            pattern_type="test_pattern",
            regex="test.*error",
            description="Test error pattern",
            severity="medium",
            category="runtime",
            subcategory="general",
            common_causes=["test cause"],
            solutions=["sol_001"],
            examples=["test error example"]
        )
        self.knowledge_base.add_pattern("test_001", pattern)
        retrieved = self.knowledge_base.get_pattern("test_001")
        self.assertEqual(retrieved.pattern_type, pattern.pattern_type)
    
    def test_add_solution(self):
        """Test adding solutions to the knowledge base."""
        solution = ErrorSolution(
            solution_id="sol_001",
            description="Test solution",
            steps=["step 1", "step 2"],
            prerequisites=["prereq 1"],
            success_criteria=["criteria 1"]
        )
        self.knowledge_base.add_solution("sol_001", solution)
        retrieved = self.knowledge_base.get_solution("sol_001")
        self.assertEqual(retrieved.solution_id, solution.solution_id)
    
    def test_pattern_solutions(self):
        """Test retrieving solutions for a pattern."""
        pattern = ErrorPattern(
            pattern_type="test_pattern",
            regex="test.*error",
            description="Test error pattern",
            severity="medium",
            category="runtime",
            subcategory="general",
            common_causes=["test cause"],
            solutions=["sol_001", "sol_002"],
            examples=["test error example"]
        )
        solution1 = ErrorSolution(
            solution_id="sol_001",
            description="Test solution 1",
            steps=["step 1"],
            prerequisites=["prereq 1"],
            success_criteria=["criteria 1"]
        )
        solution2 = ErrorSolution(
            solution_id="sol_002",
            description="Test solution 2",
            steps=["step 2"],
            prerequisites=["prereq 2"],
            success_criteria=["criteria 2"]
        )
        
        self.knowledge_base.add_pattern("test_001", pattern)
        self.knowledge_base.add_solution("sol_001", solution1)
        self.knowledge_base.add_solution("sol_002", solution2)
        
        solutions = self.knowledge_base.get_pattern_solutions("test_001")
        self.assertEqual(len(solutions), 2)
        self.assertEqual(solutions[0].solution_id, "sol_001")
        self.assertEqual(solutions[1].solution_id, "sol_002")
    
    def test_category_patterns(self):
        """Test retrieving patterns by category."""
        pattern1 = ErrorPattern(
            pattern_type="test_pattern1",
            regex="test1.*error",
            description="Test error pattern 1",
            severity="medium",
            category="runtime",
            subcategory="general",
            common_causes=["test cause 1"],
            solutions=["sol_001"],
            examples=["test error example 1"]
        )
        pattern2 = ErrorPattern(
            pattern_type="test_pattern2",
            regex="test2.*error",
            description="Test error pattern 2",
            severity="high",
            category="database",
            subcategory="connection",
            common_causes=["test cause 2"],
            solutions=["sol_002"],
            examples=["test error example 2"]
        )
        
        self.knowledge_base.add_pattern("test_001", pattern1)
        self.knowledge_base.add_pattern("test_002", pattern2)
        
        runtime_patterns = self.knowledge_base.get_category_patterns("runtime")
        self.assertEqual(len(runtime_patterns), 1)
        self.assertEqual(runtime_patterns[0].pattern_type, "test_pattern1")
        
        db_patterns = self.knowledge_base.get_category_patterns("database")
        self.assertEqual(len(db_patterns), 1)
        self.assertEqual(db_patterns[0].pattern_type, "test_pattern2")
    
    def test_search_patterns(self):
        """Test pattern search functionality."""
        pattern1 = ErrorPattern(
            pattern_type="test_pattern1",
            regex="test1.*error",
            description="Test error pattern 1",
            severity="medium",
            category="runtime",
            subcategory="general",
            common_causes=["test cause 1"],
            solutions=["sol_001"],
            examples=["test error example 1"]
        )
        pattern2 = ErrorPattern(
            pattern_type="test_pattern2",
            regex="test2.*error",
            description="Test error pattern 2",
            severity="high",
            category="database",
            subcategory="connection",
            common_causes=["test cause 2"],
            solutions=["sol_002"],
            examples=["test error example 2"]
        )
        
        self.knowledge_base.add_pattern("test_001", pattern1)
        self.knowledge_base.add_pattern("test_002", pattern2)
        
        results = self.knowledge_base.search_patterns("test error")
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.pattern_type.startswith("test_pattern") for r in results))
    
    def test_statistics(self):
        """Test knowledge base statistics."""
        pattern = ErrorPattern(
            pattern_type="test_pattern",
            regex="test.*error",
            description="Test error pattern",
            severity="medium",
            category="runtime",
            subcategory="general",
            common_causes=["test cause"],
            solutions=["sol_001"],
            examples=["test error example"]
        )
        solution = ErrorSolution(
            solution_id="sol_001",
            description="Test solution",
            steps=["step 1", "step 2"],
            prerequisites=["prereq 1"],
            success_criteria=["criteria 1"]
        )
        
        self.knowledge_base.add_pattern("test_001", pattern)
        self.knowledge_base.add_solution("sol_001", solution)
        
        stats = self.knowledge_base.get_statistics()
        
        self.assertEqual(stats["total_patterns"], 1)
        self.assertEqual(stats["total_solutions"], 1)
        self.assertEqual(stats["patterns_by_category"]["runtime"], 1)
        self.assertEqual(stats["patterns_by_severity"]["medium"], 1)

class TestSimilaritySearch(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.search = SimilaritySearch(cache_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_add_pattern(self):
        """Test adding patterns to the search index."""
        self.search.add_pattern("test_001", "Test error pattern", contexts=["runtime", "general"])
        self.assertIn("test_001", self.search.pattern_embeddings)
        self.assertEqual(self.search.pattern_texts["test_001"], "Test error pattern")
        self.assertEqual(self.search.pattern_contexts["test_001"], {"runtime", "general"})
    
    def test_add_solution(self):
        """Test adding solutions to the search index."""
        self.search.add_solution("sol_001", "Test solution", contexts=["database", "connection"])
        self.assertIn("sol_001", self.search.solution_embeddings)
        self.assertEqual(self.search.solution_texts["sol_001"], "Test solution")
        self.assertEqual(self.search.solution_contexts["sol_001"], {"database", "connection"})
    
    def test_search_with_fuzzy(self):
        """Test similarity search functionality with fuzzy matching."""
        self.search.add_pattern("test_001", "Test error pattern", contexts=["runtime"])
        self.search.add_pattern("test_002", "Database connection error", contexts=["database"])
        
        results = self.search.search("Test errr pattrn", use_fuzzy=True, use_context=False)
        self.assertEqual(len(results), 2)
        self.assertTrue(any(r.item_id == "test_001" for r in results))
        self.assertTrue(any(r.fuzzy_score > 0.8 for r in results))
    
    def test_search_with_context(self):
        """Test similarity search functionality with context-based matching."""
        self.search.add_pattern("test_001", "Test error pattern", contexts=["runtime"])
        self.search.add_pattern("test_002", "Database connection error", contexts=["database"])
        
        results = self.search.search("Test error", use_fuzzy=False, use_context=True, context_weight=0.5)
        self.assertEqual(len(results), 2)
        self.assertTrue(any(r.context_similarity > 0 for r in results))
    
    def test_find_similar_patterns(self):
        """Test finding similar patterns."""
        self.search.add_pattern("test_001", "Test error pattern", contexts=["runtime"])
        self.search.add_pattern("test_002", "Test error pattern 2", contexts=["runtime"])
        self.search.add_pattern("test_003", "Database error", contexts=["database"])
        
        results = self.search.find_similar_patterns("test_001", use_fuzzy=True, use_context=True)
        self.assertEqual(len(results), 2)
        self.assertTrue(any(r.item_id == "test_002" for r in results))
        self.assertTrue(any(r.context_similarity > 0 for r in results))
    
    def test_find_similar_solutions(self):
        """Test finding similar solutions."""
        self.search.add_solution("sol_001", "Test solution", contexts=["runtime"])
        self.search.add_solution("sol_002", "Test solution 2", contexts=["runtime"])
        self.search.add_solution("sol_003", "Database solution", contexts=["database"])
        
        results = self.search.find_similar_solutions("sol_001", use_fuzzy=True, use_context=True)
        self.assertEqual(len(results), 2)
        self.assertTrue(any(r.item_id == "sol_002" for r in results))
        self.assertTrue(any(r.context_similarity > 0 for r in results))
    
    def test_batch_processing(self):
        """Test batch processing functionality."""
        # Add multiple patterns and solutions
        for i in range(10):
            self.search.add_pattern(f"test_{i}", f"Test error pattern {i}", contexts=["runtime"])
            self.search.add_solution(f"sol_{i}", f"Test solution {i}", contexts=["runtime"])
        
        results = self.search.search("Test error", max_workers=2)
        self.assertEqual(len(results), 20)  # 10 patterns + 10 solutions
    
    def test_statistics(self):
        """Test search index statistics."""
        self.search.add_pattern("test_001", "Test error pattern", contexts=["runtime"])
        self.search.add_solution("sol_001", "Test solution", contexts=["runtime"])
        
        stats = self.search.get_statistics()
        self.assertEqual(stats["total_patterns"], 1)
        self.assertEqual(stats["total_solutions"], 1)
        self.assertEqual(stats["patterns_with_context"], 1)
        self.assertEqual(stats["solutions_with_context"], 1)
        self.assertEqual(stats["average_contexts_per_pattern"], 1.0)
        self.assertEqual(stats["average_contexts_per_solution"], 1.0)
    
    def test_edge_cases(self):
        """Test edge cases for the search functionality."""
        # Test empty search
        results = self.search.search("")
        self.assertEqual(len(results), 0)
        
        # Test search with non-existent item
        results = self.search.find_similar_patterns("non_existent")
        self.assertEqual(len(results), 0)
        
        # Test search with empty contexts
        self.search.add_pattern("test_001", "Test error pattern", contexts=[])
        results = self.search.search("Test error", use_context=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].context_similarity, 0.0)
        
        # Test search with very long text
        long_text = "Test error pattern " * 100
        self.search.add_pattern("test_002", long_text, contexts=["runtime"])
        results = self.search.search("Test error", use_fuzzy=True)
        self.assertEqual(len(results), 2)
    
    def test_cache_persistence(self):
        """Test cache persistence functionality."""
        # Add items to search
        self.search.add_pattern("test_001", "Test error pattern", contexts=["runtime"])
        self.search.add_solution("sol_001", "Test solution", contexts=["runtime"])
        
        # Create new search instance
        new_search = SimilaritySearch(cache_dir=self.temp_dir)
        
        # Verify items are loaded from cache
        self.assertIn("test_001", new_search.pattern_embeddings)
        self.assertIn("sol_001", new_search.solution_embeddings)
        self.assertEqual(new_search.pattern_texts["test_001"], "Test error pattern")
        self.assertEqual(new_search.solution_texts["sol_001"], "Test solution")
        self.assertEqual(new_search.pattern_contexts["test_001"], {"runtime"})
        self.assertEqual(new_search.solution_contexts["sol_001"], {"runtime"})

if __name__ == '__main__':
    unittest.main() 