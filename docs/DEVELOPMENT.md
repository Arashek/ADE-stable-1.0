# CloudEV.ai Early Access System Development Guide

## Development Setup

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- Node.js 14+
- Git

### Local Development Environment

1. Clone the repository:
```bash
git clone https://github.com/cloudev/early-access.git
cd early-access
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
npm install
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start MongoDB:
```bash
# Using Docker
docker-compose up -d mongodb

# Or install MongoDB locally
```

6. Initialize the database:
```bash
python scripts/init_db.py
```

7. Start the development server:
```bash
# Backend
uvicorn src.main:app --reload

# Frontend
npm run dev
```

## Project Structure

```
src/
├── core/                    # Core backend functionality
│   ├── api/                # API routes
│   │   └── routes/
│   │       ├── admin/     # Admin endpoints
│   │       └── public/    # Public endpoints
│   ├── auth/              # Authentication
│   ├── config/            # Configuration
│   ├── db/                # Database models
│   ├── email/             # Email service
│   └── storage/           # Data storage
├── web/                    # Frontend components
│   └── components/
│       ├── admin/         # Admin panel components
│       └── landing/       # Landing page components
└── tests/                  # Test files
```

## Development Workflow

### 1. Feature Development

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes following the coding standards:
   - Use type hints
   - Write docstrings
   - Follow PEP 8
   - Add tests

3. Run tests:
```bash
pytest
```

4. Format code:
```bash
black .
isort .
```

5. Commit your changes:
```bash
git add .
git commit -m "feat: description of your changes"
```

6. Push to remote:
```bash
git push origin feature/your-feature-name
```

7. Create a Pull Request

### 2. Testing

#### Unit Tests
- Located in `tests/`
- Use pytest
- Follow AAA pattern (Arrange, Act, Assert)
- Mock external services

Example:
```python
@pytest.mark.asyncio
async def test_signup_validation():
    # Arrange
    client = TestClient(public_router)
    
    # Act
    response = client.post("/early-access/signup", json={
        "email": "invalid-email",
        "privacy_policy_accepted": True
    })
    
    # Assert
    assert response.status_code == 422
```

#### Integration Tests
- Test API endpoints
- Test database operations
- Test email service
- Use test database

#### End-to-End Tests
- Test complete user flows
- Use Cypress or Playwright
- Test in staging environment

### 3. Code Quality

#### Linting
```bash
# Run linters
flake8
mypy .

# Fix formatting
black .
isort .
```

#### Type Checking
```bash
# Run type checker
mypy .

# Generate type stubs
stubgen src/
```

### 4. Documentation

#### API Documentation
- Use OpenAPI/Swagger
- Document all endpoints
- Include examples
- Update when changing endpoints

#### Code Documentation
- Use docstrings
- Follow Google style
- Include type hints
- Document complex logic

Example:
```python
def process_request(request: EarlyAccessRequest) -> Dict[str, Any]:
    """Process an early access request.
    
    Args:
        request: The early access request to process.
        
    Returns:
        Dict containing processed request data.
        
    Raises:
        ValidationError: If request data is invalid.
    """
    pass
```

### 5. Deployment

#### Staging Deployment
1. Push to staging branch
2. Run staging tests
3. Deploy to staging environment
4. Run smoke tests

#### Production Deployment
1. Create release branch
2. Run all tests
3. Update version
4. Deploy to production
5. Monitor metrics

## Best Practices

### 1. Error Handling
- Use custom exceptions
- Log errors properly
- Return appropriate status codes
- Include error details in response

### 2. Security
- Validate all inputs
- Sanitize data
- Use HTTPS
- Implement rate limiting
- Follow OWASP guidelines

### 3. Performance
- Use async/await
- Implement caching
- Optimize database queries
- Monitor response times

### 4. Monitoring
- Use structured logging
- Track metrics
- Set up alerts
- Monitor error rates

### 5. Database
- Use migrations
- Index properly
- Backup regularly
- Monitor size

## Troubleshooting

### Common Issues

1. Database Connection
```bash
# Check MongoDB status
docker-compose ps mongodb

# Check logs
docker-compose logs mongodb
```

2. Email Service
```bash
# Test email configuration
python scripts/test_email.py
```

3. API Issues
```bash
# Check API logs
tail -f logs/api.log

# Test endpoints
curl -X POST http://localhost:8000/early-access/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

### Debugging

1. Enable debug mode:
```bash
export DEBUG=1
```

2. Use logging:
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

3. Use debugger:
```python
import pdb; pdb.set_trace()
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Create a Pull Request

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release branch
4. Run tests
5. Deploy to staging
6. Run smoke tests
7. Deploy to production
8. Create GitHub release

## Support

- Documentation: https://docs.cloudev.ai
- Issues: https://github.com/cloudev/early-access/issues
- Email: support@cloudev.ai 