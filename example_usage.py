"""
Example usage of the AI Research Analysis System.
"""
import asyncio
import json
from main import ResearchAnalyst, quick_research

async def example_basic_research():
    """Example of basic research usage."""
    print("🔬 Example 1: Basic Research")
    print("=" * 50)
    
    query = "What are the latest developments in quantum computing?"
    
    # Use the quick research function
    results = await quick_research(query, "markdown")
    
    if "error" not in results:
        print(f"✅ Research completed successfully!")
        print(f"📄 Report saved to: {results['file_path']}")
        print(f"📊 Sources analyzed: {results['research_summary']['total_sources']}")
        print(f"⚖️ Evidence strength: {results['research_summary']['evidence_strength']}")
        print(f"⏱️ Duration: {results['processing_metadata']['duration_seconds']:.2f} seconds")
        
        # Show a preview of the report
        print(f"\n📝 Report Preview (first 500 characters):")
        print("-" * 30)
        print(results['report_content'][:500] + "...")
    else:
        print(f"❌ Research failed: {results['error']}")
    
    print("\n" + "=" * 50 + "\n")

async def example_advanced_research():
    """Example of advanced research with custom configuration."""
    print("🔬 Example 2: Advanced Research with Custom Configuration")
    print("=" * 50)
    
    analyst = ResearchAnalyst()
    
    # Validate system first
    validation = await analyst.validate_system()
    print(f"System Status: {validation['overall_status']}")
    
    if validation['overall_status'] == 'ready':
        query = "Impact of artificial intelligence on healthcare delivery"
        
        # Custom configuration
        config_overrides = {
            "output_format": "markdown",
            "max_sources": 8,
            "include_citations": True,
            "target_audience": "academic",
            "user_context": "Focus on recent developments in the last 2 years"
        }
        
        print(f"🔍 Researching: {query}")
        print(f"⚙️ Configuration: {json.dumps(config_overrides, indent=2)}")
        
        results = await analyst.conduct_research(query, config_overrides)
        
        if "error" not in results:
            print(f"✅ Research completed successfully!")
            print(f"📄 Report saved to: {results['file_path']}")
            print(f"📊 Sources analyzed: {results['research_summary']['total_sources']}")
            print(f"⚖️ Evidence strength: {results['research_summary']['evidence_strength']}")
            print(f"🤝 Agreements found: {results['research_summary']['agreements_found']}")
            print(f"❌ Disagreements found: {results['research_summary']['disagreements_found']}")
            print(f"⚠️ Biases identified: {results['research_summary']['biases_identified']}")
            
            # Show source breakdown
            print(f"\n📚 Source Breakdown:")
            for source_type, count in results['research_summary']['sources_by_type'].items():
                print(f"  - {source_type}: {count}")
        else:
            print(f"❌ Research failed: {results['error']}")
    else:
        print("❌ System validation failed. Please check configuration.")
    
    print("\n" + "=" * 50 + "\n")

async def example_multiple_queries():
    """Example of conducting multiple research queries."""
    print("🔬 Example 3: Multiple Research Queries")
    print("=" * 50)
    
    queries = [
        "Latest developments in renewable energy technology",
        "Machine learning applications in cybersecurity",
        "Future of remote work post-pandemic"
    ]
    
    analyst = ResearchAnalyst()
    
    for i, query in enumerate(queries, 1):
        print(f"🔍 Query {i}: {query}")
        
        # Simple configuration for each query
        config = {
            "output_format": "markdown",
            "max_sources": 5,
            "target_audience": "business"
        }
        
        results = await analyst.conduct_research(query, config)
        
        if "error" not in results:
            print(f"  ✅ Completed in {results['processing_metadata']['duration_seconds']:.2f}s")
            print(f"  📊 Sources: {results['research_summary']['total_sources']}")
            print(f"  ⚖️ Evidence: {results['research_summary']['evidence_strength']}")
        else:
            print(f"  ❌ Failed: {results['error']}")
        
        print()
    
    print("=" * 50 + "\n")

async def example_system_info():
    """Example of getting system information."""
    print("🔬 Example 4: System Information")
    print("=" * 50)
    
    analyst = ResearchAnalyst()
    
    # Get system configuration
    config = analyst.get_system_config()
    print("⚙️ System Configuration:")
    print(json.dumps(config, indent=2))
    
    print("\n🤖 Agent Information:")
    agent_info = analyst.get_agent_info()
    for agent_name, info in agent_info.items():
        print(f"  - {agent_name}: {info['description']}")
    
    print("\n🔍 System Validation:")
    validation = await analyst.validate_system()
    print(f"  Overall Status: {validation['overall_status']}")
    
    if validation['errors']:
        print("  Errors:")
        for error in validation['errors']:
            print(f"    - {error}")
    
    print("\n" + "=" * 50 + "\n")

async def main():
    """Run all examples."""
    print("🚀 AI Research Analysis System - Example Usage")
    print("=" * 60)
    
    try:
        # Run examples
        await example_system_info()
        await example_basic_research()
        await example_advanced_research()
        await example_multiple_queries()
        
        print("✅ All examples completed!")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("\n💡 Make sure you have:")
        print("  1. Set up your .env file with OpenAI API key")
        print("  2. Installed all required dependencies")
        print("  3. Have an active internet connection")

if __name__ == "__main__":
    # Run the examples
    asyncio.run(main()) 