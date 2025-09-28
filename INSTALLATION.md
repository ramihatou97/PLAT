# PLAT Installation Guide

## Quick Start (5 minutes)

### 1. Clone and Setup
```bash
git clone https://github.com/ramihatou97/PLAT.git
cd PLAT
```

### 2. Run Demo (No dependencies required)
```bash
python demo.py
```

### 3. Full Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Initialize system
python scripts/initialize_data.py

# Start server
python main.py
```

### 4. Access System
- Web Interface: http://localhost:8000/frontend/templates/index.html
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## API Keys Required

### OpenAI (GPT-4)
- Get key from: https://platform.openai.com/
- Add to .env: `OPENAI_API_KEY=sk-...`

### Google Gemini
- Get key from: https://makersuite.google.com/
- Add to .env: `GOOGLE_API_KEY=AI...`

### Anthropic Claude
- Get key from: https://console.anthropic.com/
- Add to .env: `ANTHROPIC_API_KEY=sk-ant-...`

### PubMed (Optional)
- Register at: https://www.ncbi.nlm.nih.gov/account/
- Add to .env: `PUBMED_EMAIL=your@email.com`

## System Requirements

- Python 3.9+
- 4GB RAM minimum
- Internet connection for AI providers
- Optional: Redis for background tasks

## Troubleshooting

### Common Issues

1. **Import Errors**: Install dependencies with `pip install -r requirements.txt`
2. **API Errors**: Check your API keys in .env file
3. **Port 8000 in use**: Change port in main.py or stop other services
4. **Search not working**: Run initialization script first

### Getting Help

- Check API documentation at /docs
- Review logs in plat.log
- Run health check at /health
- See README.md for detailed information

## Development Setup

```bash
# Clone repository
git clone https://github.com/ramihatou97/PLAT.git
cd PLAT

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black src/

# Start development server
python main.py
```