const fs = require('fs');
const path = require('path');

// Helper functions
const isDockerCommand = (command) => {
  const dockerCommands = ['docker build', 'docker-compose build', 'docker-compose up'];
  return dockerCommands.some(cmd => command.toLowerCase().includes(cmd));
};

const getCurrentEnvironment = () => {
  try {
    const envFile = fs.readFileSync('.env', 'utf8');
    const envMatch = envFile.match(/NODE_ENV=(\w+)/);
    return envMatch ? envMatch[1] : 'development';
  } catch (error) {
    return 'development';
  }
};

// Workflow rules
const workflowRules = {
  // Enforce development environment
  'enforce-dev-environment': {
    when: async ({ command, file }) => {
      return isDockerCommand(command) || file?.endsWith('docker-compose.yml');
    },
    then: async (context) => {
      const currentEnv = getCurrentEnvironment();
      if (currentEnv !== 'development') {
        return {
          type: 'warning',
          message: 'You are not in the development environment. Please switch before proceeding.',
        };
      }
    },
  },

  // Environment synchronization
  'sync-environment': {
    when: async ({ command }) => isDockerCommand(command),
    then: async () => {
      await syncEnvironment();
    },
  },

  // Docker build validation
  'validate-docker-build': {
    when: async ({ command }) => command.includes('docker build'),
    then: async () => {
      const validationResult = await validateDockerSetup();
      if (!validationResult.success) {
        return {
          type: 'error',
          message: `Docker build validation failed: ${validationResult.message}`,
        };
      }
    },
  },
};

// Helper functions for rules
async function syncEnvironment() {
  // Implement environment synchronization logic
  const envFiles = {
    development: '.env.development',
    production: '.env.production',
  };

  const currentEnv = getCurrentEnvironment();
  const targetEnvFile = envFiles[currentEnv];

  if (!targetEnvFile || !fs.existsSync(targetEnvFile)) {
    throw new Error(`Environment file ${targetEnvFile} not found`);
  }

  // Copy environment file
  fs.copyFileSync(targetEnvFile, '.env');
}

async function validateDockerSetup() {
  const requiredFiles = ['Dockerfile', 'docker-compose.yml'];
  const missingFiles = requiredFiles.filter(file => !fs.existsSync(file));

  if (missingFiles.length > 0) {
    return {
      success: false,
      message: `Missing required files: ${missingFiles.join(', ')}`,
    };
  }

  return { success: true };
}

module.exports = workflowRules; 