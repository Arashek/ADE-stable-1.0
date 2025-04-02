# ADE Platform Cloud Deployment Guide

This guide provides instructions for deploying the ADE Platform to the cloud (cloudev.ai).

## Prerequisites

- Docker and Docker Compose installed on the deployment server
- Access to the ADE Platform repository
- API keys for the required AI services
- GitHub OAuth application credentials (for authentication)

## Deployment Files

The following files are included for cloud deployment:

1. `Dockerfile.backend` - Backend service Dockerfile
2. `Dockerfile.frontend` - Frontend service Dockerfile with Nginx
3. `docker-compose.cloud.yml` - Docker Compose configuration for cloud deployment
4. `deployment/nginx.conf` - Nginx configuration for the frontend
5. `deployment/deploy.sh` - Bash deployment script
6. `deployment/deploy.ps1` - PowerShell deployment script
7. `.env.cloud.template` - Template for environment variables

## Deployment Steps

### 1. Prepare Environment Variables

Create a `.env.cloud` file from the template:

```bash
cp .env.cloud.template .env.cloud
```

Edit the file to include your actual API keys, database credentials, and other configuration values.

### 2. Run the Deployment Script

#### For Linux/macOS:

```bash
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

#### For Windows:

```powershell
.\deployment\deploy.ps1
```

### 3. Verify Deployment

After deployment, the services should be accessible at:
- Frontend: https://cloudev.ai
- Backend API: https://cloudev.ai/api

## Container Architecture

The deployment consists of the following containers:

1. **Frontend** - Nginx server with the compiled React application
2. **Backend** - Python FastAPI server with agent coordination functionality
3. **MongoDB** - Database for storing application data
4. **Redis** - Cache and message broker
5. **Ollama** - Local LLM server for certain AI tasks

## Scaling Considerations

For high-availability and scalability:

1. **Horizontal Scaling**: The backend service can be scaled horizontally by increasing the number of replica containers.
2. **Database Scaling**: Consider using a managed MongoDB service instead of a container for production.
3. **Redis Cluster**: For higher loads, implement a Redis cluster instead of a single Redis instance.
4. **Load Balancer**: Add a load balancer in front of multiple frontend instances.

## Monitoring

The deployment includes Prometheus and Grafana for monitoring. Access the dashboards at:
- Grafana: https://cloudev.ai/monitoring (credentials in the .env.cloud file)

## Backup Strategy

Implement regular backups of the MongoDB data volume and the Redis data volume:

```bash
docker run --rm -v ade_mongodb_data:/data -v /backup:/backup alpine tar cvf /backup/mongodb_backup.tar /data
docker run --rm -v ade_redis_data:/data -v /backup:/backup alpine tar cvf /backup/redis_backup.tar /data
```

## Security Considerations

1. **API Keys**: Keep API keys secure by using environment variables
2. **Database Credentials**: Use strong passwords for MongoDB and Redis
3. **JWT Secret**: Use a strong, unique JWT secret for authentication
4. **HTTPS**: Ensure HTTPS is properly configured on the hosting platform
5. **Firewall Rules**: Limit access to internal services (MongoDB, Redis)

## Troubleshooting

If you encounter issues with the deployment:

1. Check container logs: `docker-compose -f docker-compose.cloud.yml logs`
2. Verify all containers are running: `docker ps`
3. Check MongoDB and Redis connections
4. Inspect Nginx logs for frontend issues

For additional support, contact the ADE Platform development team.
