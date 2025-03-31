# Cursor Rules System for ADE Platform

This directory contains the Cursor rules system configuration for the ADE platform development workflow with Docker integration.

## Structure

```
.cursor/
├── rules.js              # Main rules configuration
├── rules/
│   ├── workflow.js       # Development workflow rules
│   ├── deployment.js     # Deployment safety rules
│   └── docker.js         # Docker-specific rules
└── scripts/             # Helper scripts for rules
```

## Features

### Workflow Rules
- Enforces development in the correct environment
- Triggers environment synchronization for Docker builds
- Validates Docker setup before builds
- Detects and validates Docker-related commands

### Deployment Rules
- Warns when editing production files
- Validates environment variables
- Checks deployment readiness
- Ensures proper Docker configurations

### Docker Rules
- Detects Docker build commands
- Validates Docker configurations
- Ensures proper environment variables
- Triggers environment synchronization

## Usage

### Docker Commands
```bash
# Development environment
npm run docker:build      # Build development containers
npm run docker:up         # Start development environment
npm run docker:down       # Stop development environment

# Production environment
npm run docker:build:prod # Build production containers
npm run docker:up:prod    # Start production environment
npm run docker:down:prod  # Stop production environment

# Validation and synchronization
npm run docker:validate   # Validate Docker setup
npm run docker:sync-env   # Synchronize environment files
```

### Environment Variables
Required environment variables for Docker operations:
- `DOCKER_REGISTRY`: Docker registry URL
- `DOCKER_IMAGE_NAME`: Name for the Docker image
- `DOCKER_IMAGE_TAG`: Tag for the Docker image

### Extending Rules
1. Create a new rule file in `.cursor/rules/`
2. Define your rules using the standard format:
```javascript
module.exports = {
  'rule-name': {
    when: async (context) => { /* condition */ },
    then: async (context) => { /* action */ }
  }
};
```
3. Import and add your rules in `rules.js`

## Best Practices
1. Always work in the development environment first
2. Use provided npm scripts for Docker operations
3. Keep environment files synchronized
4. Run validation before deployments
5. Follow the warning messages from the rules system

## Troubleshooting
1. **Environment Sync Issues**
   - Check if all required .env files exist
   - Verify file permissions
   - Run `npm run docker:sync-env` manually

2. **Docker Build Failures**
   - Ensure Docker daemon is running
   - Verify Docker configurations with `npm run docker:validate`
   - Check environment variables

3. **Deployment Issues**
   - Verify all checks pass with `npm run docker:validate`
   - Ensure all required environment variables are set
   - Check Docker registry access

## Contributing
1. Follow the existing rule format
2. Add tests for new rules
3. Update documentation
4. Submit a pull request

## License
This rules system is part of the ADE Platform and follows the same licensing terms. 