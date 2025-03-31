import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
import yaml
import time
from datetime import datetime
from dataclasses import dataclass, field
from threading import Lock
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    """A single log entry"""
    timestamp: str
    level: str
    message: str
    stage: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

class PipelineLogger:
    """Handles logging and reporting for pipeline execution"""
    
    def __init__(self, logs_dir: str = "logs", reports_dir: str = "reports"):
        """Initialize the pipeline logger
        
        Args:
            logs_dir: Directory for storing logs
            reports_dir: Directory for storing reports
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment for report templates
        self.template_env = Environment(
            loader=FileSystemLoader(str(Path(__file__).parent / "templates"))
        )
        
        # Thread-safe logging
        self.log_lock = Lock()
        self.current_pipeline: Optional[str] = None
        self.current_stage: Optional[str] = None
        self.log_entries: List[LogEntry] = []
        
    def start_logging(self, pipeline_name: str, stage_name: str) -> bool:
        """Start logging for a pipeline stage
        
        Args:
            pipeline_name: Name of the pipeline
            stage_name: Name of the stage
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.current_pipeline = pipeline_name
            self.current_stage = stage_name
            self.log_entries = []
            
            logger.info(f"Started logging for pipeline {pipeline_name}, stage {stage_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start logging: {str(e)}")
            return False
            
    def log(self, level: str, message: str, metadata: Optional[Dict] = None) -> bool:
        """Log a message
        
        Args:
            level: Log level (info, warning, error)
            message: Log message
            metadata: Optional metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.log_lock:
                entry = LogEntry(
                    timestamp=datetime.now().isoformat(),
                    level=level,
                    message=message,
                    stage=self.current_stage,
                    metadata=metadata or {}
                )
                self.log_entries.append(entry)
                
                # Also log to standard logger
                log_func = getattr(logger, level.lower(), logger.info)
                log_func(f"[{self.current_pipeline}:{self.current_stage}] {message}")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to log message: {str(e)}")
            return False
            
    def save_logs(self) -> bool:
        """Save logs to disk
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.current_pipeline:
                return False
                
            # Create log file path
            log_file = self.logs_dir / f"{self.current_pipeline}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            
            # Prepare log data
            log_data = {
                "pipeline_name": self.current_pipeline,
                "stage_name": self.current_stage,
                "entries": [
                    {
                        "timestamp": entry.timestamp,
                        "level": entry.level,
                        "message": entry.message,
                        "stage": entry.stage,
                        "metadata": entry.metadata
                    }
                    for entry in self.log_entries
                ]
            }
            
            # Save logs
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=4)
                
            logger.info(f"Saved logs to: {log_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save logs: {str(e)}")
            return False
            
    def generate_report(self, metrics: Dict) -> bool:
        """Generate a report for pipeline execution
        
        Args:
            metrics: Pipeline metrics
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.current_pipeline:
                return False
                
            # Create report directory
            report_dir = self.reports_dir / self.current_pipeline
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            
            # Generate plots
            self._generate_plots(metrics, report_dir / f"plots-{timestamp}")
            
            # Prepare report data
            report_data = {
                "pipeline_name": self.current_pipeline,
                "timestamp": timestamp,
                "metrics": metrics,
                "logs": [
                    {
                        "timestamp": entry.timestamp,
                        "level": entry.level,
                        "message": entry.message,
                        "stage": entry.stage
                    }
                    for entry in self.log_entries
                ]
            }
            
            # Generate HTML report
            template = self.template_env.get_template("pipeline_report.html")
            report_html = template.render(**report_data)
            
            # Save report
            report_file = report_dir / f"report-{timestamp}.html"
            with open(report_file, 'w') as f:
                f.write(report_html)
                
            logger.info(f"Generated report: {report_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            return False
            
    def _generate_plots(self, metrics: Dict, plot_dir: Path) -> None:
        """Generate plots for metrics visualization
        
        Args:
            metrics: Pipeline metrics
            plot_dir: Directory for saving plots
        """
        try:
            plot_dir.mkdir(parents=True, exist_ok=True)
            
            # Set style
            plt.style.use('seaborn')
            
            # CPU Usage Plot
            for stage_name, stage_metrics in metrics["stages"].items():
                plt.figure(figsize=(10, 6))
                plt.plot(stage_metrics["cpu_usage"])
                plt.title(f"CPU Usage - {stage_name}")
                plt.xlabel("Time")
                plt.ylabel("CPU Usage (%)")
                plt.savefig(plot_dir / f"cpu_usage_{stage_name}.png")
                plt.close()
                
            # Memory Usage Plot
            for stage_name, stage_metrics in metrics["stages"].items():
                plt.figure(figsize=(10, 6))
                plt.plot(stage_metrics["memory_usage"])
                plt.title(f"Memory Usage - {stage_name}")
                plt.xlabel("Time")
                plt.ylabel("Memory Usage (%)")
                plt.savefig(plot_dir / f"memory_usage_{stage_name}.png")
                plt.close()
                
            # GPU Usage Plot
            for stage_name, stage_metrics in metrics["stages"].items():
                if stage_metrics["gpu_usage"]:
                    plt.figure(figsize=(10, 6))
                    for i, gpu_usage in enumerate(zip(*stage_metrics["gpu_usage"])):
                        plt.plot(gpu_usage, label=f"GPU {i}")
                    plt.title(f"GPU Usage - {stage_name}")
                    plt.xlabel("Time")
                    plt.ylabel("GPU Usage (%)")
                    plt.legend()
                    plt.savefig(plot_dir / f"gpu_usage_{stage_name}.png")
                    plt.close()
                    
        except Exception as e:
            logger.error(f"Failed to generate plots: {str(e)}")
            
    def get_logs(self, pipeline_name: str) -> Optional[Dict]:
        """Get logs for a pipeline
        
        Args:
            pipeline_name: Name of the pipeline
            
        Returns:
            Dict: Pipeline logs if found, None otherwise
        """
        try:
            # Find latest log file
            log_files = list(self.logs_dir.glob(f"{pipeline_name}-*.json"))
            if not log_files:
                return None
                
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_log, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to get logs: {str(e)}")
            return None
            
    def clean_logs(self, pipeline_name: str) -> bool:
        """Clean up logs for a pipeline
        
        Args:
            pipeline_name: Name of the pipeline
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Remove log files
            for log_file in self.logs_dir.glob(f"{pipeline_name}-*.json"):
                log_file.unlink()
                
            # Remove report directory
            report_dir = self.reports_dir / pipeline_name
            if report_dir.exists():
                shutil.rmtree(report_dir)
                
            logger.info(f"Cleaned logs and reports for pipeline: {pipeline_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clean logs: {str(e)}")
            return False 