# CartGenie 🛒✨

**Smart AI-Powered Shopping Cart Optimization**

CartGenie is an intelligent shopping assistant that helps users save money by finding the best prices across multiple retailers. It combines a Chrome extension for seamless cart detection with a powerful Django backend featuring AI agents, vector search, and knowledge graphs.

## 🎯 Key Features

- **Multi-Platform Cart Detection**: Automatically detects shopping carts on Amazon, Flipkart, BigBasket, and Swiggy Instamart
- **AI-Powered Price Analysis**: Uses CrewAI agents for intelligent product research and savings analysis
- **Semantic Product Matching**: Vector similarity search finds equivalent products across different retailers
- **Real-Time Price Scraping**: Geolocation-aware web scraping for current pricing data
- **Knowledge Graph Integration**: Price history and retailer relationships stored in Neo4j
- **Chrome Extension UI**: Seamless integration with shopping workflows

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  Chrome         │    │  Django Backend  │    │  AI & Data Layer    │
│  Extension      │    │                  │    │                     │
├─────────────────┤    ├──────────────────┤    ├─────────────────────┤
│ • content.js    │───▶│ • API Views      │───▶│ • CrewAI Agents     │
│ • background.js │    │ • Serializers    │    │ • Qdrant (Vectors)  │
│ • popup.html    │    │ • URL Routing    │    │ • Neo4j (Graph)     │
└─────────────────┘    └──────────────────┘    │ • Zyte (Scraping)   │
                                               └─────────────────────┘
```

### Data Flow

1. **Extension** detects cart and extracts product data
2. **Background Script** sends data to Django API
3. **Product Research Agent** finds similar products using vector search
4. **Savings Analysis Agent** calculates optimal recommendations
5. **Results** displayed in extension popup with savings breakdown

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js (for development tools)
- Docker & Docker Compose
- Chrome browser

### Backend Setup

```bash
# Clone and navigate to project
git clone <repository-url>
cd cartgenie

# Set up Python environment
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start infrastructure services
cd ..
docker-compose up -d

# Set up environment variables
cp .env.template .env
# Edit .env with your API keys and configuration

# Initialize Django
cd backend
python manage.py migrate
python manage.py runserver
```

### Chrome Extension Setup

```bash
# Open Chrome and go to chrome://extensions/
# Enable "Developer mode"
# Click "Load unpacked" and select the extension/ folder
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here

# Database Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# AI & API Keys
GEMINI_API_KEY=your-gemini-api-key
MISTRAL_API_KEY=your-mistral-api-key
ZYTE_API_KEY=your-zyte-api-key
```

## 📁 Project Structure

```
cartgenie/
├── backend/                 # Django backend application
│   ├── api/                # REST API endpoints and serializers
│   ├── cartgenie_project/  # Django project configuration
│   └── core/               # Core business logic
│       ├── agents/         # CrewAI agent definitions and tools
│       ├── db/             # Database connectors (Qdrant, Neo4j)
│       └── utils/          # Utility classes (Zyte client)
├── extension/              # Chrome extension
│   ├── content.js          # Cart detection and data extraction
│   ├── background.js       # API communication and state management
│   ├── popup/              # Extension popup UI
│   └── manifest.json       # Extension configuration
└── docker-compose.yml     # Infrastructure services
```

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest core/tests/ -v

# Extension testing
# Load extension in Chrome developer mode and test on supported sites
```

### Supported Platforms

The extension currently supports:

- **Amazon India** (`amazon.in/gp/cart/*`)
- **Flipkart** (`flipkart.com/viewcart*`)
- **BigBasket** (`bigbasket.com/basket*`)
- **Swiggy Instamart** (`swiggy.com/instamart/*/cart`)

### Adding New Platforms

1. Add platform detection logic in `extension/content.js`
2. Define CSS selectors for cart items, titles, and prices
3. Test extraction logic on target platform
4. Update platform list in documentation

### AI Agent Customization

The system uses two specialized CrewAI agents:

- **Product Research Agent**: Handles product identification and price discovery
- **Savings Analysis Agent**: Processes research data into actionable recommendations

Modify agent behavior in `backend/core/agents/crew.py`.

## 🔧 API Reference

### Cart Optimization Endpoint

**POST** `/api/v1/optimize-cart`

```json
{
  "userContext": {
    "country": "IN",
    "postalCode": "560001"
  },
  "sourceRetailer": "amazon.in",
  "items": [
    {
      "productTitle": "Sony WH-1000XM5 Headphones",
      "quantity": 1,
      "price": 29990.0,
      "currency": "INR",
      "url": "https://amazon.in/product-url"
    }
  ]
}
```

**Response:**

```json
{
  "originalTotal": 29990.0,
  "optimizedTotal": 25990.0,
  "currency": "INR",
  "totalSavings": 4000.0,
  "recommendations": [
    {
      "originalItem": {
        /* original item */
      },
      "cheapestAlternative": {
        "productTitle": "Sony WH-1000XM5 Headphones",
        "price": 25990.0,
        "currency": "INR",
        "retailer": "Flipkart",
        "url": "https://flipkart.com/alternative-url"
      }
    }
  ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8, use Black for formatting
- **JavaScript**: Use ESLint with standard configuration
- **Documentation**: Add docstrings and comments for all new functions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CrewAI** for the multi-agent framework
- **Qdrant** for vector similarity search
- **Neo4j** for graph database capabilities
- **Zyte** for web scraping infrastructure
- **Superlinked** for embedding generation (planned integration)
- **Cognee** for HTML content extraction (planned integration)

## 📞 Support

For questions, bug reports, or feature requests:

- Open an issue on GitHub
- Check existing documentation in the codebase
- Review the API reference and examples

---

**CartGenie** - Making smart shopping effortless! 🛒💡
