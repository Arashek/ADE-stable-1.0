import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import pandas as pd
from threading import Lock
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

@dataclass
class FeedbackEntry:
    """Container for user feedback"""
    timestamp: str
    user_id: str
    model_name: str
    version: str
    rating: float
    comment: str
    context: Dict
    metadata: Dict = field(default_factory=dict)

class FeedbackCollector:
    """Collects and analyzes user feedback for model improvement"""
    
    def __init__(self, feedback_dir: str = "feedback"):
        """Initialize the feedback collector
        
        Args:
            feedback_dir: Directory for storing feedback data
        """
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize NLTK components
        try:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
        except Exception as e:
            logger.error(f"Failed to download NLTK data: {str(e)}")
            
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Initialize thread safety
        self.feedback_lock = Lock()
        
    def collect_feedback(self, feedback: FeedbackEntry) -> bool:
        """Collect user feedback
        
        Args:
            feedback: Feedback entry to collect
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate feedback
            if not self._validate_feedback(feedback):
                return False
                
            # Save feedback
            feedback_file = self.feedback_dir / f"{feedback.model_name}_{feedback.version}.json"
            
            with self.feedback_lock:
                if feedback_file.exists():
                    with open(feedback_file, 'r') as f:
                        existing_feedback = json.load(f)
                else:
                    existing_feedback = []
                    
                existing_feedback.append(feedback.__dict__)
                
                with open(feedback_file, 'w') as f:
                    json.dump(existing_feedback, f, indent=4)
                    
            logger.info(f"Collected feedback for model {feedback.model_name} version {feedback.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to collect feedback: {str(e)}")
            return False
            
    def _validate_feedback(self, feedback: FeedbackEntry) -> bool:
        """Validate feedback entry
        
        Args:
            feedback: Feedback entry to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check required fields
            if not all([feedback.user_id, feedback.model_name, feedback.version]):
                logger.error("Missing required feedback fields")
                return False
                
            # Validate rating
            if not isinstance(feedback.rating, (int, float)) or not 0 <= feedback.rating <= 5:
                logger.error("Invalid rating value")
                return False
                
            # Validate comment
            if not isinstance(feedback.comment, str) or not feedback.comment.strip():
                logger.error("Invalid comment")
                return False
                
            # Validate context
            if not isinstance(feedback.context, dict):
                logger.error("Invalid context")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate feedback: {str(e)}")
            return False
            
    def get_feedback(self, model_name: str, version: Optional[str] = None) -> List[Dict]:
        """Get feedback for a model
        
        Args:
            model_name: Name of the model
            version: Optional model version
            
        Returns:
            List[Dict]: List of feedback entries
        """
        try:
            feedback_file = self.feedback_dir / f"{model_name}_{version}.json" if version else None
            
            if feedback_file and feedback_file.exists():
                with open(feedback_file, 'r') as f:
                    return json.load(f)
                    
            # If no specific version requested, return all versions
            feedback = []
            for file in self.feedback_dir.glob(f"{model_name}_*.json"):
                with open(file, 'r') as f:
                    feedback.extend(json.load(f))
                    
            return feedback
            
        except Exception as e:
            logger.error(f"Failed to get feedback: {str(e)}")
            return []
            
    def analyze_feedback(self, model_name: str, version: Optional[str] = None) -> Dict:
        """Analyze feedback for a model
        
        Args:
            model_name: Name of the model
            version: Optional model version
            
        Returns:
            Dict: Analysis results
        """
        try:
            feedback = self.get_feedback(model_name, version)
            if not feedback:
                return {}
                
            # Convert feedback to DataFrame
            df = pd.DataFrame(feedback)
            
            # Calculate basic statistics
            analysis = {
                "model_name": model_name,
                "version": version or "all",
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_feedback": len(feedback),
                    "avg_rating": df["rating"].mean(),
                    "rating_distribution": df["rating"].value_counts().to_dict(),
                    "unique_users": df["user_id"].nunique()
                }
            }
            
            # Analyze comments
            if "comment" in df.columns:
                analysis["comment_analysis"] = self._analyze_comments(df["comment"])
                
            # Analyze context
            if "context" in df.columns:
                analysis["context_analysis"] = self._analyze_context(df["context"])
                
            # Analyze sentiment
            if "comment" in df.columns:
                analysis["sentiment_analysis"] = self._analyze_sentiment(df["comment"])
                
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze feedback: {str(e)}")
            return {}
            
    def _analyze_comments(self, comments: pd.Series) -> Dict:
        """Analyze feedback comments
        
        Args:
            comments: Series of comments
            
        Returns:
            Dict: Comment analysis results
        """
        try:
            # Preprocess comments
            processed_comments = comments.apply(self._preprocess_text)
            
            # Extract key terms
            vectorizer = TfidfVectorizer(max_features=100)
            tfidf_matrix = vectorizer.fit_transform(processed_comments)
            
            # Get top terms
            feature_names = vectorizer.get_feature_names_out()
            tfidf_sums = tfidf_matrix.sum(axis=0).A1
            top_terms = dict(zip(feature_names, tfidf_sums))
            top_terms = dict(sorted(top_terms.items(), key=lambda x: x[1], reverse=True)[:20])
            
            # Cluster comments
            n_clusters = min(5, len(comments))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(tfidf_matrix)
            
            # Get cluster centers
            cluster_centers = kmeans.cluster_centers_
            cluster_terms = {}
            
            for i in range(n_clusters):
                center = cluster_centers[i]
                top_indices = center.argsort()[-5:][::-1]
                cluster_terms[f"cluster_{i}"] = [feature_names[idx] for idx in top_indices]
                
            return {
                "top_terms": top_terms,
                "clusters": {
                    "n_clusters": n_clusters,
                    "cluster_terms": cluster_terms,
                    "cluster_sizes": pd.Series(clusters).value_counts().to_dict()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze comments: {str(e)}")
            return {}
            
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis
        
        Args:
            text: Text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        try:
            # Tokenize
            tokens = word_tokenize(text.lower())
            
            # Remove stopwords and lemmatize
            tokens = [
                self.lemmatizer.lemmatize(token)
                for token in tokens
                if token not in self.stop_words and token.isalnum()
            ]
            
            return " ".join(tokens)
            
        except Exception as e:
            logger.error(f"Failed to preprocess text: {str(e)}")
            return ""
            
    def _analyze_context(self, contexts: pd.Series) -> Dict:
        """Analyze feedback context
        
        Args:
            contexts: Series of context dictionaries
            
        Returns:
            Dict: Context analysis results
        """
        try:
            analysis = {}
            
            # Extract all context keys
            context_keys = set()
            for context in contexts:
                if isinstance(context, dict):
                    context_keys.update(context.keys())
                    
            # Analyze each context field
            for key in context_keys:
                values = []
                for context in contexts:
                    if isinstance(context, dict) and key in context:
                        values.append(context[key])
                        
                if values:
                    # Handle different value types
                    if all(isinstance(v, (int, float)) for v in values):
                        analysis[key] = {
                            "mean": np.mean(values),
                            "std": np.std(values),
                            "min": np.min(values),
                            "max": np.max(values)
                        }
                    else:
                        analysis[key] = {
                            "unique_values": len(set(values)),
                            "value_counts": pd.Series(values).value_counts().to_dict()
                        }
                        
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze context: {str(e)}")
            return {}
            
    def _analyze_sentiment(self, comments: pd.Series) -> Dict:
        """Analyze comment sentiment
        
        Args:
            comments: Series of comments
            
        Returns:
            Dict: Sentiment analysis results
        """
        try:
            sentiments = []
            for comment in comments:
                blob = TextBlob(comment)
                sentiments.append(blob.sentiment.polarity)
                
            return {
                "mean_sentiment": np.mean(sentiments),
                "std_sentiment": np.std(sentiments),
                "sentiment_distribution": {
                    "positive": len([s for s in sentiments if s > 0.2]),
                    "neutral": len([s for s in sentiments if -0.2 <= s <= 0.2]),
                    "negative": len([s for s in sentiments if s < -0.2])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {str(e)}")
            return {}
            
    def plot_feedback_analysis(self, model_name: str, version: Optional[str] = None) -> bool:
        """Generate feedback visualization plots
        
        Args:
            model_name: Name of the model
            version: Optional model version
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            feedback = self.get_feedback(model_name, version)
            if not feedback:
                return False
                
            # Convert feedback to DataFrame
            df = pd.DataFrame(feedback)
            
            # Create plots directory
            plots_dir = self.feedback_dir / "plots"
            plots_dir.mkdir(exist_ok=True)
            
            # Set style
            plt.style.use('seaborn')
            
            # Plot rating distribution
            plt.figure(figsize=(10, 6))
            sns.histplot(data=df, x="rating", bins=6)
            plt.title(f"Rating Distribution - {model_name}")
            plt.xlabel("Rating")
            plt.ylabel("Count")
            plt.tight_layout()
            plt.savefig(plots_dir / f"{model_name}_ratings.png")
            plt.close()
            
            # Plot sentiment over time
            if "comment" in df.columns:
                sentiments = [TextBlob(comment).sentiment.polarity for comment in df["comment"]]
                plt.figure(figsize=(12, 6))
                plt.plot(df["timestamp"], sentiments)
                plt.title(f"Sentiment Over Time - {model_name}")
                plt.xlabel("Time")
                plt.ylabel("Sentiment")
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(plots_dir / f"{model_name}_sentiment.png")
                plt.close()
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to plot feedback analysis: {str(e)}")
            return False
            
    def clean_feedback(self, model_name: str, version: Optional[str] = None) -> bool:
        """Clean up feedback data
        
        Args:
            model_name: Name of the model
            version: Optional model version
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if version:
                # Clean specific version
                feedback_file = self.feedback_dir / f"{model_name}_{version}.json"
                if feedback_file.exists():
                    feedback_file.unlink()
                    
                plot_file = self.feedback_dir / "plots" / f"{model_name}_{version}.png"
                if plot_file.exists():
                    plot_file.unlink()
            else:
                # Clean all versions
                for file in self.feedback_dir.glob(f"{model_name}_*.json"):
                    file.unlink()
                    
                for file in (self.feedback_dir / "plots").glob(f"{model_name}_*.png"):
                    file.unlink()
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to clean feedback: {str(e)}")
            return False 