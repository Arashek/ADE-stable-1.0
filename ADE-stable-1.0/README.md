# ADE Platform Development Environment

This repository contains the development environment setup for the ADE (Advanced Development Environment) platform. The platform includes a frontend interface, backend API, and model training components.

## Prerequisites

- Windows 10 or later
- Docker Desktop for Windows
- PowerShell 5.1 or later
- Git
- Node.js >= 18.0.0
- Python >= 3.11

## Directory Structure

```
ade-platform/
├── frontend/           # Frontend application
├── src/               # Backend API source code
├── model-training/    # Model training components
├── scripts/           # Development and setup scripts
├── docker/            # Docker configuration files
├── data/              # Data directory for training
├── output/            # Output directory for models and metrics
└── .env.txt          # Environment variables (create this file)
```

## Setup Instructions

1. **Configure Docker for D Drive**
   ```powershell
   # Run PowerShell as Administrator
   .\scripts\configure_docker.ps1
   ```

2. **Set Up Environment Variables**
   ```powershell
   .\scripts\setup_env.ps1
   ```
   Create a `.env.txt` file in the root directory with the following variables:
   ```
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   GOOGLE_API_KEY=your_google_key
   DEEPSEEK_API_KEY=your_deepseek_key
   GROQ_API_KEY=your_groq_key
   ```

3. **Start Development Environment**
   ```powershell
   .\scripts\dev_workflow.ps1 start
   ```

## Development Workflow

### Available Commands

```powershell
# Start the development environment
.\scripts\dev_workflow.ps1 start

# Start with force rebuild
.\scripts\dev_workflow.ps1 start -Force

# Stop the development environment
.\scripts\dev_workflow.ps1 stop

# View logs
.\scripts\dev_workflow.ps1 logs [service]

# Restart a service
.\scripts\dev_workflow.ps1 restart [service]

# Show help
.\scripts\dev_workflow.ps1 help
```

### Services

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Model Trainer**: http://localhost:5000
- **Metrics Visualizer**: http://localhost:8080
- **Adminer**: http://localhost:8080
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **PgAdmin**: http://localhost:5050

## Development Features

- Hot reloading for both frontend and backend
- Debugging support for Python services
- Integrated monitoring with Prometheus and Grafana
- Database management with Adminer and PgAdmin
- Model training visualization
- Comprehensive logging

## Model Training

The model trainer is integrated into the development environment and will automatically start when you run the development environment. It includes:

- Real-time training metrics visualization
- Model checkpointing
- Training data management
- Performance monitoring
- Integration with the main API

## Troubleshooting

1. **Docker Issues**
   - Ensure Docker Desktop is running
   - Check Docker service status: `Get-Service docker`
   - Verify Docker configuration: `docker info`

2. **Environment Variables**
   - Run `.\scripts\setup_env.ps1` to verify environment variables
   - Check `.env.txt` file format and content

3. **Service Issues**
   - View service logs: `.\scripts\dev_workflow.ps1 logs [service]`
   - Restart service: `.\scripts\dev_workflow.ps1 restart [service]`
   - Force rebuild: `.\scripts\dev_workflow.ps1 start -Force`

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests and ensure all services work
4. Submit a pull request

## License

This project is proprietary and confidential. All rights reserved. 