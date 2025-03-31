const fs = require('fs');
const path = require('path');

// Helper functions
const parseDockerCommand = (command) => {
  const dockerBuildRegex = /docker(?:\s+compose)?\s+build\s+(?:--no-cache\s+)?([^\s]+)?/;
  const match = command.match(dockerBuildRegex);
  return match ? { service: match[1] || 'default' } : null;
};

const validateDockerfile = (dockerfile) => {
  try {
    const content = fs.readFileSync(dockerfile, 'utf8');
    const requiredInstructions = ['FROM', 'WORKDIR', 'COPY', 'RUN'];
    
    const missingInstructions = requiredInstructions.filter(
      instruction => !content.includes(instruction)
    );

    return {
      valid: missingInstructions.length === 0,
      missingInstructions,
    };
  } catch (error) {
    return {
      valid: false,
      error: `Could not read ${dockerfile}: ${error.message}`,
    };
  }
};

// Docker rules
const dockerRules = {
  // Detect Docker build commands
  'detect-docker-build': {
    when: async ({ command }) => {
      return command?.toLowerCase().includes('docker build') ||
             command?.toLowerCase().includes('docker-compose build');
    },
    then: async ({ command }) => {
      const buildInfo = parseDockerCommand(command);
      if (buildInfo) {
        return {
          type: 'info',
          message: `Detected Docker build for service: ${buildInfo.service}`,
        };
      }
    },
  },

  // Validate Docker configuration
  'validate-docker-config': {
    when: async ({ command, file }) => {
      return (command?.toLowerCase().includes('docker') && 
              command?.toLowerCase().includes('build')) ||
             file?.endsWith('Dockerfile') ||
             file?.endsWith('docker-compose.yml');
    },
    then: async () => {
      const dockerfileResult = validateDockerfile('Dockerfile');
      const composeResult = validateDockerCompose();

      const errors = [];
      
      if (!dockerfileResult.valid) {
        errors.push(
          dockerfileResult.error || 
          `Missing Dockerfile instructions: ${dockerfileResult.missingInstructions.join(', ')}`
        );
      }

      if (!composeResult.valid) {
        errors.push(composeResult.message);
      }

      if (errors.length > 0) {
        return {
          type: 'error',
          message: `Docker configuration validation failed:\n${errors.join('\n')}`,
        };
      }
    },
  },

  // Environment variable validation for Docker
  'validate-docker-env': {
    when: async ({ command }) => {
      return command?.toLowerCase().includes('docker') &&
             (command?.toLowerCase().includes('build') ||
              command?.toLowerCase().includes('up'));
    },
    then: async () => {
      const envResult = validateDockerEnv();
      if (!envResult.valid) {
        return {
          type: 'error',
          message: `Docker environment validation failed: ${envResult.message}`,
        };
      }
    },
  },
};

// Helper functions for Docker validation
function validateDockerCompose() {
  const composeFiles = ['docker-compose.yml', 'docker-compose.prod.test.yml'];
  const missingFiles = composeFiles.filter(file => !fs.existsSync(file));

  if (missingFiles.length > 0) {
    return {
      valid: false,
      message: `Missing Docker Compose files: ${missingFiles.join(', ')}`,
    };
  }

  return { valid: true };
}

function validateDockerEnv() {
  const requiredVars = [
    'DOCKER_REGISTRY',
    'DOCKER_IMAGE_NAME',
    'DOCKER_IMAGE_TAG',
  ];

  const missingVars = requiredVars.filter(
    variable => !process.env[variable]
  );

  return {
    valid: missingVars.length === 0,
    message: missingVars.length > 0
      ? `Missing required Docker environment variables: ${missingVars.join(', ')}`
      : 'Docker environment variables are valid',
  };
}

module.exports = dockerRules; 