# Contributing to iFixit Repair Guide API

Thank you for your interest in contributing to the iFixit Repair Guide API! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** for your changes
4. **Set up the development environment**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/ifixit-repair-guide-api.git
cd ifixit-repair-guide-api

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys (optional)

# Run the development server
python app.py
```

## Code Style Guidelines

### Python Code
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints for all function parameters and return values
- Add docstrings for all public functions and classes
- Keep functions focused and under 50 lines when possible

### API Design
- Follow RESTful principles
- Use proper HTTP status codes
- Include comprehensive error messages
- Add input validation using Pydantic models

### Testing
- Write tests for new features
- Ensure all tests pass before submitting
- Run the test suite: `python test_api.py`

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update the README** if adding new features
5. **Submit a pull request** with a clear description

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tests pass locally
- [ ] API endpoints tested
- [ ] Documentation updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
```

## Reporting Issues

When reporting issues, please include:

1. **Environment details** (OS, Python version)
2. **Steps to reproduce** the issue
3. **Expected vs actual behavior**
4. **Error messages** and stack traces
5. **API request/response examples** if applicable

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's coding standards

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🚀 