# ADE Model Training Platform

A comprehensive platform for capturing, processing, and training models using ADE learning data.

## Features

- **Data Capture**: Automatically captures learning data from ADE sessions
- **Cloud Integration**: Supports AWS and Google Cloud for data storage and model training
- **Web Interface**: User-friendly interface for managing data and training processes
- **Dataset Management**: Tools for processing and preparing training datasets
- **Model Integration**: Seamless integration with existing ADE models
- **Training Process Tracking**: Monitor and analyze training progress

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ade-platform.git
cd ade-platform
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

4. Configure cloud credentials:
   - Create `config/aws_credentials.json` for AWS credentials
   - Create `config/gcp_credentials.json` for Google Cloud credentials

5. Configure ADE integration:
   - Create `config/ade_integration.json` with your ADE API settings

## Usage

1. Start the application:
```bash
python src/web/app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Use the web interface to:
   - Monitor active ADE sessions
   - Capture and process learning data
   - Manage datasets
   - Configure cloud integration
   - Track training progress

## Project Structure

```
ade-platform/
├── config/                 # Configuration files
├── data/                   # Data storage
│   ├── learning/          # Captured learning data
│   └── models/            # Trained models
├── src/                   # Source code
│   ├── ade/              # ADE integration
│   ├── cloud/            # Cloud integration
│   └── web/              # Web application
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

The project uses:
- Black for code formatting
- Flake8 for linting
- MyPy for type checking
- isort for import sorting

Run code style checks:
```bash
black .
flake8
mypy .
isort .
```

### Documentation

Build documentation:
```bash
cd docs
make html
```

## Configuration

### ADE Integration

Configure `config/ade_integration.json`:
```json
{
    "ade_api_url": "http://your-ade-api",
    "ade_api_key": "your-api-key",
    "data_capture_enabled": true,
    "learning_data_dir": "data/learning",
    "model_data_dir": "data/models"
}
```

### AWS Integration

Configure `config/aws_credentials.json`:
```json
{
    "aws_access_key_id": "your-access-key",
    "aws_secret_access_key": "your-secret-key",
    "region": "us-east-1"
}
```

### Google Cloud Integration

Configure `config/gcp_credentials.json`:
```json
{
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "your-private-key-id",
    "private_key": "your-private-key",
    "client_email": "your-client-email",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "your-cert-url"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 