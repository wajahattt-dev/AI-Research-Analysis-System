"""
Configuration management for the AI Research Analysis Project.
"""
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the research analyst system."""
    
    def __init__(self):
        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        
        # News API Configuration
        self.news_api_key = os.getenv("NEWS_API_KEY")
        
        # ArXiv Configuration
        self.arxiv_email = os.getenv("ARXIV_EMAIL")
        
        # Database Configuration
        self.database_type = os.getenv("DATABASE_TYPE", "sqlite")
        self.database_path = os.getenv("DATABASE_PATH", "./data/research_db.sqlite")
        
        # Report Configuration
        self.default_output_format = os.getenv("DEFAULT_OUTPUT_FORMAT", "markdown")
        self.reports_dir = os.getenv("REPORTS_DIR", "./reports")
        
        # Rate Limiting
        self.max_requests_per_minute = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
        self.request_delay = float(os.getenv("REQUEST_DELAY", "1.0"))
        
        # Source Configuration
        self.default_sources = os.getenv("DEFAULT_SOURCES", "arxiv,news,scholarly").split(",")
        self.max_sources_per_query = int(os.getenv("MAX_SOURCES_PER_QUERY", "10"))
        self.max_articles_per_source = int(os.getenv("MAX_ARTICLES_PER_SOURCE", "5"))
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "./data/research_analyst.log")
        
        # Validate required configuration
        self._validate_config()
        
        # Setup logging
        self._setup_logging()
    
    def _validate_config(self):
        """Validate that required configuration is present."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file.")
        
        if not self.news_api_key:
            print("Warning: NEWS_API_KEY not set. News sources will be disabled.")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
    
    def get_source_config(self, source_name: str) -> Dict:
        """Get configuration for a specific source."""
        source_configs = {
            "arxiv": {
                "enabled": True,
                "max_results": self.max_articles_per_source,
                "email": self.arxiv_email
            },
            "news": {
                "enabled": bool(self.news_api_key),
                "max_results": self.max_articles_per_source,
                "api_key": self.news_api_key
            },
            "scholarly": {
                "enabled": True,
                "max_results": self.max_articles_per_source
            }
        }
        
        return source_configs.get(source_name, {"enabled": False})
    
    def get_report_config(self) -> Dict:
        """Get report generation configuration."""
        return {
            "output_format": self.default_output_format,
            "reports_dir": self.reports_dir,
            "include_citations": True,
            "include_metadata": True
        }
    
    def get_agent_config(self) -> Dict:
        """Get agent configuration."""
        return {
            "model": self.openai_model,
            "max_tokens": 4000,
            "temperature": 0.3,
            "request_delay": self.request_delay
        }

# Global configuration instance
config = Config() 