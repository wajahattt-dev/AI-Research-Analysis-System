#!/usr/bin/env python3
"""
Simple test script to verify the AI Research Analysis System works correctly.
"""

import asyncio
import json
from main import ResearchAnalyst

async def test_system():
    """Test the system with a simple query."""
    print("🧪 Testing AI Research Analysis System")
    print("=" * 50)
    
    # Initialize the research analyst
    analyst = ResearchAnalyst()
    
    # Test with a simple query
    query = "artificial intelligence in healthcare"
    
    print(f"🔍 Testing query: {query}")
    print("⏳ This may take a few minutes...")
    
    try:
        # Conduct research
        results = await analyst.conduct_research(
            query=query,
            config_overrides={
                "output_format": "markdown",
                "max_sources": 5,
                "target_audience": "general"
            }
        )
        
        print("\n✅ Research completed successfully!")
        print("\n📊 Results Summary:")
        print(f"  - Topic: {query}")
        print(f"  - Sources found: {len(results.get('sources', []))}")
        print(f"  - Report generated: {results.get('report_metadata', {}).get('file_path', 'N/A')}")
        
        if 'report_content' in results:
            print(f"\n📄 Report Preview (first 500 chars):")
            print("-" * 50)
            print(results['report_content'][:500] + "...")
        
        print("\n🎉 System test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("This might be due to:")
        print("  - Missing API keys in .env file")
        print("  - Network connectivity issues")
        print("  - API rate limits")
        print("\nPlease check your configuration and try again.")

if __name__ == "__main__":
    asyncio.run(test_system()) 