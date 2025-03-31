# Docker-Integrated Workflow Documentation

This document describes the Docker-based development, testing, and deployment workflow for the ADE Platform.

## Environment Structure

The platform uses three distinct environments, each with its own Docker configuration:

### Development Environment
- Located in `/environments/development/`
- Includes hot-reload capabilities
- Development-specific tools and services
- Exposed ports for direct access
- Development database UI tools

### Testing Environment
- Located in `/environments/testing/`
- Dedicated testing services
- Automated test runners
- Code coverage reporting
- Performance testing suite

### Production Environment
- Located in `/environments/production/`
- High availability configuration
- Load balancing with Nginx
- MongoDB replication
- Redis clustering
- Prometheus/Grafana monitoring

## Quick Start

1. Start the development environment:
   ```bash
   ./scripts/docker_workflow.sh development up
   ```

2. Run tests in the testing environment:
   ```bash
   ./scripts/docker_workflow.sh testing test
   ```

3. Deploy to production:
   ```bash
   ./scripts/docker_workflow.sh production up
   ```

## Workflow Commands

The `docker_workflow.sh` script supports the following commands:

- `up`: Start the environment
- `down`: Stop the environment
- `build`: Rebuild containers
- `test`: Run tests (testing environment only)
- `logs`: View container logs
- `status`: Check container status

## Development Workflow

1. **Local Development**
   - Start development environment: `./scripts/docker_workflow.sh development up`
   - Code changes are automatically detected and reloaded
   - Access services:
     - API: http://localhost:8000
     - MongoDB UI: http://localhost:8080
     - Redis UI: http://localhost:8081

2. **Testing**
   - Run all tests: `./scripts/docker_workflow.sh testing test`
   - View test results in `coverage/` directory
   - Performance test results in `performance_results/`

3. **Production Deployment**
   - Build production images: `./scripts/docker_workflow.sh production build`
   - Deploy: `./scripts/docker_workflow.sh production up`
   - Monitor: Access Grafana dashboard (configured port)

## Environment-Specific Features

### Development
- Hot-reload enabled
- Debug logging
- Development tools:
  - Adminer (MongoDB UI)
  - Redis Commander
  - Direct port access

### Testing
- Automated test suite
- Integration tests
- Performance tests
- Code coverage reporting
- Isolated test databases

### Production
- Multi-container deployment
- Load balancing
- High availability:
  - API service replication
  - Database replication
  - Redis clustering
- Monitoring:
  - Prometheus metrics
  - Grafana dashboards
  - Log aggregation

## Docker Configuration

### Development
```yaml
services:
  dev-api:
    build:
      context: ../..
      dockerfile: environments/development/Dockerfile
    volumes:
      - ../../src:/app/src
    ports:
      - "8000:8000"
```

### Testing
```yaml
services:
  test-api:
    build:
      context: ../..
      dockerfile: environments/testing/Dockerfile
  integration-tests:
    command: ["pytest", "-v", "tests/integration/"]
  performance-tests:
    command: ["locust", "-f", "tests/performance/locustfile.py"]
```

### Production
```yaml
services:
  prod-api:
    build:
      context: ../..
      dockerfile: environments/production/Dockerfile
    deploy:
      replicas: 3
  prod-nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
```

## Best Practices

1. **Environment Variables**
   - Use `.env` files for each environment
   - Never commit sensitive values
   - Use environment-specific prefixes

2. **Resource Management**
   - Set appropriate resource limits
   - Monitor resource usage
   - Scale containers as needed

3. **Security**
   - Use non-root users in containers
   - Implement health checks
   - Regular security updates
   - Proper secret management

4. **Monitoring**
   - Set up alerting
   - Monitor container health
   - Track performance metrics
   - Aggregate logs

## Troubleshooting

1. **Container Issues**
   - Check logs: `./scripts/docker_workflow.sh <env> logs`
   - Verify status: `./scripts/docker_workflow.sh <env> status`
   - Rebuild: `./scripts/docker_workflow.sh <env> build`

2. **Performance Issues**
   - Check resource usage
   - Review Prometheus metrics
   - Analyze performance test results

3. **Development Issues**
   - Verify hot-reload is working
   - Check mounted volumes
   - Review development logs

## Maintenance

1. **Regular Tasks**
   - Update base images
   - Check for dependency updates
   - Review and rotate logs
   - Monitor disk usage

2. **Backup Strategy**
   - Regular database backups
   - Configuration backups
   - Disaster recovery plan

3. **Updates**
   - Rolling updates in production
   - Regular security patches
   - Dependency updates 