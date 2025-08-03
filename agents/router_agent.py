"""
RouterAgent - Classifies research queries and creates task plans.
"""
import json
from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from prompts.agent_prompts import RouterAgentPrompts

class RouterAgent(BaseAgent):
    """Agent responsible for analyzing research queries and creating task plans."""
    
    def __init__(self):
        super().__init__(
            name="RouterAgent",
            description="Analyzes research queries and creates detailed task plans"
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a research query and create a comprehensive task plan.
        
        Args:
            input_data: Dictionary containing:
                - query: The research query string
                - user_context: Optional user context or preferences
                
        Returns:
            Dictionary containing:
                - domain: Classified research domain
                - subtopics: List of key subtopics to research
                - sources: Recommended sources for research
                - strategy: Research strategy and approach
                - task_plan: Detailed task breakdown
                - expected_output: Type of analysis expected
        """
        self.log_processing_start(input_data)
        
        # Validate input
        if not self.validate_input(input_data, ["query"]):
            return {"error": "Missing required field: query"}
        
        query = input_data["query"]
        user_context = input_data.get("user_context", "")
        
        try:
            # Analyze the query using OpenAI
            analysis = await self._analyze_query(query, user_context)
            
            # Create task plan
            task_plan = await self._create_task_plan(analysis, query)
            
            output_data = {
                "domain": analysis.get("domain", "general"),
                "subtopics": analysis.get("subtopics", []),
                "sources": analysis.get("sources", []),
                "strategy": analysis.get("strategy", ""),
                "task_plan": task_plan,
                "expected_output": analysis.get("expected_output", "comprehensive_report"),
                "query": query,
                "analysis": analysis
            }
            
            self.log_processing_complete(output_data)
            return output_data
            
        except Exception as e:
            self.logger.error(f"Error in RouterAgent processing: {e}")
            return {"error": f"Processing failed: {str(e)}"}
    
    async def _analyze_query(self, query: str, user_context: str) -> Dict[str, Any]:
        """Analyze the research query using OpenAI."""
        
        # Prepare the prompt
        system_message = self.create_system_message(RouterAgentPrompts.SYSTEM_PROMPT)
        
        user_prompt = RouterAgentPrompts.QUERY_ANALYSIS_PROMPT.format(query=query)
        if user_context:
            user_prompt += f"\n\nUser Context: {user_context}"
        
        user_message = self.create_user_message(user_prompt)
        
        # Add instruction for structured output
        user_message["content"] += """

Please provide your analysis in the following JSON format:
{
    "domain": "technology/science/business/healthcare/etc",
    "subtopics": ["subtopic1", "subtopic2", "subtopic3"],
    "sources": ["arxiv", "news", "scholarly"],
    "strategy": "detailed research strategy description",
    "expected_output": "comprehensive_report/comparative_analysis/technical_summary"
}
"""
        
        messages = [system_message, user_message]
        
        # Call OpenAI
        response = await self.call_openai(messages)
        
        # Parse the response
        try:
            # Try to extract JSON from the response
            analysis = self.parse_json_response(response)
            
            if isinstance(analysis, dict) and "text" not in analysis:
                return analysis
            else:
                # Fallback to text parsing
                return self._parse_analysis_text(response)
                
        except Exception as e:
            self.logger.warning(f"Failed to parse analysis as JSON: {e}")
            return self._parse_analysis_text(response)
    
    def _parse_analysis_text(self, response: str) -> Dict[str, Any]:
        """Parse analysis from text response."""
        analysis = {
            "domain": "general",
            "subtopics": [],
            "sources": ["arxiv", "news", "scholarly"],
            "strategy": "Comprehensive literature review and analysis",
            "expected_output": "comprehensive_report"
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if "domain" in line.lower() or "field" in line.lower():
                current_section = "domain"
                # Extract domain
                if ":" in line:
                    domain = line.split(":", 1)[1].strip()
                    analysis["domain"] = domain
                    
            elif "subtopic" in line.lower() or "aspect" in line.lower():
                current_section = "subtopics"
                
            elif "source" in line.lower():
                current_section = "sources"
                
            elif "strategy" in line.lower() or "approach" in line.lower():
                current_section = "strategy"
                
            elif "output" in line.lower() or "analysis" in line.lower():
                current_section = "expected_output"
            
            # Extract content based on current section
            if current_section == "subtopics" and line.startswith("-"):
                subtopic = line[1:].strip()
                if subtopic:
                    analysis["subtopics"].append(subtopic)
                    
            elif current_section == "strategy" and line:
                if analysis["strategy"] == "Comprehensive literature review and analysis":
                    analysis["strategy"] = line
                else:
                    analysis["strategy"] += " " + line
        
        return analysis
    
    async def _create_task_plan(self, analysis: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Create a detailed task plan based on the analysis."""
        
        task_plan = [
            {
                "agent": "LiteratureAgent",
                "task": "source_collection",
                "description": f"Search for relevant sources on '{query}'",
                "parameters": {
                    "query": query,
                    "sources": analysis.get("sources", ["arxiv", "news", "scholarly"]),
                    "max_sources": 10,
                    "subtopics": analysis.get("subtopics", [])
                },
                "dependencies": [],
                "estimated_duration": "5-10 minutes"
            },
            {
                "agent": "SummaryAgent",
                "task": "content_summarization",
                "description": "Summarize collected sources and extract key insights",
                "parameters": {
                    "focus_areas": analysis.get("subtopics", []),
                    "summary_format": "bullet_points",
                    "include_quotes": True
                },
                "dependencies": ["LiteratureAgent"],
                "estimated_duration": "3-5 minutes"
            },
            {
                "agent": "ComparisonAgent",
                "task": "viewpoint_analysis",
                "description": "Compare viewpoints and identify patterns across sources",
                "parameters": {
                    "analysis_focus": analysis.get("domain", "general"),
                    "comparison_depth": "detailed",
                    "bias_detection": True
                },
                "dependencies": ["SummaryAgent"],
                "estimated_duration": "3-5 minutes"
            },
            {
                "agent": "ReportWriterAgent",
                "task": "report_generation",
                "description": f"Generate {analysis.get('expected_output', 'comprehensive_report')}",
                "parameters": {
                    "output_format": "markdown",
                    "include_citations": True,
                    "target_audience": "general",
                    "report_type": analysis.get("expected_output", "comprehensive_report")
                },
                "dependencies": ["ComparisonAgent"],
                "estimated_duration": "2-3 minutes"
            }
        ]
        
        return task_plan
    
    def get_domain_keywords(self, domain: str) -> List[str]:
        """Get relevant keywords for a specific domain."""
        domain_keywords = {
            "technology": ["AI", "machine learning", "software", "hardware", "innovation"],
            "science": ["research", "experiment", "theory", "hypothesis", "methodology"],
            "business": ["market", "industry", "strategy", "economics", "finance"],
            "healthcare": ["medical", "clinical", "treatment", "diagnosis", "patient"],
            "education": ["learning", "teaching", "curriculum", "pedagogy", "assessment"]
        }
        
        return domain_keywords.get(domain.lower(), [])
    
    def validate_task_plan(self, task_plan: List[Dict[str, Any]]) -> bool:
        """Validate that the task plan is complete and coherent."""
        required_agents = ["LiteratureAgent", "SummaryAgent", "ComparisonAgent", "ReportWriterAgent"]
        plan_agents = [task["agent"] for task in task_plan]
        
        for agent in required_agents:
            if agent not in plan_agents:
                self.logger.error(f"Missing required agent in task plan: {agent}")
                return False
        
        return True 