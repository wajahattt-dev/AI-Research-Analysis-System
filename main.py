"""
Main orchestrator for the AI Research Analysis Project.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from agents.router_agent import RouterAgent
from agents.literature_agent import LiteratureAgent
from agents.summary_agent import SummaryAgent
from agents.comparison_agent import ComparisonAgent
from agents.report_writer_agent import ReportWriterAgent
from utils.config import config

logger = logging.getLogger(__name__)

class ResearchAnalyst:
    """Main orchestrator for the research analysis system."""
    
    def __init__(self):
        """Initialize the research analyst with all agents."""
        self.router_agent = RouterAgent()
        self.literature_agent = LiteratureAgent()
        self.summary_agent = SummaryAgent()
        self.comparison_agent = ComparisonAgent()
        self.report_writer_agent = ReportWriterAgent()
        
        self.agents = {
            "RouterAgent": self.router_agent,
            "LiteratureAgent": self.literature_agent,
            "SummaryAgent": self.summary_agent,
            "ComparisonAgent": self.comparison_agent,
            "ReportWriterAgent": self.report_writer_agent
        }
        
        logger.info("Research Analyst initialized with all agents")
    
    async def conduct_research(self, query: str, config_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Conduct comprehensive research on a given query.
        
        Args:
            query: The research query string
            config_overrides: Optional configuration overrides
            
        Returns:
            Dictionary containing the complete research results
        """
        start_time = datetime.now()
        logger.info(f"Starting research on query: {query}")
        
        try:
            # Step 1: Route and plan the research
            logger.info("Step 1: Routing and planning research...")
            routing_result = await self.router_agent.process({
                "query": query,
                "user_context": config_overrides.get("user_context", "")
            })
            
            if "error" in routing_result:
                return {"error": f"Routing failed: {routing_result['error']}"}
            
            # Step 2: Collect literature sources
            logger.info("Step 2: Collecting literature sources...")
            literature_result = await self.literature_agent.process({
                "query": query,
                "sources": routing_result.get("sources", config.default_sources),
                "max_sources": config_overrides.get("max_sources", config.max_sources_per_query),
                "subtopics": routing_result.get("subtopics", [])
            })
            
            if "error" in literature_result:
                return {"error": f"Literature collection failed: {literature_result['error']}"}
            
            # Step 3: Summarize sources
            logger.info("Step 3: Summarizing sources...")
            summary_result = await self.summary_agent.process({
                "sources": literature_result["sources"],
                "focus_areas": routing_result.get("subtopics", []),
                "summary_format": config_overrides.get("summary_format", "bullet_points"),
                "include_quotes": config_overrides.get("include_quotes", True)
            })
            
            if "error" in summary_result:
                return {"error": f"Summarization failed: {summary_result['error']}"}
            
            # Step 4: Compare viewpoints
            logger.info("Step 4: Comparing viewpoints...")
            comparison_result = await self.comparison_agent.process({
                "summaries": summary_result["summaries"],
                "topic": query,
                "analysis_focus": routing_result.get("domain", "general"),
                "comparison_depth": config_overrides.get("comparison_depth", "detailed"),
                "bias_detection": config_overrides.get("bias_detection", True)
            })
            
            if "error" in comparison_result:
                return {"error": f"Comparison failed: {comparison_result['error']}"}
            
            # Step 5: Generate final report
            logger.info("Step 5: Generating final report...")
            report_result = await self.report_writer_agent.process({
                "topic": query,
                "summaries": summary_result["summaries"],
                "comparison": comparison_result,
                "key_insights": summary_result.get("key_insights", {}),
                "output_format": config_overrides.get("output_format", config.default_output_format),
                "include_citations": config_overrides.get("include_citations", True),
                "target_audience": config_overrides.get("target_audience", "general")
            })
            
            if "error" in report_result:
                return {"error": f"Report generation failed: {report_result['error']}"}
            
            # Compile final results
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            final_results = {
                "query": query,
                "report_content": report_result["report_content"],
                "report_metadata": report_result["report_metadata"],
                "file_path": report_result["file_path"],
                "output_format": report_result["output_format"],
                "research_summary": {
                    "total_sources": len(literature_result["sources"]),
                    "sources_by_type": literature_result["source_stats"]["by_source_type"],
                    "agreements_found": len(comparison_result["agreements"]),
                    "disagreements_found": len(comparison_result["disagreements"]),
                    "biases_identified": len(comparison_result["noteworthy_biases"]),
                    "evidence_strength": comparison_result["strength_of_evidence"]["overall_strength"]
                },
                "processing_metadata": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration,
                    "config_used": {
                        "sources": routing_result.get("sources", config.default_sources),
                        "max_sources": config_overrides.get("max_sources", config.max_sources_per_query),
                        "output_format": config_overrides.get("output_format", config.default_output_format)
                    }
                },
                "intermediate_results": {
                    "routing": routing_result,
                    "literature": literature_result,
                    "summary": summary_result,
                    "comparison": comparison_result
                }
            }
            
            logger.info(f"Research completed successfully in {duration:.2f} seconds")
            return final_results
            
        except Exception as e:
            logger.error(f"Research failed with error: {e}")
            return {"error": f"Research failed: {str(e)}"}
    
    async def get_research_status(self, query: str) -> Dict[str, Any]:
        """
        Get the current status of a research query (for future async implementation).
        
        Args:
            query: The research query string
            
        Returns:
            Dictionary containing the current status
        """
        # This is a placeholder for future async implementation
        return {
            "query": query,
            "status": "not_implemented",
            "message": "Status tracking not yet implemented"
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about all agents in the system."""
        agent_info = {}
        for name, agent in self.agents.items():
            agent_info[name] = agent.get_agent_info()
        return agent_info
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get the current system configuration."""
        return {
            "default_sources": config.default_sources,
            "max_sources_per_query": config.max_sources_per_query,
            "max_articles_per_source": config.max_articles_per_source,
            "default_output_format": config.default_output_format,
            "openai_model": config.openai_model,
            "database_type": config.database_type,
            "reports_dir": config.reports_dir
        }
    
    async def validate_system(self) -> Dict[str, Any]:
        """Validate that all system components are working correctly."""
        validation_results = {
            "overall_status": "unknown",
            "agents": {},
            "config": {},
            "errors": []
        }
        
        try:
            # Validate configuration
            if not config.openai_api_key:
                validation_results["errors"].append("OpenAI API key not configured")
            else:
                validation_results["config"]["openai"] = "configured"
            
            if not config.news_api_key:
                validation_results["config"]["news_api"] = "not_configured (optional)"
            else:
                validation_results["config"]["news_api"] = "configured"
            
            # Validate agents
            for name, agent in self.agents.items():
                try:
                    agent_info = agent.get_agent_info()
                    validation_results["agents"][name] = {
                        "status": "ready",
                        "info": agent_info
                    }
                except Exception as e:
                    validation_results["agents"][name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    validation_results["errors"].append(f"Agent {name} error: {e}")
            
            # Determine overall status
            if validation_results["errors"]:
                validation_results["overall_status"] = "error"
            else:
                validation_results["overall_status"] = "ready"
            
        except Exception as e:
            validation_results["overall_status"] = "error"
            validation_results["errors"].append(f"System validation error: {e}")
        
        return validation_results

# Convenience function for quick research
async def quick_research(query: str, output_format: str = "markdown") -> Dict[str, Any]:
    """
    Quick research function for simple queries.
    
    Args:
        query: The research query string
        output_format: Output format (markdown or pdf)
        
    Returns:
        Research results dictionary
    """
    analyst = ResearchAnalyst()
    return await analyst.conduct_research(query, {"output_format": output_format})

# Example usage
if __name__ == "__main__":
    async def main():
        # Example research query
        query = "What are the latest developments in quantum computing?"
        
        analyst = ResearchAnalyst()
        
        # Validate system first
        validation = await analyst.validate_system()
        print("System Validation:", validation)
        
        if validation["overall_status"] == "ready":
            # Conduct research
            results = await analyst.conduct_research(query, {
                "output_format": "markdown",
                "max_sources": 5
            })
            
            if "error" not in results:
                print(f"Research completed successfully!")
                print(f"Report saved to: {results['file_path']}")
                print(f"Sources analyzed: {results['research_summary']['total_sources']}")
                print(f"Evidence strength: {results['research_summary']['evidence_strength']}")
            else:
                print(f"Research failed: {results['error']}")
        else:
            print("System validation failed. Please check configuration.")
    
    # Run the example
    asyncio.run(main()) 