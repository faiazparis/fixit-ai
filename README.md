# 🔧 iFixit Repair Guide API

A **FastAPI-based REST API** for searching and retrieving repair guides from iFixit, with optional **AI-powered summaries** using DeepSeek.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🔍 **Smart Search**: Search repair guides by device name, model, or brand
- 📖 **Detailed Guides**: Get complete repair guides with tools, parts, and step-by-step instructions
- 🤖 **AI Summaries**: Generate beginner-friendly summaries using DeepSeek AI (optional)
- 📊 **Popular Devices**: Get suggestions for common devices
- 🚀 **High Performance**: Built with FastAPI for speed and efficiency
- 📚 **Interactive Docs**: Auto-generated Swagger UI documentation
- 🛡️ **Production Ready**: Proper error handling, logging, and security

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)

### Installation (3 Steps)

1. **Clone & Navigate**
   ```bash
   git clone https://github.com/yourusername/fixit.git
   cd fixit
   ```

2. **Quick Start (Recommended)**
   ```bash
   python start.py
   ```
   *This will automatically check dependencies, setup environment, and start the server*

3. **Manual Setup (Alternative)**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Copy environment template
   cp .env.example .env
   
   # Start the API server
   python app.py
   ```

### 🎯 Access Your API

Once running, visit these URLs:

- **📚 Interactive API Docs**: http://localhost:8000/docs
- **💚 Health Check**: http://localhost:8000/health  
- **🏠 API Home**: http://localhost:8000/

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `GET` | `/` | API information | `curl http://localhost:8000/` |
| `GET` | `/health` | Health check | `curl http://localhost:8000/health` |
| `GET` | `/docs` | Interactive docs | Visit in browser |
| `GET` | `/search?q={query}` | Quick search | `curl "http://localhost:8000/search?q=iPhone%2014"` |
| `POST` | `/search` | Advanced search | See examples below |
| `GET` | `/guides/{url}` | Get repair guides | `curl "http://localhost:8000/guides/..."` |
| `POST` | `/summarize` | AI summary | See examples below |
| `GET` | `/popular` | Popular devices | `curl http://localhost:8000/popular` |

## 💡 Usage Examples

### 1. Quick Search (GET)
```bash
# Search for iPhone 14 repair guides
curl "http://localhost:8000/search?q=iPhone%2014&max_results=5"
```

### 2. Advanced Search (POST)
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Samsung Galaxy S23",
    "max_results": 10
  }'
```

### 3. Get AI Summary
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "device_url": "https://www.ifixit.com/Guide/iPhone+14+Screen+Replacement/173000",
    "summary_type": "beginner"
  }'
```

### 4. Get Popular Devices
```bash
curl http://localhost:8000/popular
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEEPSEEK_API_KEY` | DeepSeek API key for AI summaries | - | No (optional) |
| `PORT` | Server port | 8000 | No |
| `HOST` | Server host | 127.0.0.1 | No |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) | * | No |

### 🤖 DeepSeek AI Setup (Optional)

For AI-powered summaries:

1. **Sign up** at [DeepSeek Platform](https://platform.deepseek.com/)
2. **Get API key** from your dashboard
3. **Add to `.env`**:
   ```
   DEEPSEEK_API_KEY=sk-your-api-key-here
   ```

**Note**: Without DeepSeek API key, the app works perfectly - just without AI summaries!

## 📁 Project Structure

```
ifixit-repair-guide-api/
├── 📄 app.py                    # Main FastAPI application
├── 🚀 start.py                  # Quick start script
├── 🔧 fastapi_ifixit.py         # iFixit integration
├── 🛠️ fastapi_utils.py          # Utility functions  
├── 🤖 deepseek_summarizer.py    # AI summarization
├── 📋 requirements.txt          # Python dependencies
├── ⚙️ .env.example             # Environment template
├── 📖 README.md                 # This file
├── 📜 LICENSE                   # MIT License
├── 🤝 CONTRIBUTING.md           # Contribution guidelines
├── 📝 CHANGELOG.md              # Version history
└── 🧪 test_api.py              # API tests
```

## 🛠️ Development

### Running the Server

```bash
# Development mode (auto-reload)
python app.py

# Or with uvicorn directly
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### Testing

```bash
# Run the test suite
python test_api.py

# Or test individual endpoints
curl http://localhost:8000/health
curl "http://localhost:8000/search?q=iPhone%2014"
```

### API Documentation

Visit **http://localhost:8000/docs** for interactive API testing with Swagger UI.

## 🔒 Security & Production

### Security Features
- ✅ **Environment variables** for sensitive data
- ✅ **CORS configuration** for production
- ✅ **Input validation** with Pydantic
- ✅ **Error handling** and logging
- ✅ **Rate limiting** ready (can be added)

### Production Deployment
1. **Set proper CORS origins** in `.env`:
   ```
   ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   ```
2. **Use a production server** like Gunicorn
3. **Add authentication** if needed
4. **Monitor logs** and performance

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Steps
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [iFixit](https://www.ifixit.com/) - For providing repair guides
- [FastAPI](https://fastapi.tiangolo.com/) - For the excellent web framework
- [DeepSeek](https://platform.deepseek.com/) - For AI summarization
- [LangChain](https://www.langchain.com/) - For AI integration

## 🆘 Support & Issues

### Getting Help
1. **Check the docs**: http://localhost:8000/docs
2. **Review issues**: [GitHub Issues](https://github.com/yourusername/ifixit-repair-guide-api/issues)
3. **Create new issue**: Include environment details and error messages

### Common Issues
- **Port already in use**: Change `PORT` in `.env`
- **Import errors**: Run `pip install -r requirements.txt`
- **API key issues**: Check `.env` file format

---

**⚠️ Note**: This API is for educational and personal use. Please respect iFixit's terms of service and rate limits.

**⭐ Star this repo if it helped you!** 