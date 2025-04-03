# Getting Started with ADE Cloud Deployment

This guide will help you quickly get started with deploying the ADE Platform to the cloud (cloudev.ai).

## Prerequisites

- Docker Desktop installed and running
- Git (to clone the repository if needed)
- PowerShell (Windows) or Bash (Linux/macOS)
- API keys for required AI services (OpenAI, Anthropic, etc.)

## Quick Start

### 1. Clone the Repository (if not already done)

```bash
git clone https://github.com/yourusername/ADE-stable-1.0.git
cd ADE-stable-1.0
```

### 2. Run the Pre-Deployment Check

This will verify if your system is ready for deployment.

**Windows:**
```powershell
.\deployment\pre_deployment_check.ps1
```

**Linux/macOS:**
```bash
chmod +x deployment/deploy.sh
./deployment/pre_deployment_check.sh
```

### 3. Create Environment Variables File

Create a `.env.cloud` file from the template:

**Windows:**
```powershell
Copy-Item .env.cloud.template .env.cloud
notepad .env.cloud  # Edit with your settings
```

**Linux/macOS:**
```bash
cp .env.cloud.template .env.cloud
nano .env.cloud  # Edit with your settings
```

### 4. Run the Deployment Script

**Windows:**
```powershell
.\deployment\deploy.ps1
```

**Linux/macOS:**
```bash
./deployment/deploy.sh
```

## Troubleshooting

### Frontend Build Issues

If the frontend build fails, try running the frontend error fixing script:

```powershell
.\scripts\fix_frontend_errors.ps1
```

### Container Issues

If containers fail to start properly, check the logs:

```bash
docker-compose -f docker-compose.cloud.yml logs
```

### Network Issues

If you're having issues with service connectivity:

1. Verify that all services are running:
   ```bash
   docker ps
   ```

2. Check that the services can reach each other:
   ```bash
   docker-compose -f docker-compose.cloud.yml exec backend ping frontend
   ```

## Next Steps

After successful deployment:

1. **Access the Platform**: Visit your deployment URL (e.g., https://cloudev.ai)
2. **Run Tests**: Execute the integration tests to verify all functionality
   ```powershell
   .\tests\run_integration_tests.ps1
   ```
3. **Monitor Performance**: Set up monitoring for your services

## Getting Help

If you encounter any issues not covered in this guide:

1. Check the detailed deployment documentation in `deployment/CLOUD_DEPLOYMENT.md`
2. Review the logs for specific error messages
3. Contact the ADE Platform development team

Happy deploying!
