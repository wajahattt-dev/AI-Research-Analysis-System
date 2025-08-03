"""
FastAPI web interface for the AI Research Analysis Project.
"""
import asyncio
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from main import ResearchAnalyst

# Initialize FastAPI app
app = FastAPI(
    title="AI Research Analysis System",
    description="An autonomous research assistant that conducts multi-source literature reviews",
    version="1.0.0"
)

# Initialize research analyst
analyst = ResearchAnalyst()

# Pydantic models for API requests/responses
class ResearchRequest(BaseModel):
    query: str
    output_format: str = "markdown"
    max_sources: int = 10
    include_citations: bool = True
    target_audience: str = "general"
    user_context: Optional[str] = None

class ResearchResponse(BaseModel):
    query: str
    status: str
    report_content: Optional[str] = None
    file_path: Optional[str] = None
    research_summary: Optional[Dict[str, Any]] = None
    processing_metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SystemStatusResponse(BaseModel):
    overall_status: str
    agents: Dict[str, Any]
    config: Dict[str, Any]
    errors: List[str]

# In-memory storage for research results (in production, use a database)
research_results = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML interface."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Research Analysis System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            textarea { height: 100px; resize: vertical; }
            button { background-color: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background-color: #2980b9; }
            .status { margin-top: 20px; padding: 15px; border-radius: 5px; }
            .status.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .status.error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .status.info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            .results { margin-top: 20px; }
            .loading { text-align: center; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔬 AI Research Analysis System</h1>
            
            <form id="researchForm">
                <div class="form-group">
                    <label for="query">Research Query:</label>
                    <textarea id="query" name="query" placeholder="Enter your research question here..." required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="output_format">Output Format:</label>
                    <select id="output_format" name="output_format">
                        <option value="markdown">Markdown</option>
                        <option value="pdf">PDF</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="max_sources">Maximum Sources:</label>
                    <input type="number" id="max_sources" name="max_sources" value="10" min="1" max="20">
                </div>
                
                <div class="form-group">
                    <label for="target_audience">Target Audience:</label>
                    <select id="target_audience" name="target_audience">
                        <option value="general">General</option>
                        <option value="academic">Academic</option>
                        <option value="business">Business</option>
                        <option value="technical">Technical</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="user_context">Additional Context (Optional):</label>
                    <textarea id="user_context" name="user_context" placeholder="Any additional context or specific requirements..."></textarea>
                </div>
                
                <button type="submit">🚀 Start Research</button>
            </form>
            
            <div id="status" class="status" style="display: none;"></div>
            <div id="results" class="results"></div>
        </div>
        
        <script>
            document.getElementById('researchForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = {
                    query: formData.get('query'),
                    output_format: formData.get('output_format'),
                    max_sources: parseInt(formData.get('max_sources')),
                    target_audience: formData.get('target_audience'),
                    user_context: formData.get('user_context') || null
                };
                
                // Show loading status
                const statusDiv = document.getElementById('status');
                statusDiv.style.display = 'block';
                statusDiv.className = 'status info';
                statusDiv.innerHTML = '<div class="loading">🔍 Conducting research... This may take a few minutes.</div>';
                
                try {
                    const response = await fetch('/api/research', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (result.error) {
                        statusDiv.className = 'status error';
                        statusDiv.innerHTML = `❌ Error: ${result.error}`;
                    } else {
                        statusDiv.className = 'status success';
                        statusDiv.innerHTML = `✅ Research completed successfully!<br>
                            📊 Sources analyzed: ${result.research_summary.total_sources}<br>
                            ⚖️ Evidence strength: ${result.research_summary.evidence_strength}<br>
                            ⏱️ Duration: ${result.processing_metadata.duration_seconds.toFixed(1)} seconds`;
                        
                        // Show results
                        const resultsDiv = document.getElementById('results');
                        resultsDiv.innerHTML = `
                            <h3>📄 Research Report</h3>
                            <p><strong>Query:</strong> ${result.query}</p>
                            <p><strong>File saved:</strong> ${result.file_path}</p>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 15px;">
                                <h4>Report Preview:</h4>
                                <pre style="white-space: pre-wrap; font-size: 14px;">${result.report_content.substring(0, 1000)}...</pre>
                            </div>
                            <p><a href="/download/${result.file_path.split('/').pop()}" target="_blank">📥 Download Full Report</a></p>
                        `;
                    }
                } catch (error) {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = `❌ Network error: ${error.message}`;
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    """Conduct research on a given query."""
    try:
        # Prepare configuration overrides
        config_overrides = {
            "output_format": request.output_format,
            "max_sources": request.max_sources,
            "include_citations": request.include_citations,
            "target_audience": request.target_audience,
            "user_context": request.user_context
        }
        
        # Conduct research
        results = await analyst.conduct_research(request.query, config_overrides)
        
        if "error" in results:
            return ResearchResponse(
                query=request.query,
                status="error",
                error=results["error"]
            )
        
        # Store results for later access
        research_results[request.query] = results
        
        return ResearchResponse(
            query=request.query,
            status="completed",
            report_content=results["report_content"],
            file_path=results["file_path"],
            research_summary=results["research_summary"],
            processing_metadata=results["processing_metadata"]
        )
        
    except Exception as e:
        return ResearchResponse(
            query=request.query,
            status="error",
            error=str(e)
        )

@app.get("/api/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get the current system status."""
    try:
        status = await analyst.validate_system()
        return SystemStatusResponse(**status)
    except Exception as e:
        return SystemStatusResponse(
            overall_status="error",
            agents={},
            config={},
            errors=[str(e)]
        )

@app.get("/api/config")
async def get_system_config():
    """Get the current system configuration."""
    return analyst.get_system_config()

@app.get("/api/agents")
async def get_agent_info():
    """Get information about all agents."""
    return analyst.get_agent_info()

@app.get("/download/{filename}")
async def download_report(filename: str):
    """Download a generated report file."""
    file_path = os.path.join("reports", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@app.get("/api/results/{query}")
async def get_research_results(query: str):
    """Get stored research results for a query."""
    if query not in research_results:
        raise HTTPException(status_code=404, detail="Research results not found")
    
    return research_results[query]

@app.delete("/api/results/{query}")
async def delete_research_results(query: str):
    """Delete stored research results for a query."""
    if query in research_results:
        del research_results[query]
        return {"message": "Results deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Research results not found")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        "web_interface:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 