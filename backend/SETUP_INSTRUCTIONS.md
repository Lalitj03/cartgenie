# CartGenie Setup Instructions

## 🚀 Improved API System - Recent Fixes Applied!

### What's Been Fixed

✅ **JSON Parsing**: Now handles markdown code blocks properly  
✅ **Web Scraping**: Added fallback mechanisms (Zyte → Direct HTTP)  
✅ **Sample Data**: Created populator script for realistic testing  
✅ **Error Handling**: Better messages throughout the system

---

## Quick Setup Guide

### 1. Environment Configuration

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

- `ZYTE_API_KEY`: Get from https://www.zyte.com/
- `GEMINI_API_KEY`: Get from https://makersuite.google.com/app/apikey
- `MISTRAL_API_KEY`: Get from https://console.mistral.ai/

### 2. Start Infrastructure Services

Ensure Docker containers are running:

```bash
docker-compose up -d
```

This starts:

- Neo4j on ports 7474 (HTTP) and 7687 (Bolt)
- Qdrant on ports 6333 (HTTP) and 6334 (Web UI)

### 3. Test Database Connections

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Test the connections
python test_production_tools.py
```

### 4. Populate Sample Data (Optional)

To test with actual data, you can:

- Add sample products to Qdrant vector database
- Set up Neo4j schema and sample price data
- Use the database initialization scripts

### 5. Test API Endpoint

```bash
# Start Django server
python manage.py runserver

# Test with curl or Postman:
# POST http://localhost:8000/api/v1/optimize-cart/
```

## Current Working Status

✅ **Fixed**: JSON parsing error in CrewAI output handling
✅ **Fixed**: Better error handling in tools for missing services
⚠️ **Needs Config**: Environment variables (API keys)
⚠️ **Needs Data**: Empty databases need sample data

The system will now provide meaningful error messages instead of crashing when external services are unavailable.
