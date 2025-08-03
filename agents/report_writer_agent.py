"""
ReportWriterAgent - Generates final structured reports.
"""
import os
from datetime import datetime
from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from prompts.agent_prompts import ReportWriterAgentPrompts
from utils.formatters import ReportFormatter, CitationFormatter
from utils.config import config

class ReportWriterAgent(BaseAgent):
    """Agent responsible for generating final structured reports."""
    
    def __init__(self):
        super().__init__(
            name="ReportWriterAgent",
            description="Generates professional research reports"
        )
        self.report_formatter = ReportFormatter()
        self.citation_formatter = CitationFormatter()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive research report.
        
        Args:
            input_data: Dictionary containing:
                - topic: The research topic
                - summaries: List of source summaries
                - comparison: Comparison analysis results
                - key_insights: Overall key insights
                - output_format: Desired output format (markdown/pdf)
                - include_citations: Whether to include citations
                - target_audience: Target audience for the report
                
        Returns:
            Dictionary containing:
                - report_content: The generated report content
                - report_metadata: Metadata about the report
                - file_path: Path to saved report file (if applicable)
        """
        self.log_processing_start(input_data)
        
        # Validate input
        required_fields = ["topic", "summaries", "comparison"]
        if not self.validate_input(input_data, required_fields):
            return {"error": f"Missing required fields: {required_fields}"}
        
        topic = input_data["topic"]
        summaries = input_data["summaries"]
        comparison = input_data["comparison"]
        key_insights = input_data.get("key_insights", {})
        output_format = input_data.get("output_format", "markdown")
        include_citations = input_data.get("include_citations", True)
        target_audience = input_data.get("target_audience", "general")
        
        # Handle case when no sources are available
        if not summaries or len(summaries) == 0:
            self.logger.warning("No sources available for report generation")
            report_content = self._create_no_sources_report(topic)
            file_path = await self._save_report(report_content, topic, output_format)
            
            return {
                "report_content": report_content,
                "report_metadata": {
                    "topic": topic,
                    "num_sources": 0,
                    "output_format": output_format,
                    "file_path": file_path,
                    "generation_date": datetime.now().isoformat(),
                    "note": "Report generated with no sources available"
                },
                "file_path": file_path,
                "output_format": output_format
            }
        
        try:
            # Generate report content
            report_content = await self._generate_report_content(
                topic, summaries, comparison, key_insights, target_audience
            )
            
            # Format citations if requested
            if include_citations:
                report_content = await self._add_citations(report_content, summaries)
            
            # Save report to file
            file_path = await self._save_report(report_content, topic, output_format)
            
            # Generate report metadata
            report_metadata = self._generate_report_metadata(
                topic, summaries, comparison, output_format, file_path
            )
            
            output_data = {
                "report_content": report_content,
                "report_metadata": report_metadata,
                "file_path": file_path,
                "output_format": output_format
            }
            
            self.log_processing_complete(output_data)
            return output_data
            
        except Exception as e:
            self.logger.error(f"Error in ReportWriterAgent processing: {e}")
            return {"error": f"Processing failed: {str(e)}"}
    
    async def _generate_report_content(self, topic: str, summaries: List[Dict[str, Any]], 
                                     comparison: Dict[str, Any], key_insights: Dict[str, Any],
                                     target_audience: str) -> str:
        """Generate the main report content using OpenAI."""
        
        # Prepare data for report generation
        introduction_context = self._create_introduction_context(topic, summaries)
        literature_overview = self._create_literature_overview(summaries)
        source_summaries = self._format_source_summaries(summaries)
        comparison_analysis = self._format_comparison_analysis(comparison)
        key_findings = self._format_key_findings(key_insights)
        
        # Create the prompt
        system_message = self.create_system_message(ReportWriterAgentPrompts.SYSTEM_PROMPT)
        
        user_prompt = ReportWriterAgentPrompts.REPORT_GENERATION_PROMPT.format(
            topic=topic,
            introduction_context=introduction_context,
            literature_overview=literature_overview,
            source_summaries=source_summaries,
            comparison_analysis=comparison_analysis,
            key_findings=key_findings,
            audience=target_audience,
            length_requirement="comprehensive"
        )
        
        user_message = self.create_user_message(user_prompt)
        
        # Add specific formatting instructions
        user_message["content"] += """

Please generate a professional research report with the following structure:

1. **Introduction** - Context and research question
2. **Literature Overview** - Summary of sources consulted
3. **Summary of Key Sources** - Detailed summaries of each source
4. **Comparison of Viewpoints** - Analysis of agreements and disagreements
5. **Key Takeaways** - Main findings and insights
6. **Recommendations** - Suggested next steps or areas for further research
7. **References** - Properly formatted citations

Use clear, professional language appropriate for the target audience.
"""
        
        messages = [system_message, user_message]
        
        # Call OpenAI
        response = await self.call_openai(messages)
        
        return response
    
    def _create_introduction_context(self, topic: str, summaries: List[Dict[str, Any]]) -> str:
        """Create introduction context for the report."""
        context = f"Research Topic: {topic}\n\n"
        
        # Add source statistics
        context += f"Sources Analyzed: {len(summaries)}\n"
        
        # Source type breakdown
        source_types = {}
        for summary in summaries:
            source_type = summary.get("source_type", "unknown")
            source_types[source_type] = source_types.get(source_type, 0) + 1
        
        context += "Source Types:\n"
        for source_type, count in source_types.items():
            context += f"- {source_type}: {count}\n"
        
        # Add date range if available
        dates = [s.get("published") for s in summaries if s.get("published") and s.get("published") != "Unknown"]
        if dates:
            context += f"\nDate Range: {min(dates)} to {max(dates)}\n"
        
        return context
    
    def _create_literature_overview(self, summaries: List[Dict[str, Any]]) -> str:
        """Create literature overview section."""
        overview = f"This research review analyzed {len(summaries)} sources from various academic and news platforms.\n\n"
        
        # Group by source type
        source_groups = {}
        for summary in summaries:
            source_type = summary.get("source_type", "unknown")
            if source_type not in source_groups:
                source_groups[source_type] = []
            source_groups[source_type].append(summary)
        
        for source_type, group_summaries in source_groups.items():
            overview += f"**{source_type.replace('_', ' ').title()} Sources ({len(group_summaries)}):**\n"
            for summary in group_summaries[:3]:  # Show first 3 of each type
                overview += f"- {summary.get('title', 'Untitled')} ({summary.get('authors', 'Unknown')})\n"
            if len(group_summaries) > 3:
                overview += f"- ... and {len(group_summaries) - 3} more\n"
            overview += "\n"
        
        return overview
    
    def _format_source_summaries(self, summaries: List[Dict[str, Any]]) -> str:
        """Format source summaries for the report."""
        formatted_summaries = []
        
        for i, summary in enumerate(summaries, 1):
            title = summary.get("title", "Untitled")
            authors = summary.get("authors", "Unknown")
            source = summary.get("source", "Unknown")
            bullets = summary.get("summary_bullets", [])
            findings = summary.get("key_findings", [])
            
            summary_text = f"""
**Source {i}: {title}**
Authors: {authors}
Source: {source}

Key Points:
{chr(10).join([f"- {bullet}" for bullet in bullets])}

Key Findings:
{chr(10).join([f"- {finding}" for finding in findings])}
"""
            formatted_summaries.append(summary_text)
        
        return "\n" + "---\n".join(formatted_summaries)
    
    def _format_comparison_analysis(self, comparison: Dict[str, Any]) -> str:
        """Format comparison analysis for the report."""
        analysis = ""
        
        # Agreements
        agreements = comparison.get("agreements", [])
        if agreements:
            analysis += "**Areas of Agreement:**\n"
            for agreement in agreements:
                analysis += f"- {agreement}\n"
            analysis += "\n"
        
        # Disagreements
        disagreements = comparison.get("disagreements", [])
        if disagreements:
            analysis += "**Areas of Disagreement:**\n"
            for disagreement in disagreements:
                analysis += f"- {disagreement}\n"
            analysis += "\n"
        
        # Biases
        biases = comparison.get("noteworthy_biases", [])
        if biases:
            analysis += "**Notable Biases and Limitations:**\n"
            for bias in biases:
                analysis += f"- {bias}\n"
            analysis += "\n"
        
        # Gaps
        gaps = comparison.get("gaps_in_knowledge", [])
        if gaps:
            analysis += "**Research Gaps:**\n"
            for gap in gaps:
                analysis += f"- {gap}\n"
            analysis += "\n"
        
        return analysis
    
    def _format_key_findings(self, key_insights: Dict[str, Any]) -> str:
        """Format key findings for the report."""
        findings = ""
        
        insights = key_insights.get("insights", [])
        if insights:
            findings += "**Key Insights:**\n"
            for insight in insights:
                findings += f"- {insight}\n"
            findings += "\n"
        
        themes = key_insights.get("themes", [])
        if themes:
            findings += "**Common Themes:**\n"
            for theme in themes:
                findings += f"- {theme}\n"
            findings += "\n"
        
        gaps = key_insights.get("gaps", [])
        if gaps:
            findings += "**Research Gaps:**\n"
            for gap in gaps:
                findings += f"- {gap}\n"
            findings += "\n"
        
        return findings
    
    async def _add_citations(self, report_content: str, summaries: List[Dict[str, Any]]) -> str:
        """Add properly formatted citations to the report."""
        # Generate citations for each source
        citations = []
        
        for i, summary in enumerate(summaries, 1):
            title = summary.get("title", "Untitled")
            authors = summary.get("authors", "Unknown")
            source = summary.get("source", "Unknown")
            published = summary.get("published", "Unknown")
            link = summary.get("link", "")
            
            # Extract year from published date
            year = "Unknown"
            if published and published != "Unknown":
                try:
                    year = published.split("-")[0]
                except:
                    year = "Unknown"
            
            # Format citation in APA style
            citation = self.citation_formatter.format_apa(
                authors, title, source, year, link
            )
            
            citations.append(f"{i}. {citation}")
        
        # Add citations section to report
        citations_section = "\n\n## 📚 References\n\n" + "\n".join(citations)
        
        return report_content + citations_section
    
    async def _save_report(self, report_content: str, topic: str, output_format: str) -> str:
        """Save the report to a file."""
        # Create reports directory if it doesn't exist
        os.makedirs(config.reports_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_topic = safe_topic.replace(' ', '_')[:50]  # Limit length
        
        if output_format.lower() == "pdf":
            filename = f"{timestamp}_{safe_topic}.pdf"
            file_path = os.path.join(config.reports_dir, filename)
            
            # Convert markdown to PDF
            success = self.report_formatter.markdown_to_pdf(report_content, file_path)
            if not success:
                # Fallback to markdown
                filename = f"{timestamp}_{safe_topic}.md"
                file_path = os.path.join(config.reports_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
        else:
            filename = f"{timestamp}_{safe_topic}.md"
            file_path = os.path.join(config.reports_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        return file_path
    
    def _generate_report_metadata(self, topic: str, summaries: List[Dict[str, Any]], 
                                comparison: Dict[str, Any], output_format: str, 
                                file_path: str) -> Dict[str, Any]:
        """Generate metadata about the report."""
        metadata = {
            "topic": topic,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "output_format": output_format,
            "file_path": file_path,
            "sources_consulted": len(summaries),
            "articles_analyzed": len(summaries),
            "source_types": {},
            "evidence_strength": comparison.get("strength_of_evidence", {}).get("overall_strength", "unknown"),
            "agreements_found": len(comparison.get("agreements", [])),
            "disagreements_found": len(comparison.get("disagreements", [])),
            "biases_identified": len(comparison.get("noteworthy_biases", []))
        }
        
        # Source type breakdown
        for summary in summaries:
            source_type = summary.get("source_type", "unknown")
            metadata["source_types"][source_type] = metadata["source_types"].get(source_type, 0) + 1
        
        return metadata 

    def _create_no_sources_report(self, topic: str) -> str:
        """Create a report when no sources are available."""
        report = f"""# Research Report: {topic}

## Executive Summary

This research report was generated for the topic: **{topic}**

Unfortunately, no relevant sources were found during the research process. This could be due to several factors:

- Limited availability of recent sources on this specific topic
- Search query optimization issues
- Source availability or access restrictions
- Topic specificity requiring more targeted search strategies

## Research Methodology

The research was conducted using an AI-powered research analysis system that searches multiple academic and news sources including:
- ArXiv (academic papers)
- News APIs (current events and developments)
- Google Scholar (scholarly articles)

## Recommendations

To obtain more comprehensive research on this topic, consider:

1. **Refining the search query** with more specific terms
2. **Expanding the search timeframe** to include older sources
3. **Adding additional sources** such as specialized databases
4. **Using alternative search strategies** with different keywords

## Conclusion

While no sources were found for this specific query, this report serves as a starting point for further research. The topic may require more targeted investigation or may be an emerging area that needs time for more sources to become available.

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*No sources were found during the research process*
"""
        return report 