# 🔬 AI Research Analysis System By Wajahat
<img width="864" height="607" alt="image" src="https://github.com/user-attachments/assets/a4f9b152-e0ac-4d10-aaad-085a7964c4c5" />

A comprehensive, AI-powered research analysis system that transforms research queries into detailed, professional reports using OpenAI's GPT-4 and multiple data sources.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized AI agents for routing, literature search, summarization, comparison, and report generation
- **Multi-Source Research**: Searches ArXiv, News APIs, and provides mock data for demonstration
- **Intelligent Analysis**: Cross-source comparison, bias detection, and evidence strength assessment
- **Professional Reports**: Generates comprehensive reports in Markdown or PDF format
- **Multiple Interfaces**: Choose between Streamlit (recommended) or Web interface
- **Scalable Design**: Built for enterprise-level research workflows

## 🏗️ Architecture

### Agent Network
- **RouterAgent**: Analyzes queries and creates research plans
- **LiteratureAgent**: Searches multiple academic and news sources
- **SummaryAgent**: Distills content into key insights
- **ComparisonAgent**: Identifies agreements, disagreements, and biases
- **ReportWriterAgent**: Generates professional research reports

### Data Flow
```
User Query → RouterAgent → LiteratureAgent → SummaryAgent → ComparisonAgent → ReportWriterAgent → Final Report
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- OpenAI API key
- News API key (optional)

### Setup
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-research-analysis-system
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Run setup script**:
   ```bash
   python setup.py
   ```

## 🎯 Quick Start

### Option 1: Launcher (Recommended)
```bash
python launch_interface.py
```
Choose your preferred interface from the menu.

### Option 2: Streamlit Interface
```bash
streamlit run streamlit_app.py
```
- Modern, interactive interface
- Real-time progress tracking
- Professional appearance
- Access at: http://localhost:8501

### Option 3: Web Interface
```bash
python web_interface_enhanced.py
```
- Traditional web application
- Custom HTML/CSS design
- Lightweight and fast
- Access at: http://localhost:8000

### Option 4: Command Line
```bash
python test_system.py
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Optional
NEWS_API_KEY=your_news_api_key_here
ARXIV_EMAIL=your_email_for_arxiv_api@example.com

# System Configuration
DEFAULT_OUTPUT_FORMAT=markdown
MAX_SOURCES_PER_QUERY=10
MAX_ARTICLES_PER_SOURCE=5
```

## 📊 Usage Examples

### Basic Research
```python
from main import ResearchAnalyst

analyst = ResearchAnalyst()
results = await analyst.conduct_research("artificial intelligence in healthcare")
```

### Advanced Configuration
```python
results = await analyst.conduct_research(
    query="quantum computing applications",
    config_overrides={
        "output_format": "pdf",
        "max_sources": 12,
        "target_audience": "academic",
        "include_citations": True
    }
)
```

## 🎨 Interface Comparison

| Feature | Streamlit | Web Interface |
|---------|-----------|---------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Customization** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Mobile Friendly** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Setup Complexity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 📁 Project Structure

```
ai-research-analysis-system/
├── agents/                 # AI agent implementations
│   ├── base_agent.py      # Base agent class
│   ├── router_agent.py    # Query routing and planning
│   ├── literature_agent.py # Source collection
│   ├── summary_agent.py   # Content summarization
│   ├── comparison_agent.py # Cross-source analysis
│   └── report_writer_agent.py # Report generation
├── utils/                  # Utility modules
│   ├── config.py          # Configuration management
│   ├── formatters.py      # Data formatting utilities
│   └── scrapers.py        # Web scraping and API clients
├── prompts/               # AI prompt templates
│   └── agent_prompts.py   # System prompts for each agent
├── reports/               # Generated reports
├── data/                  # Data storage
├── streamlit_app.py       # Streamlit interface
├── web_interface_enhanced.py # Web interface
├── launch_interface.py    # Interface launcher
├── main.py               # Main system orchestrator
├── test_system.py        # System testing
└── requirements.txt      # Python dependencies
```

## 🔍 API Reference

### ResearchAnalyst Class

#### `conduct_research(query, config_overrides=None)`
Conducts comprehensive research analysis.

**Parameters:**
- `query` (str): Research question
- `config_overrides` (dict, optional): Configuration overrides

**Returns:**
- `dict`: Research results including sources, summaries, comparison, and report

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output_format` | str | "markdown" | Report format (markdown/pdf) |
| `max_sources` | int | 10 | Maximum sources to analyze |
| `target_audience` | str | "general" | Report audience (general/academic/business/technical) |
| `include_citations` | bool | True | Include citations in report |

## 🧪 Testing

### Run System Test
```bash
python test_system.py
```

### Run Examples
```bash
python example_usage.py
```

## 🚀 Deployment

### Local Development
```bash
# Streamlit
streamlit run streamlit_app.py

# Web Interface
python web_interface_enhanced.py

# Both with launcher
python launch_interface.py
```

### Production Deployment
1. Set up environment variables
2. Configure reverse proxy (nginx)
3. Use process manager (systemd, PM2)
4. Enable SSL certificates

## 🔧 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify OpenAI API key in `.env`
   - Check API key permissions and quota

2. **Import Errors**
   - Install missing dependencies: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **No Sources Found**
   - System provides mock data when no real sources are found
   - Check internet connectivity
   - Verify API keys for external services

4. **Interface Not Loading**
   - Check if port is available
   - Verify firewall settings
   - Try different port: `--server.port 8502`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- ArXiv for academic papers
- NewsAPI for news articles
- Streamlit for the web interface framework
- FastAPI for the web server

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the example usage files

---

**Made with ❤️ for the research community by Wajahat Hussain** 
