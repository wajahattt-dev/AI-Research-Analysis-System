"""
LiteratureAgent - Searches and collects sources from multiple platforms.
"""
import asyncio
from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from prompts.agent_prompts import LiteratureAgentPrompts
from utils.scrapers import SourceManager
from utils.config import config

class LiteratureAgent(BaseAgent):
    """Agent responsible for searching and collecting sources from multiple platforms."""
    
    def __init__(self):
        super().__init__(
            name="LiteratureAgent",
            description="Searches and collects sources from academic and news platforms"
        )
        self.source_manager = SourceManager()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for and collect relevant sources based on the research query.
        
        Args:
            input_data: Dictionary containing:
                - query: The research query string
                - sources: List of sources to search (optional)
                - max_sources: Maximum number of sources to collect (optional)
                - subtopics: List of subtopics to focus on (optional)
                
        Returns:
            Dictionary containing:
                - sources: List of collected sources with metadata
                - search_queries: List of queries used for search
                - source_stats: Statistics about collected sources
                - search_metadata: Information about the search process
        """
        self.log_processing_start(input_data)
        
        # Validate input
        if not self.validate_input(input_data, ["query"]):
            return {"error": "Missing required field: query"}
        
        query = input_data["query"]
        sources = input_data.get("sources", config.default_sources)
        max_sources = input_data.get("max_sources", config.max_sources_per_query)
        subtopics = input_data.get("subtopics", [])
        
        try:
            # Generate search strategy
            search_strategy = await self._generate_search_strategy(query, subtopics)
            
            # Collect sources
            collected_sources = await self._collect_sources(
                query, sources, max_sources, search_strategy
            )
            
            # Enhance sources with additional content
            enhanced_sources = await self._enhance_sources(collected_sources)
            
            # Generate source statistics
            source_stats = self._generate_source_stats(enhanced_sources)
            
            output_data = {
                "sources": enhanced_sources,
                "search_queries": search_strategy.get("queries", [query]),
                "source_stats": source_stats,
                "search_metadata": {
                    "query": query,
                    "sources_searched": sources,
                    "total_sources_found": len(enhanced_sources),
                    "search_strategy": search_strategy
                }
            }
            
            self.log_processing_complete(output_data)
            return output_data
            
        except Exception as e:
            self.logger.error(f"Error in LiteratureAgent processing: {e}")
            return {"error": f"Processing failed: {str(e)}"}
    
    async def _generate_search_strategy(self, query: str, subtopics: List[str]) -> Dict[str, Any]:
        """Generate a comprehensive search strategy using OpenAI."""
        
        system_message = self.create_system_message(LiteratureAgentPrompts.SYSTEM_PROMPT)
        
        user_prompt = LiteratureAgentPrompts.SEARCH_STRATEGY_PROMPT.format(
            topic=query,
            domain="general"
        )
        
        if subtopics:
            user_prompt += f"\n\nSubtopics to focus on: {', '.join(subtopics)}"
        
        user_message = self.create_user_message(user_prompt)
        
        # Add instruction for structured output
        user_message["content"] += """

Please provide your search strategy in the following JSON format:
{
    "primary_keywords": ["keyword1", "keyword2"],
    "related_terms": ["term1", "term2"],
    "time_range": "recent/any",
    "source_types": ["academic", "news", "industry"],
    "quality_criteria": ["peer_reviewed", "recent", "reputable"],
    "queries": ["search query 1", "search query 2"]
}
"""
        
        messages = [system_message, user_message]
        
        # Call OpenAI
        response = await self.call_openai(messages)
        
        # Parse the response
        try:
            strategy = self.parse_json_response(response)
            if isinstance(strategy, dict) and "text" not in strategy:
                return strategy
            else:
                return self._parse_strategy_text(response, query, subtopics)
        except Exception as e:
            self.logger.warning(f"Failed to parse strategy as JSON: {e}")
            return self._parse_strategy_text(response, query, subtopics)
    
    def _parse_strategy_text(self, response: str, query: str, subtopics: List[str]) -> Dict[str, Any]:
        """Parse search strategy from text response."""
        strategy = {
            "primary_keywords": [query],
            "related_terms": [],
            "time_range": "any",
            "source_types": ["academic", "news"],
            "quality_criteria": ["recent", "reputable"],
            "queries": [query]
        }
        
        # Add subtopics as related terms and queries
        if subtopics:
            strategy["related_terms"].extend(subtopics)
            strategy["queries"].extend(subtopics)
        
        return strategy
    
    async def _collect_sources(self, query: str, sources: List[str], 
                             max_sources: int, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect sources from multiple platforms."""
        
        all_sources = []
        queries = strategy.get("queries", [query])
        
        # Calculate sources per query to stay within limits
        sources_per_query = max(1, max_sources // len(queries))
        
        # Map descriptive source names to actual source keys
        source_mapping = {
            "academic": "arxiv",
            "scholarly": "scholarly", 
            "news": "news",
            "arxiv": "arxiv",
            "google scholar": "scholarly",
            "academic sources": "arxiv",
            "news sources": "news",
            "industry reports": "news"
        }
        
        # Clean and map sources
        cleaned_sources = []
        for source in sources:
            if source.lower() in source_mapping:
                cleaned_sources.append(source_mapping[source.lower()])
            elif source in ["arxiv", "news", "scholarly"]:
                cleaned_sources.append(source)
            else:
                # Try to map descriptive names
                for key, value in source_mapping.items():
                    if key in source.lower():
                        cleaned_sources.append(value)
                        break
        
        # Use default sources if none are valid
        if not cleaned_sources:
            cleaned_sources = ["arxiv", "news", "scholarly"]
        
        for search_query in queries:
            self.logger.info(f"Searching for: {search_query}")
            
            try:
                # Search all configured sources
                results = self.source_manager.search_all_sources(
                    query=search_query,
                    sources=cleaned_sources,
                    max_per_source=sources_per_query
                )
                
                all_sources.extend(results)
                
                # Add small delay to respect rate limits
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error searching for '{search_query}': {e}")
                continue
        
        # Remove duplicates and limit total sources
        unique_sources = self._remove_duplicates(all_sources)
        return unique_sources[:max_sources]
    
    def _remove_duplicates(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate sources based on title similarity."""
        seen_titles = set()
        unique_sources = []
        
        for source in sources:
            title = source.get("title", "").lower().strip()
            
            # Simple similarity check
            is_duplicate = False
            for seen_title in seen_titles:
                if self._similarity_score(title, seen_title) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_titles.add(title)
                unique_sources.append(source)
        
        return unique_sources
    
    def _similarity_score(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles."""
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def _enhance_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance sources with additional content and metadata."""
        
        enhanced_sources = []
        
        for source in sources:
            enhanced_source = source.copy()
            
            # Add source quality score
            enhanced_source["quality_score"] = self._calculate_quality_score(source)
            
            # Add content length
            content = source.get("content", "")
            enhanced_source["content_length"] = len(content)
            
            # Add source type classification
            enhanced_source["source_type"] = self._classify_source_type(source)
            
            # Add relevance indicators
            enhanced_source["relevance_indicators"] = self._extract_relevance_indicators(source)
            
            enhanced_sources.append(enhanced_source)
        
        # Sort by quality score
        enhanced_sources.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        
        return enhanced_sources
    
    def _calculate_quality_score(self, source: Dict[str, Any]) -> float:
        """Calculate a quality score for a source."""
        score = 0.0
        
        # Source type scoring
        source_name = source.get("source", "").lower()
        if "arxiv" in source_name:
            score += 0.3
        elif "scholarly" in source_name:
            score += 0.3
        elif "news" in source_name:
            score += 0.2
        
        # Content length scoring
        content_length = len(source.get("content", ""))
        if content_length > 1000:
            score += 0.2
        elif content_length > 500:
            score += 0.1
        
        # Author information
        authors = source.get("authors", "")
        if authors and authors != "Unknown":
            score += 0.1
        
        # Publication date (prefer recent sources)
        published = source.get("published", "")
        if published and published != "Unknown":
            score += 0.1
        
        # Citations (if available)
        citations = source.get("citations", 0)
        if citations > 10:
            score += 0.1
        
        return min(score, 1.0)
    
    def _classify_source_type(self, source: Dict[str, Any]) -> str:
        """Classify the type of source."""
        source_name = source.get("source", "").lower()
        
        if "arxiv" in source_name:
            return "academic_paper"
        elif "scholarly" in source_name:
            return "scholarly_article"
        elif "news" in source_name:
            return "news_article"
        else:
            return "other"
    
    def _extract_relevance_indicators(self, source: Dict[str, Any]) -> List[str]:
        """Extract indicators of relevance from the source."""
        indicators = []
        
        title = source.get("title", "").lower()
        content = source.get("content", "").lower()
        
        # Check for technical terms
        technical_terms = ["research", "study", "analysis", "method", "results", "conclusion"]
        for term in technical_terms:
            if term in title or term in content:
                indicators.append(f"contains_{term}")
        
        # Check for recent publication
        published = source.get("published", "")
        if published and published != "Unknown":
            indicators.append("has_publication_date")
        
        # Check for authors
        authors = source.get("authors", "")
        if authors and authors != "Unknown":
            indicators.append("has_authors")
        
        return indicators
    
    def _generate_source_stats(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about collected sources."""
        if not sources:
            return {"total": 0}
        
        stats = {
            "total": len(sources),
            "by_source_type": {},
            "by_quality": {
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "content_length": {
                "short": 0,
                "medium": 0,
                "long": 0
            }
        }
        
        for source in sources:
            # Source type stats
            source_type = source.get("source_type", "other")
            stats["by_source_type"][source_type] = stats["by_source_type"].get(source_type, 0) + 1
            
            # Quality stats
            quality_score = source.get("quality_score", 0)
            if quality_score >= 0.7:
                stats["by_quality"]["high"] += 1
            elif quality_score >= 0.4:
                stats["by_quality"]["medium"] += 1
            else:
                stats["by_quality"]["low"] += 1
            
            # Content length stats
            content_length = source.get("content_length", 0)
            if content_length > 1000:
                stats["content_length"]["long"] += 1
            elif content_length > 500:
                stats["content_length"]["medium"] += 1
            else:
                stats["content_length"]["short"] += 1
        
        return stats 