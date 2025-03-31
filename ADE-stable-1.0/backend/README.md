# ADE Owner Panel Backend

The backend service for the ADE (Autonomous Development Environment) Owner Panel, providing administrative and management capabilities for the cloudev.ai platform.

## Features

- **Dashboard & Analytics**
  - System metrics and health monitoring
  - User statistics and activity tracking
  - Performance analytics and reporting

- **Security Management**
  - User authentication and authorization
  - Role-based access control
  - API key management
  - Security event monitoring

- **Frontend Management**
  - Theme customization
  - Navigation configuration
  - Content management
  - Component library

- **System Administration**
  - Backup and restore functionality
  - System diagnostics
  - Log management
  - Configuration management

- **Technical Support**
  - Support ticket management
  - System health monitoring
  - Error tracking and reporting
  - Performance optimization

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Node.js 14+ (for frontend)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cloudev-ai/ade-platform.git
cd ade-platform/backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
alembic upgrade head
```

## Configuration

The application can be configured through environment variables or the `.env` file:

```env
# Application
APP_NAME=ADE Owner Panel
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ade_db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
MFA_ENABLED=true

# Frontend
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000"]

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

## Running the Application

1. Start the development server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
```
http://localhost:8000/docs
```

3. Access the health check endpoint:
```
http://localhost:8000/health
```

## API Documentation

The API documentation is available at `/docs` and includes:

- Interactive API documentation
- Request/response examples
- Authentication details
- Rate limiting information

## Development

### Code Style

The project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Run the formatters:
```bash
black .
isort .
```

Run the linters:
```bash
flake8
mypy .
```

### Testing

Run the test suite:
```bash
pytest
```

Generate coverage report:
```bash
pytest --cov=.
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Deployment

1. Build the Docker image:
```bash
docker build -t ade-owner-panel .
```

2. Run the container:
```bash
docker run -p 8000:8000 ade-owner-panel
```

## Monitoring

The application includes:

- Prometheus metrics endpoint at `/metrics`
- Health check endpoint at `/health`
- Structured logging with rotation
- Performance monitoring
- Error tracking

## Security

Security features include:

- JWT authentication
- Role-based access control
- API key management
- Rate limiting
- CORS protection
- Input validation
- XSS protection
- CSRF protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact:
- Email: support@cloudev.ai
- Documentation: https://docs.cloudev.ai
- GitHub Issues: https://github.com/cloudev-ai/ade-platform/issues 