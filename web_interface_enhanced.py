#!/usr/bin/env python3
"""
Enhanced Web Interface for AI Research Analysis System
A beautiful, responsive web interface built with FastAPI and modern CSS.
"""

import asyncio
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from main import ResearchAnalyst
from utils.config import config
from pathlib import Path

app = FastAPI(
    title="AI Research Analysis System",
    description="Transform research queries into comprehensive AI-powered analysis reports",
    version="1.0.0"
)

# Initialize the research analyst
analyst = ResearchAnalyst()

# Pydantic models
class ResearchRequest(BaseModel):
    query: str
    output_format: str = "markdown"
    max_sources: int = 8
    target_audience: str = "general"
    include_citations: bool = True

class ResearchResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Store research results in memory (in production, use a database)
research_results = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML interface."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Research Analysis System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #000000 100%);
            min-height: 100vh;
            color: #ffffff;
            position: relative;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: #ffffff;
            margin-bottom: 40px;
            position: relative;
        }

        .header::after {
            content: '';
            position: absolute;
            bottom: -20px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 2px;
            background: linear-gradient(90deg, transparent, #ffffff, transparent);
        }

        .header h1 {
            font-size: 3.5rem;
            margin-bottom: 15px;
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
            font-weight: 300;
            letter-spacing: 2px;
        }

        .header p {
            font-size: 1.3rem;
            opacity: 0.8;
            font-weight: 300;
            letter-spacing: 1px;
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }

        .card {
            background: rgba(20, 20, 20, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 35px;
            box-shadow: 
                0 20px 40px rgba(0, 0, 0, 0.5),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
        }

        .card:hover {
            transform: translateY(-8px);
            box-shadow: 
                0 30px 60px rgba(0, 0, 0, 0.7),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .card h2 {
            color: #ffffff;
            margin-bottom: 25px;
            font-size: 2rem;
            font-weight: 300;
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }

        .form-group {
            margin-bottom: 25px;
        }

        .form-group label {
            display: block;
            margin-bottom: 10px;
            font-weight: 500;
            color: #ffffff;
            font-size: 0.95rem;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 15px;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            font-size: 16px;
            color: #ffffff;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }

        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: #ffffff;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.7);
        }

        .form-group input::placeholder,
        .form-group textarea::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }

        .form-group textarea {
            resize: vertical;
            min-height: 120px;
        }

        .btn {
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
            color: #000000;
            border: none;
            padding: 18px 30px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
            background: linear-gradient(135deg, #f8f8f8 0%, #ffffff 100%);
        }

        .btn:active {
            transform: translateY(-1px);
        }

        .btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .status {
            padding: 18px;
            border-radius: 12px;
            margin-bottom: 25px;
            display: none;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }

        .status.success {
            background: rgba(34, 197, 94, 0.1);
            border-color: rgba(34, 197, 94, 0.3);
            color: #22c55e;
        }

        .status.error {
            background: rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.3);
            color: #ef4444;
        }

        .status.info {
            background: rgba(59, 130, 246, 0.1);
            border-color: rgba(59, 130, 246, 0.3);
            color: #3b82f6;
        }

        .progress-container {
            display: none;
            margin: 25px 0;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            overflow: hidden;
            backdrop-filter: blur(5px);
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #ffffff, #f0f0f0);
            width: 0%;
            transition: width 0.5s ease;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }

        .results {
            display: none;
            margin-top: 40px;
        }

        .results h3 {
            color: #ffffff;
            margin-bottom: 20px;
            font-weight: 300;
            letter-spacing: 1px;
        }

        .report-content {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            max-height: 400px;
            overflow-y: auto;
            backdrop-filter: blur(10px);
        }

        .report-content::-webkit-scrollbar {
            width: 8px;
        }

        .report-content::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }

        .report-content::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 10px;
        }

        .download-btn {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: #ffffff;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-top: 15px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
        }

        .download-btn:hover {
            background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(34, 197, 94, 0.4);
        }

        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }

        .metric {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
            color: #ffffff;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .metric:hover {
            transform: translateY(-3px);
            border-color: rgba(255, 255, 255, 0.2);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .metric h4 {
            font-size: 0.9rem;
            margin-bottom: 8px;
            opacity: 0.8;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .metric .value {
            font-size: 2.2rem;
            font-weight: 300;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }

        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2.5rem;
            }

            .card {
                padding: 25px;
            }
        }

        /* Custom checkbox styling */
        .form-group input[type="checkbox"] {
            width: auto;
            margin-right: 10px;
            accent-color: #ffffff;
        }

        /* Range slider styling */
        .form-group input[type="range"] {
            -webkit-appearance: none;
            appearance: none;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            height: 8px;
            outline: none;
        }

        .form-group input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            background: #ffffff;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }

        .form-group input[type="range"]::-moz-range-thumb {
            width: 20px;
            height: 20px;
            background: #ffffff;
            border-radius: 50%;
            cursor: pointer;
            border: none;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> AI Research Analysis System</h1>
            <p>Transform your research queries into comprehensive, AI-powered analysis reports</p>
        </div>

        <div class="main-content">
            <div class="card">
                <h2>🚀 Start Your Research</h2>
                <form id="researchForm">
                    <div class="form-group">
                        <label for="query">Research Query</label>
                        <textarea id="query" name="query" placeholder="Enter your research question here..." required></textarea>
                    </div>

                    <div class="form-group">
                        <label for="outputFormat">Output Format</label>
                        <select id="outputFormat" name="outputFormat">
                            <option value="markdown">Markdown</option>
                            <option value="pdf">PDF</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="maxSources">Maximum Sources</label>
                        <input type="range" id="maxSources" name="maxSources" min="3" max="15" value="8">
                        <span id="maxSourcesValue">8</span>
                    </div>

                    <div class="form-group">
                        <label for="targetAudience">Target Audience</label>
                        <select id="targetAudience" name="targetAudience">
                            <option value="general">General</option>
                            <option value="academic">Academic</option>
                            <option value="business">Business</option>
                            <option value="technical">Technical</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="includeCitations" name="includeCitations" checked>
                            Include Citations
                        </label>
                    </div>

                    <button type="submit" class="btn" id="submitBtn">🔍 Start Research Analysis</button>
                </form>

                <div id="status" class="status"></div>

                <div class="progress-container" id="progressContainer">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <p id="progressText">Initializing...</p>
                </div>
            </div>

            <div class="card">
                <h2>📊 System Status</h2>
                <div id="systemStatus">
                    <p><strong>Version:</strong> 1.0.0</p>
                    <p><strong>Model:</strong> GPT-4 Turbo</p>
                    <p><strong>Sources:</strong> ArXiv, News API, Mock Data</p>
                </div>

                <h2>📈 Quick Stats</h2>
                <div class="metrics" id="metrics">
                    <div class="metric">
                        <h4>📚 Sources</h4>
                        <div class="value">-</div>
                    </div>
                    <div class="metric">
                        <h4>⏱️ Time</h4>
                        <div class="value">-</div>
                    </div>
                    <div class="metric">
                        <h4>💪 Evidence</h4>
                        <div class="value">-</div>
                    </div>
                </div>

                <h2>📄 Recent Reports</h2>
                <div id="recentReports">
                    <p>No reports generated yet.</p>
                </div>
            </div>
        </div>

        <div class="results" id="results">
            <div class="card">
                <h2>📋 Research Report</h2>
                <div class="report-content" id="reportContent"></div>
                <a href="#" class="download-btn" id="downloadBtn" style="display: none;">📥 Download Report</a>
            </div>
        </div>
    </div>

    <script>
        // Update max sources display
        document.getElementById('maxSources').addEventListener('input', function() {
            document.getElementById('maxSourcesValue').textContent = this.value;
        });

        // Form submission
        document.getElementById('researchForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                query: formData.get('query'),
                output_format: formData.get('outputFormat'),
                max_sources: parseInt(formData.get('maxSources')),
                target_audience: formData.get('targetAudience'),
                include_citations: formData.get('includeCitations') === 'on'
            };

            // Show progress
            document.getElementById('progressContainer').style.display = 'block';
            document.getElementById('submitBtn').disabled = true;
            showStatus('info', '🤖 AI agents are analyzing your research query...');

            try {
                const response = await fetch('/api/research', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (result.success) {
                    showStatus('success', '✅ Research completed successfully!');
                    displayResults(result.data);
                } else {
                    showStatus('error', '❌ Research failed: ' + result.error);
                }
            } catch (error) {
                showStatus('error', '❌ Network error: ' + error.message);
            } finally {
                document.getElementById('progressContainer').style.display = 'none';
                document.getElementById('submitBtn').disabled = false;
            }
        });

        function showStatus(type, message) {
            const status = document.getElementById('status');
            status.className = `status ${type}`;
            status.textContent = message;
            status.style.display = 'block';
        }

        function displayResults(data) {
            const results = document.getElementById('results');
            const reportContent = document.getElementById('reportContent');
            const downloadBtn = document.getElementById('downloadBtn');

            if (data.report_content) {
                reportContent.innerHTML = data.report_content.replace(/\\n/g, '<br>');
                downloadBtn.style.display = 'inline-block';
                downloadBtn.href = `/download/${data.report_metadata?.file_path?.split('/').pop() || 'report.md'}`;
            }

            // Update metrics
            updateMetrics(data);

            results.style.display = 'block';
        }

        function updateMetrics(data) {
            const metrics = document.getElementById('metrics');
            
            const numSources = data.sources?.length || 0;
            const processingTime = data.processing_metadata?.processing_time || 0;
            const evidenceStrength = data.comparison?.strength_of_evidence?.overall_strength || 'unknown';

            metrics.innerHTML = `
                <div class="metric">
                    <h4>📚 Sources</h4>
                    <div class="value">${numSources}</div>
                </div>
                <div class="metric">
                    <h4>⏱️ Time</h4>
                    <div class="value">${processingTime.toFixed(1)}s</div>
                </div>
                <div class="metric">
                    <h4>💪 Evidence</h4>
                    <div class="value">${evidenceStrength}</div>
                </div>
            `;
        }

        // Simulate progress
        function updateProgress(percent, text) {
            document.getElementById('progressFill').style.width = percent + '%';
            document.getElementById('progressText').textContent = text;
        }

        // Load recent reports on page load
        window.addEventListener('load', async function() {
            try {
                const response = await fetch('/api/recent-reports');
                const reports = await response.json();
                
                const recentReports = document.getElementById('recentReports');
                if (reports.length > 0) {
                    recentReports.innerHTML = reports.map(report => 
                        `<div style="margin-bottom: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                            <strong>${report.name}</strong><br>
                            <small>${report.date}</small>
                        </div>`
                    ).join('');
                }
            } catch (error) {
                console.error('Failed to load recent reports:', error);
            }
        });
    </script>
</body>
</html>
    """

@app.post("/api/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    """Conduct research analysis."""
    try:
        # Configure research
        config_overrides = {
            "output_format": request.output_format,
            "max_sources": request.max_sources,
            "target_audience": request.target_audience,
            "include_citations": request.include_citations
        }

        # Run research
        results = await analyst.conduct_research(request.query, config_overrides)
        
        # Store results
        research_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        research_results[research_id] = results

        return ResearchResponse(
            success=True,
            message="Research completed successfully",
            data=results
        )

    except Exception as e:
        return ResearchResponse(
            success=False,
            message="Research failed",
            error=str(e)
        )

@app.get("/api/recent-reports")
async def get_recent_reports():
    """Get list of recent reports."""
    reports_dir = Path("./reports")
    if not reports_dir.exists():
        return []
    
    reports = list(reports_dir.glob("*.md"))
    reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    recent_reports = []
    for report in reports[:5]:
        report_name = report.stem
        report_date = datetime.fromtimestamp(report.stat().st_mtime)
        recent_reports.append({
            "name": report_name,
            "date": report_date.strftime("%Y-%m-%d %H:%M"),
            "path": str(report)
        })
    
    return recent_reports

@app.get("/download/{filename}")
async def download_report(filename: str):
    """Download a report file."""
    file_path = f"./reports/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="Report not found")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run("web_interface_enhanced:app", host="0.0.0.0", port=8000, reload=True) 