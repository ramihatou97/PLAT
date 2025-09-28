# PLAT - Personal AI-Driven Neurosurgical Knowledge Management System

A comprehensive, self-updating neurosurgical encyclopedia that aggregates content from multiple sources and provides evidence-based medical reference powered by artificial intelligence.

## 🧠 Features

### Core Capabilities
- **Semantic Search**: Search across 427+ neurosurgical concepts using advanced vector similarity
- **AI-Powered Content Generation**: Leverage GPT-4, Gemini, and Claude for content creation
- **Auto-Updating**: Continuous updates from PubMed research with confidence scoring
- **Evidence-Based**: Synthesized protocols, surgical techniques, and clinical guidelines
- **Real-Time Reference**: Searchable medical reference that evolves with the field

### Content Sources
- 📚 Medical textbooks and literature
- 🔬 Latest research papers from PubMed
- 🤖 AI-generated content from multiple providers
- 📊 Evidence-based protocols and guidelines

### Search & Discovery
- Semantic similarity search using sentence transformers
- Content filtering by type, category, and confidence
- Similar concept discovery
- Real-time search analytics

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Redis (for background tasks)
- Internet connection (for AI providers and PubMed)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ramihatou97/PLAT.git
   cd PLAT
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Initialize the system**
   ```bash
   python scripts/initialize_data.py
   ```

5. **Start the server**
   ```bash
   python main.py
   ```

6. **Access the interface**
   - Web UI: http://localhost:8000/frontend/templates/index.html
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=sqlite:///./data/plat.db

# AI Provider API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# PubMed Configuration
PUBMED_EMAIL=your_email@example.com
PUBMED_API_KEY=your_ncbi_api_key_here

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
MAX_CONCEPTS=427
UPDATE_FREQUENCY_HOURS=24
MIN_CONFIDENCE_SCORE=0.7
```

### AI Provider Setup

#### OpenAI (GPT-4)
1. Get API key from https://platform.openai.com/
2. Add to `.env`: `OPENAI_API_KEY=sk-...`

#### Google Gemini
1. Get API key from https://makersuite.google.com/
2. Add to `.env`: `GOOGLE_API_KEY=AI...`

#### Anthropic Claude
1. Get API key from https://console.anthropic.com/
2. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

#### PubMed
1. Register at https://www.ncbi.nlm.nih.gov/account/
2. Add to `.env`: `PUBMED_EMAIL=your@email.com`

## 🏗️ Architecture

### System Components

```
PLAT/
├── src/plat/
│   ├── api/                 # FastAPI REST endpoints
│   ├── core/                # Configuration and utilities
│   ├── models/              # Database models
│   ├── services/            # Business logic services
│   └── db/                  # Database utilities
├── frontend/                # Web interface
├── scripts/                 # Initialization scripts
└── data/                    # Database and search index
```

### Services

1. **AI Provider Manager**: Coordinates content generation across multiple AI providers
2. **PubMed Service**: Fetches and processes latest research papers
3. **Semantic Search**: Vector-based similarity search using ChromaDB
4. **Content Management**: Handles neurosurgical concepts and metadata

## 📊 API Endpoints

### Search
- `POST /search` - Semantic search for concepts
- `GET /search/similar/{concept_id}` - Find similar concepts

### Content Generation  
- `POST /generate` - Generate content using AI providers

### PubMed Integration
- `GET /pubmed/recent` - Get recent neurosurgical papers
- `GET /pubmed/concept/{concept}` - Search papers by concept

### System
- `GET /health` - Health check
- `GET /stats` - System statistics
- `POST /update/pubmed` - Trigger content update

## 🎯 Content Types

The system manages various types of neurosurgical content:

- **Protocols**: Clinical management protocols
- **Surgical Techniques**: Step-by-step surgical procedures  
- **Clinical Guidelines**: Evidence-based treatment guidelines
- **Concepts**: General neurosurgical concepts and definitions
- **Case Studies**: Clinical case studies and examples

## 🏥 Neurosurgical Categories

- Brain Tumors (Gliomas, Meningiomas, Metastases)
- Vascular Neurosurgery (Aneurysms, AVMs, Stroke)
- Spinal Surgery (Degenerative, Traumatic, Tumors)
- Functional Neurosurgery (DBS, Epilepsy, Pain)
- Pediatric Neurosurgery
- Trauma (TBI, Spinal Trauma)
- Stereotactic Radiosurgery
- Endoscopic Surgery

## 🔍 Search Features

### Semantic Search
- Natural language queries
- Vector similarity matching
- Content-aware results
- Confidence scoring

### Filters
- Content type filtering
- Category and subcategory
- Evidence level
- Peer review status
- Confidence thresholds

### Example Searches
- "brain tumor resection techniques"
- "deep brain stimulation for Parkinson's"
- "cervical spine fusion protocols"
- "intracranial pressure management"

## 🤖 AI Integration

### Content Generation
The system uses multiple AI providers to generate comprehensive neurosurgical content:

1. **GPT-4**: Advanced medical knowledge and detailed explanations
2. **Gemini**: Google's large language model for medical content
3. **Claude**: Anthropic's AI for evidence-based information

### Consensus Building
- Multiple AI providers generate content for the same prompt
- Confidence scores determine the best response
- Future versions will synthesize multiple responses

## 📈 Updates & Maintenance

### Automatic Updates
- Daily PubMed searches for new research
- Content refresh based on latest evidence
- Confidence score recalculation
- Search index updates

### Manual Updates
- Content curation and review
- New concept addition
- Quality assurance processes

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test specific components
pytest tests/test_search_service.py
pytest tests/test_ai_providers.py
```

## 📝 Development

### Adding New Concepts
1. Use the admin interface or API endpoints
2. Include proper metadata and classifications
3. Ensure content quality and medical accuracy
4. Add to search index automatically

### Extending AI Providers
1. Implement the `AIProvider` abstract class
2. Add configuration options
3. Register in `AIProviderManager`
4. Test integration thoroughly

## 🔒 Security & Privacy

- API key protection in environment variables
- No storage of personal patient information
- HIPAA-compliant design principles
- Secure API endpoints with rate limiting

## 📚 Medical Disclaimer

**IMPORTANT**: This system is designed for educational and reference purposes only. It should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for patient care decisions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Google for Gemini API  
- Anthropic for Claude API
- NCBI for PubMed access
- The neurosurgical community for medical knowledge

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Contact the development team
- Check the documentation at `/docs`

---

**Built with ❤️ for the neurosurgical community**
