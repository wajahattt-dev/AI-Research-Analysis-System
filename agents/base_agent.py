"""
Base agent class for the AI Research Analysis Project.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from openai import OpenAI
from utils.config import config

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents in the research analysis system."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.client = OpenAI(api_key=config.openai_api_key)
        self.agent_config = config.get_agent_config()
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        
        Args:
            input_data: Dictionary containing input data for the agent
            
        Returns:
            Dictionary containing the agent's output
        """
        pass
    
    async def call_openai(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Make a call to OpenAI API with proper error handling and rate limiting.
        
        Args:
            messages: List of message dictionaries for the chat completion
            **kwargs: Additional parameters for the OpenAI call
            
        Returns:
            Response content from OpenAI
        """
        try:
            # Apply default configuration
            default_params = {
                "model": self.agent_config["model"],
                "max_tokens": self.agent_config["max_tokens"],
                "temperature": self.agent_config["temperature"]
            }
            
            # Override with any provided kwargs
            default_params.update(kwargs)
            
            self.logger.info(f"Making OpenAI API call with model: {default_params['model']}")
            
            response = self.client.chat.completions.create(
                messages=messages,
                **default_params
            )
            
            content = response.choices[0].message.content
            self.logger.info(f"OpenAI API call successful, response length: {len(content)}")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error in OpenAI API call: {e}")
            raise
    
    def validate_input(self, input_data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate that required fields are present in input data.
        
        Args:
            input_data: Input data dictionary
            required_fields: List of required field names
            
        Returns:
            True if validation passes, False otherwise
        """
        missing_fields = [field for field in required_fields if field not in input_data]
        
        if missing_fields:
            self.logger.error(f"Missing required fields: {missing_fields}")
            return False
        
        return True
    
    def log_processing_start(self, input_data: Dict[str, Any]):
        """Log the start of processing."""
        self.logger.info(f"Starting {self.name} processing")
        self.logger.debug(f"Input data keys: {list(input_data.keys())}")
    
    def log_processing_complete(self, output_data: Dict[str, Any]):
        """Log the completion of processing."""
        self.logger.info(f"Completed {self.name} processing")
        self.logger.debug(f"Output data keys: {list(output_data.keys())}")
    
    def create_system_message(self, system_prompt: str) -> Dict[str, str]:
        """Create a system message for OpenAI API."""
        return {
            "role": "system",
            "content": system_prompt
        }
    
    def create_user_message(self, user_prompt: str) -> Dict[str, str]:
        """Create a user message for OpenAI API."""
        return {
            "role": "user",
            "content": user_prompt
        }
    
    def parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON response from OpenAI, with fallback to text parsing.
        
        Args:
            response: Response string from OpenAI
            
        Returns:
            Parsed dictionary or None if parsing fails
        """
        import json
        import re
        
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # If no JSON found, return the full response as text
            return {"text": response}
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            return {"text": response}
    
    def extract_structured_data(self, response: str, expected_fields: List[str]) -> Dict[str, Any]:
        """
        Extract structured data from OpenAI response.
        
        Args:
            response: Response string from OpenAI
            expected_fields: List of expected field names
            
        Returns:
            Dictionary with extracted data
        """
        # First try JSON parsing
        parsed = self.parse_json_response(response)
        
        if isinstance(parsed, dict) and "text" not in parsed:
            return parsed
        
        # Fallback to text parsing
        result = {}
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for key-value patterns
            for field in expected_fields:
                if field.lower() in line.lower():
                    # Extract value after the field name
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        result[field] = parts[1].strip()
                    break
        
        return result
    
    def get_agent_info(self) -> Dict[str, str]:
        """Get information about this agent."""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__
        } 