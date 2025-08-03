"""
SummaryAgent - Distills content into key insights and summaries.
"""
import asyncio
from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from prompts.agent_prompts import SummaryAgentPrompts
from utils.formatters import DataFormatter

class SummaryAgent(BaseAgent):
    """Agent responsible for summarizing and extracting key insights from sources."""
    
    def __init__(self):
        super().__init__(
            name="SummaryAgent",
            description="Summarizes sources and extracts key insights"
        )
        self.formatter = DataFormatter()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize sources and extract key insights.
        
        Args:
            input_data: Dictionary containing:
                - sources: List of sources to summarize
                - focus_areas: List of focus areas for summarization (optional)
                - summary_format: Format for summaries (optional)
                - include_quotes: Whether to include notable quotes (optional)
                
        Returns:
            Dictionary containing:
                - summaries: List of summarized sources
                - key_insights: Overall key insights across all sources
                - summary_stats: Statistics about the summarization process
        """
        self.log_processing_start(input_data)
        
        # Validate input
        if not self.validate_input(input_data, ["sources"]):
            return {"error": "Missing required field: sources"}
        
        sources = input_data["sources"]
        focus_areas = input_data.get("focus_areas", [])
        summary_format = input_data.get("summary_format", "bullet_points")
        include_quotes = input_data.get("include_quotes", True)
        
        # Handle case when no sources are available
        if not sources or len(sources) == 0:
            self.logger.warning("No sources available for summarization")
            return {
                "summaries": [],
                "key_insights": {
                    "main_findings": [],
                    "key_themes": [],
                    "research_gaps": ["No sources were found to analyze"],
                    "methodological_insights": [],
                    "future_directions": []
                },
                "summary_stats": {
                    "total_sources": 0,
                    "successful_summaries": 0,
                    "failed_summaries": 0,
                    "average_summary_length": 0
                },
                "processing_metadata": {
                    "total_sources": 0,
                    "focus_areas": focus_areas,
                    "summary_format": summary_format,
                    "include_quotes": include_quotes,
                    "note": "No sources available for summarization"
                }
            }
        
        try:
            # Summarize each source
            summaries = await self._summarize_sources(
                sources, focus_areas, summary_format, include_quotes
            )
            
            # Extract overall key insights
            key_insights = await self._extract_key_insights(summaries, focus_areas)
            
            # Generate summary statistics
            summary_stats = self._generate_summary_stats(summaries)
            
            output_data = {
                "summaries": summaries,
                "key_insights": key_insights,
                "summary_stats": summary_stats,
                "processing_metadata": {
                    "total_sources": len(sources),
                    "focus_areas": focus_areas,
                    "summary_format": summary_format,
                    "include_quotes": include_quotes
                }
            }
            
            self.log_processing_complete(output_data)
            return output_data
            
        except Exception as e:
            self.logger.error(f"Error in SummaryAgent processing: {e}")
            return {"error": f"Processing failed: {str(e)}"}
    
    async def _summarize_sources(self, sources: List[Dict[str, Any]], 
                               focus_areas: List[str], summary_format: str, 
                               include_quotes: bool) -> List[Dict[str, Any]]:
        """Summarize each source individually."""
        
        summaries = []
        
        # Process sources concurrently with rate limiting
        semaphore = asyncio.Semaphore(3)  # Limit concurrent API calls
        
        async def summarize_source(source):
            async with semaphore:
                return await self._summarize_single_source(
                    source, focus_areas, summary_format, include_quotes
                )
        
        # Create tasks for all sources
        tasks = [summarize_source(source) for source in sources]
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Error summarizing source {i}: {result}")
                # Create a basic summary for failed sources
                basic_summary = self._create_basic_summary(sources[i])
                summaries.append(basic_summary)
            else:
                summaries.append(result)
        
        return summaries
    
    async def _summarize_single_source(self, source: Dict[str, Any], 
                                     focus_areas: List[str], summary_format: str, 
                                     include_quotes: bool) -> Dict[str, Any]:
        """Summarize a single source using OpenAI."""
        
        # Prepare the content for summarization
        title = source.get("title", "Untitled")
        authors = source.get("authors", "Unknown")
        source_name = source.get("source", "Unknown")
        content = source.get("content", "")
        
        # Clean and truncate content if too long
        content = self.formatter.clean_text(content)
        if len(content) > 3000:
            content = self.formatter.truncate_text(content, 3000)
        
        # Create the prompt
        system_message = self.create_system_message(SummaryAgentPrompts.SYSTEM_PROMPT)
        
        user_prompt = SummaryAgentPrompts.SUMMARY_PROMPT.format(
            title=title,
            authors=authors,
            source=source_name,
            content=content
        )
        
        # Add focus areas if specified
        if focus_areas:
            user_prompt += f"\n\nFocus Areas: {', '.join(focus_areas)}"
        
        # Add format instructions
        if summary_format == "bullet_points":
            user_prompt += "\n\nPlease provide the summary in clear bullet points."
        elif summary_format == "paragraph":
            user_prompt += "\n\nPlease provide the summary in paragraph format."
        
        user_message = self.create_user_message(user_prompt)
        
        # Add instruction for structured output
        user_message["content"] += """

Please provide your summary in the following JSON format:
{
    "summary_bullets": ["point1", "point2", "point3"],
    "notable_quotes": ["quote1", "quote2"],
    "key_findings": ["finding1", "finding2"],
    "methodology": "brief methodology description",
    "limitations": ["limitation1", "limitation2"],
    "relevance_score": 0.85
}
"""
        
        messages = [system_message, user_message]
        
        # Call OpenAI
        response = await self.call_openai(messages)
        
        # Parse the response
        try:
            summary_data = self.parse_json_response(response)
            
            if isinstance(summary_data, dict) and "text" not in summary_data:
                # Add source metadata to the summary
                summary_data.update({
                    "title": title,
                    "authors": authors,
                    "source": source_name,
                    "published": source.get("published", "Unknown"),
                    "link": source.get("link", ""),
                    "source_type": source.get("source_type", "unknown"),
                    "quality_score": source.get("quality_score", 0)
                })
                return summary_data
            else:
                return self._parse_summary_text(response, source)
                
        except Exception as e:
            self.logger.warning(f"Failed to parse summary as JSON: {e}")
            return self._parse_summary_text(response, source)
    
    def _parse_summary_text(self, response: str, source: Dict[str, Any]) -> Dict[str, Any]:
        """Parse summary from text response."""
        summary = {
            "title": source.get("title", "Untitled"),
            "authors": source.get("authors", "Unknown"),
            "source": source.get("source", "Unknown"),
            "published": source.get("published", "Unknown"),
            "link": source.get("link", ""),
            "source_type": source.get("source_type", "unknown"),
            "quality_score": source.get("quality_score", 0),
            "summary_bullets": [],
            "notable_quotes": [],
            "key_findings": [],
            "methodology": "",
            "limitations": [],
            "relevance_score": 0.5
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if "key points" in line.lower() or "bullet" in line.lower():
                current_section = "summary_bullets"
            elif "quote" in line.lower():
                current_section = "notable_quotes"
            elif "finding" in line.lower():
                current_section = "key_findings"
            elif "methodology" in line.lower():
                current_section = "methodology"
            elif "limitation" in line.lower():
                current_section = "limitations"
            
            # Extract content based on current section
            if current_section == "summary_bullets" and line.startswith("-"):
                bullet = line[1:].strip()
                if bullet:
                    summary["summary_bullets"].append(bullet)
                    
            elif current_section == "notable_quotes" and line.startswith(">"):
                quote = line[1:].strip()
                if quote:
                    summary["notable_quotes"].append(quote)
                    
            elif current_section == "key_findings" and line.startswith("-"):
                finding = line[1:].strip()
                if finding:
                    summary["key_findings"].append(finding)
                    
            elif current_section == "methodology" and line:
                if not summary["methodology"]:
                    summary["methodology"] = line
                else:
                    summary["methodology"] += " " + line
                    
            elif current_section == "limitations" and line.startswith("-"):
                limitation = line[1:].strip()
                if limitation:
                    summary["limitations"].append(limitation)
        
        return summary
    
    def _create_basic_summary(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic summary when AI summarization fails."""
        return {
            "title": source.get("title", "Untitled"),
            "authors": source.get("authors", "Unknown"),
            "source": source.get("source", "Unknown"),
            "published": source.get("published", "Unknown"),
            "link": source.get("link", ""),
            "source_type": source.get("source_type", "unknown"),
            "quality_score": source.get("quality_score", 0),
            "summary_bullets": [
                f"Source: {source.get('source', 'Unknown')}",
                f"Title: {source.get('title', 'Untitled')}",
                f"Content length: {len(source.get('content', ''))} characters"
            ],
            "notable_quotes": [],
            "key_findings": [],
            "methodology": "Not available",
            "limitations": ["AI summarization failed"],
            "relevance_score": 0.3
        }
    
    async def _extract_key_insights(self, summaries: List[Dict[str, Any]], 
                                  focus_areas: List[str]) -> Dict[str, Any]:
        """Extract overall key insights across all summaries."""
        
        if not summaries:
            return {"insights": [], "themes": [], "gaps": []}
        
        # Collect all key findings and summary bullets
        all_findings = []
        all_bullets = []
        
        for summary in summaries:
            all_findings.extend(summary.get("key_findings", []))
            all_bullets.extend(summary.get("summary_bullets", []))
        
        # Create a combined text for analysis
        combined_text = "\n".join(all_findings + all_bullets)
        
        if not combined_text.strip():
            return {"insights": [], "themes": [], "gaps": []}
        
        # Use OpenAI to extract key insights
        system_message = self.create_system_message(
            "You are an expert at extracting key insights from research summaries."
        )
        
        user_prompt = f"""
Based on the following research summaries, extract the key insights:

{combined_text}

Focus Areas: {', '.join(focus_areas) if focus_areas else 'General research'}

Please provide:
1. Key insights (3-5 main points)
2. Common themes across sources
3. Research gaps or areas needing more investigation

Format as JSON:
{{
    "insights": ["insight1", "insight2"],
    "themes": ["theme1", "theme2"],
    "gaps": ["gap1", "gap2"]
}}
"""
        
        user_message = self.create_user_message(user_prompt)
        messages = [system_message, user_message]
        
        try:
            response = await self.call_openai(messages)
            insights_data = self.parse_json_response(response)
            
            if isinstance(insights_data, dict) and "text" not in insights_data:
                return insights_data
            else:
                return self._parse_insights_text(response)
                
        except Exception as e:
            self.logger.error(f"Error extracting key insights: {e}")
            return {"insights": [], "themes": [], "gaps": []}
    
    def _parse_insights_text(self, response: str) -> Dict[str, Any]:
        """Parse insights from text response."""
        insights = {
            "insights": [],
            "themes": [],
            "gaps": []
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if "insight" in line.lower():
                current_section = "insights"
            elif "theme" in line.lower():
                current_section = "themes"
            elif "gap" in line.lower():
                current_section = "gaps"
            
            if current_section and line.startswith("-"):
                item = line[1:].strip()
                if item:
                    insights[current_section].append(item)
        
        return insights
    
    def _generate_summary_stats(self, summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about the summarization process."""
        if not summaries:
            return {"total": 0}
        
        stats = {
            "total": len(summaries),
            "by_source_type": {},
            "avg_relevance_score": 0,
            "total_bullets": 0,
            "total_quotes": 0,
            "sources_with_methodology": 0,
            "sources_with_limitations": 0
        }
        
        total_relevance = 0
        
        for summary in summaries:
            # Source type stats
            source_type = summary.get("source_type", "unknown")
            stats["by_source_type"][source_type] = stats["by_source_type"].get(source_type, 0) + 1
            
            # Relevance score
            relevance = summary.get("relevance_score", 0)
            total_relevance += relevance
            
            # Content stats
            stats["total_bullets"] += len(summary.get("summary_bullets", []))
            stats["total_quotes"] += len(summary.get("notable_quotes", []))
            
            if summary.get("methodology"):
                stats["sources_with_methodology"] += 1
            
            if summary.get("limitations"):
                stats["sources_with_limitations"] += 1
        
        stats["avg_relevance_score"] = total_relevance / len(summaries) if summaries else 0
        
        return stats 