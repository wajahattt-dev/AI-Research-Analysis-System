"""
ComparisonAgent - Analyzes viewpoints and identifies patterns across sources.
"""
from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from prompts.agent_prompts import ComparisonAgentPrompts

class ComparisonAgent(BaseAgent):
    """Agent responsible for comparing viewpoints and identifying patterns across sources."""
    
    def __init__(self):
        super().__init__(
            name="ComparisonAgent",
            description="Compares viewpoints and identifies agreements/disagreements"
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare viewpoints across multiple sources and identify patterns.
        
        Args:
            input_data: Dictionary containing:
                - summaries: List of source summaries to compare
                - topic: The research topic being analyzed
                - analysis_focus: Focus area for the analysis (optional)
                - comparison_depth: Depth of comparison (optional)
                - bias_detection: Whether to detect biases (optional)
                
        Returns:
            Dictionary containing:
                - agreements: Areas of agreement across sources
                - disagreements: Areas of disagreement across sources
                - noteworthy_biases: Identified biases and limitations
                - common_themes: Common themes across sources
                - gaps_in_knowledge: Identified research gaps
                - strength_of_evidence: Assessment of evidence strength
                - comparison_matrix: Detailed comparison data
        """
        self.log_processing_start(input_data)
        
        # Validate input
        if not self.validate_input(input_data, ["summaries", "topic"]):
            return {"error": "Missing required fields: summaries, topic"}
        
        summaries = input_data["summaries"]
        topic = input_data["topic"]
        analysis_focus = input_data.get("analysis_focus", "general")
        comparison_depth = input_data.get("comparison_depth", "detailed")
        bias_detection = input_data.get("bias_detection", True)
        
        # Handle case when no summaries are available
        if not summaries or len(summaries) == 0:
            self.logger.warning("No summaries available for comparison")
            return {
                "agreements": [],
                "disagreements": [],
                "noteworthy_biases": [],
                "common_themes": [],
                "gaps_in_knowledge": [f"No sources found for topic: {topic}"],
                "strength_of_evidence": {
                    "overall_strength": "insufficient",
                    "reasoning": "No sources were found to analyze",
                    "indicators": []
                },
                "comparison_matrix": {},
                "analysis_metadata": {
                    "topic": topic,
                    "num_sources": 0,
                    "analysis_focus": analysis_focus,
                    "comparison_depth": comparison_depth,
                    "bias_detection": bias_detection,
                    "note": "No sources available for comparison"
                }
            }
        
        try:
            # Prepare source summaries for comparison
            source_summaries = self._prepare_source_summaries(summaries)
            
            # Perform comprehensive comparison
            comparison = await self._perform_comparison(
                source_summaries, topic, analysis_focus, comparison_depth, bias_detection
            )
            
            # Generate comparison matrix
            comparison_matrix = self._generate_comparison_matrix(summaries)
            
            # Assess strength of evidence
            strength_assessment = await self._assess_evidence_strength(summaries, topic)
            
            output_data = {
                "agreements": comparison.get("agreements", []),
                "disagreements": comparison.get("disagreements", []),
                "noteworthy_biases": comparison.get("noteworthy_biases", []),
                "common_themes": comparison.get("common_themes", []),
                "gaps_in_knowledge": comparison.get("gaps_in_knowledge", []),
                "strength_of_evidence": strength_assessment,
                "comparison_matrix": comparison_matrix,
                "analysis_metadata": {
                    "topic": topic,
                    "num_sources": len(summaries),
                    "analysis_focus": analysis_focus,
                    "comparison_depth": comparison_depth,
                    "bias_detection": bias_detection
                }
            }
            
            self.log_processing_complete(output_data)
            return output_data
            
        except Exception as e:
            self.logger.error(f"Error in ComparisonAgent processing: {e}")
            return {"error": f"Processing failed: {str(e)}"}
    
    def _prepare_source_summaries(self, summaries: List[Dict[str, Any]]) -> str:
        """Prepare source summaries for comparison analysis."""
        formatted_summaries = []
        
        for i, summary in enumerate(summaries, 1):
            title = summary.get("title", "Untitled")
            authors = summary.get("authors", "Unknown")
            source = summary.get("source", "Unknown")
            bullets = summary.get("summary_bullets", [])
            findings = summary.get("key_findings", [])
            methodology = summary.get("methodology", "")
            limitations = summary.get("limitations", [])
            
            # Handle case where bullets and findings might be strings instead of lists
            if isinstance(bullets, str):
                bullets = [bullets] if bullets else []
            if isinstance(findings, str):
                findings = [findings] if findings else []
            if isinstance(limitations, str):
                limitations = [limitations] if limitations else []
            
            summary_text = f"""
Source {i}: {title}
Authors: {authors}
Source: {source}

Key Points:
{chr(10).join([f"- {bullet}" for bullet in bullets]) if bullets else "- No key points available"}

Key Findings:
{chr(10).join([f"- {finding}" for finding in findings]) if findings else "- No key findings available"}

Methodology: {methodology if methodology else "Not specified"}

Limitations:
{chr(10).join([f"- {limitation}" for limitation in limitations]) if limitations else "- No limitations specified"}
"""
            formatted_summaries.append(summary_text)
        
        return "\n" + "="*50 + "\n".join(formatted_summaries)
    
    async def _perform_comparison(self, source_summaries: str, topic: str, 
                                analysis_focus: str, comparison_depth: str, 
                                bias_detection: bool) -> Dict[str, Any]:
        """Perform comprehensive comparison using OpenAI."""
        
        system_message = self.create_system_message(ComparisonAgentPrompts.SYSTEM_PROMPT)
        
        # Count the number of sources from the source_summaries string
        num_sources = source_summaries.count("Source ")
        
        user_prompt = ComparisonAgentPrompts.COMPARISON_PROMPT.format(
            topic=topic,
            num_sources=num_sources,
            source_summaries=source_summaries
        )
        
        # Add analysis focus and depth instructions
        if analysis_focus != "general":
            user_prompt += f"\n\nFocus your analysis on: {analysis_focus}"
        
        if comparison_depth == "detailed":
            user_prompt += "\n\nProvide a detailed comparison with specific examples."
        else:
            user_prompt += "\n\nProvide a high-level comparison focusing on main points."
        
        if bias_detection:
            user_prompt += "\n\nPay special attention to potential biases and limitations."
        
        user_message = self.create_user_message(user_prompt)
        
        # Add instruction for structured output
        user_message["content"] += """

Please provide your comparison in the following JSON format:
{
    "agreements": ["agreement1", "agreement2"],
    "disagreements": ["disagreement1", "disagreement2"],
    "noteworthy_biases": ["bias1", "bias2"],
    "common_themes": ["theme1", "theme2"],
    "gaps_in_knowledge": ["gap1", "gap2"],
    "methodological_differences": ["difference1", "difference2"],
    "confidence_levels": {
        "agreements": "high/medium/low",
        "disagreements": "high/medium/low"
    }
}
"""
        
        messages = [system_message, user_message]
        
        # Call OpenAI
        response = await self.call_openai(messages)
        
        # Parse the response
        try:
            comparison_data = self.parse_json_response(response)
            
            if isinstance(comparison_data, dict) and "text" not in comparison_data:
                return comparison_data
            else:
                return self._parse_comparison_text(response)
                
        except Exception as e:
            self.logger.warning(f"Failed to parse comparison as JSON: {e}")
            return self._parse_comparison_text(response)
    
    def _parse_comparison_text(self, response: str) -> Dict[str, Any]:
        """Parse comparison from text response."""
        comparison = {
            "agreements": [],
            "disagreements": [],
            "noteworthy_biases": [],
            "common_themes": [],
            "gaps_in_knowledge": [],
            "methodological_differences": [],
            "confidence_levels": {
                "agreements": "medium",
                "disagreements": "medium"
            }
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if "agreement" in line.lower():
                current_section = "agreements"
            elif "disagreement" in line.lower() or "contradict" in line.lower():
                current_section = "disagreements"
            elif "bias" in line.lower():
                current_section = "noteworthy_biases"
            elif "theme" in line.lower():
                current_section = "common_themes"
            elif "gap" in line.lower():
                current_section = "gaps_in_knowledge"
            elif "method" in line.lower():
                current_section = "methodological_differences"
            
            # Extract content based on current section
            if current_section and line.startswith("-"):
                item = line[1:].strip()
                if item and current_section in comparison:
                    comparison[current_section].append(item)
        
        return comparison
    
    def _generate_comparison_matrix(self, summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a detailed comparison matrix."""
        if not summaries:
            return {}
        
        matrix = {
            "source_comparison": [],
            "methodology_comparison": [],
            "quality_comparison": []
        }
        
        # Source comparison
        for summary in summaries:
            source_info = {
                "title": summary.get("title", "Untitled"),
                "source": summary.get("source", "Unknown"),
                "authors": summary.get("authors", "Unknown"),
                "quality_score": summary.get("quality_score", 0),
                "relevance_score": summary.get("relevance_score", 0),
                "content_length": len(summary.get("summary_bullets", [])),
                "has_methodology": bool(summary.get("methodology")),
                "has_limitations": bool(summary.get("limitations"))
            }
            matrix["source_comparison"].append(source_info)
        
        # Methodology comparison
        methodologies = [s.get("methodology", "") for s in summaries if s.get("methodology")]
        if methodologies:
            matrix["methodology_comparison"] = {
                "total_with_methodology": len(methodologies),
                "methodology_types": self._categorize_methodologies(methodologies)
            }
        
        # Quality comparison
        quality_scores = [s.get("quality_score", 0) for s in summaries]
        relevance_scores = [s.get("relevance_score", 0) for s in summaries]
        
        matrix["quality_comparison"] = {
            "avg_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "avg_relevance_score": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0,
            "quality_distribution": {
                "high": len([s for s in quality_scores if s >= 0.7]),
                "medium": len([s for s in quality_scores if 0.4 <= s < 0.7]),
                "low": len([s for s in quality_scores if s < 0.4])
            }
        }
        
        return matrix
    
    def _categorize_methodologies(self, methodologies: List[str]) -> Dict[str, int]:
        """Categorize methodologies by type."""
        categories = {
            "experimental": 0,
            "observational": 0,
            "theoretical": 0,
            "review": 0,
            "case_study": 0,
            "other": 0
        }
        
        for methodology in methodologies:
            methodology_lower = methodology.lower()
            
            if any(word in methodology_lower for word in ["experiment", "trial", "test"]):
                categories["experimental"] += 1
            elif any(word in methodology_lower for word in ["observe", "survey", "interview"]):
                categories["observational"] += 1
            elif any(word in methodology_lower for word in ["theory", "model", "framework"]):
                categories["theoretical"] += 1
            elif any(word in methodology_lower for word in ["review", "meta-analysis", "systematic"]):
                categories["review"] += 1
            elif any(word in methodology_lower for word in ["case", "study", "example"]):
                categories["case_study"] += 1
            else:
                categories["other"] += 1
        
        return categories
    
    async def _assess_evidence_strength(self, summaries: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Assess the strength of evidence across all sources."""
        
        if not summaries:
            return {"overall_strength": "insufficient", "reasoning": "No sources available"}
        
        # Collect evidence indicators
        evidence_indicators = []
        
        for summary in summaries:
            indicators = {
                "source_quality": summary.get("quality_score", 0),
                "relevance": summary.get("relevance_score", 0),
                "has_methodology": bool(summary.get("methodology")),
                "has_limitations": bool(summary.get("limitations")),
                "content_depth": len(summary.get("summary_bullets", [])),
                "source_type": summary.get("source_type", "unknown")
            }
            evidence_indicators.append(indicators)
        
        # Calculate overall strength
        avg_quality = sum(i["source_quality"] for i in evidence_indicators) / len(evidence_indicators)
        avg_relevance = sum(i["relevance"] for i in evidence_indicators) / len(evidence_indicators)
        methodology_coverage = sum(1 for i in evidence_indicators if i["has_methodology"]) / len(evidence_indicators)
        
        # Determine strength level
        if avg_quality >= 0.7 and avg_relevance >= 0.7 and methodology_coverage >= 0.5:
            strength = "strong"
        elif avg_quality >= 0.5 and avg_relevance >= 0.5:
            strength = "moderate"
        elif avg_quality >= 0.3 and avg_relevance >= 0.3:
            strength = "weak"
        else:
            strength = "insufficient"
        
        # Generate reasoning
        reasoning = self._generate_strength_reasoning(evidence_indicators, strength)
        
        return {
            "overall_strength": strength,
            "reasoning": reasoning,
            "metrics": {
                "avg_quality_score": avg_quality,
                "avg_relevance_score": avg_relevance,
                "methodology_coverage": methodology_coverage,
                "total_sources": len(summaries)
            }
        }
    
    def _generate_strength_reasoning(self, indicators: List[Dict[str, Any]], strength: str) -> str:
        """Generate reasoning for evidence strength assessment."""
        avg_quality = sum(i["source_quality"] for i in indicators) / len(indicators)
        avg_relevance = sum(i["relevance"] for i in indicators) / len(indicators)
        methodology_coverage = sum(1 for i in indicators if i["has_methodology"]) / len(indicators)
        
        reasoning = f"Evidence strength assessed as {strength}. "
        
        if strength == "strong":
            reasoning += "Sources show high quality and relevance with good methodology coverage."
        elif strength == "moderate":
            reasoning += "Sources show moderate quality and relevance with some methodology coverage."
        elif strength == "weak":
            reasoning += "Sources show low quality or relevance with limited methodology coverage."
        else:
            reasoning += "Insufficient sources or very low quality evidence available."
        
        reasoning += f" Average quality: {avg_quality:.2f}, relevance: {avg_relevance:.2f}, methodology coverage: {methodology_coverage:.2f}."
        
        return reasoning 