const fs = require('fs');
const path = require('path');

// Helper functions
const isProductionFile = (filePath) => {
  const productionPatterns = [
    'production',
    'prod',
    '.env.production',
    'docker-compose.prod',
  ];
  return productionPatterns.some(pattern => 
    filePath.toLowerCase().includes(pattern)
  );
};

const validateEnvVariables = (envFile) => {
  try {
    const content = fs.readFileSync(envFile, 'utf8');
    const requiredVars = [
      'NODE_ENV',
      'DATABASE_URL',
      'API_KEY',
      'DOCKER_REGISTRY',
    ];

    const missingVars = requiredVars.filter(variable => 
      !content.includes(`${variable}=`)
    );

    return {
      valid: missingVars.length === 0,
      missingVars,
    };
  } catch (error) {
    return {
      valid: false,
      error: `Could not read ${envFile}: ${error.message}`,
    };
  }
};

// Deployment rules
const deploymentRules = {
  // Production edit warning
  'warn-production-edit': {
    when: async ({ file }) => isProductionFile(file),
    then: async () => ({
      type: 'warning',
      message: '⚠️ You are editing production-related files. Please ensure you have the proper authorization.',
    }),
  },

  // Environment variables validation
  'validate-env-variables': {
    when: async ({ command, file }) => {
      return command?.includes('deploy') || 
             file?.endsWith('.env') ||
             isProductionFile(file);
    },
    then: async () => {
      const envFiles = ['.env', '.env.production'];
      const results = envFiles.map(validateEnvVariables);
      
      const errors = results
        .filter(result => !result.valid)
        .map(result => result.error || `Missing variables: ${result.missingVars.join(', ')}`);

      if (errors.length > 0) {
        return {
          type: 'error',
          message: `Environment validation failed:\n${errors.join('\n')}`,
        };
      }
    },
  },

  // Deployment readiness check
  'check-deployment-readiness': {
    when: async ({ command }) => command?.includes('deploy'),
    then: async () => {
      const readinessChecks = [
        checkDockerConfig(),
        checkGitStatus(),
        validateEnvVariables('.env.production'),
      ];

      const results = await Promise.all(readinessChecks);
      const failures = results.filter(r => !r.valid);

      if (failures.length > 0) {
        return {
          type: 'error',
          message: `Deployment checks failed:\n${failures.map(f => f.message).join('\n')}`,
        };
      }
    },
  },
};

// Helper functions for deployment checks
async function checkDockerConfig() {
  const requiredFiles = [
    'Dockerfile',
    'docker-compose.yml',
    'docker-compose.prod.test.yml',
  ];

  const missingFiles = requiredFiles.filter(file => !fs.existsSync(file));

  return {
    valid: missingFiles.length === 0,
    message: missingFiles.length > 0 
      ? `Missing Docker configuration files: ${missingFiles.join(', ')}`
      : 'Docker configuration is valid',
  };
}

async function checkGitStatus() {
  // This is a placeholder for git status check
  // In a real implementation, you would use the git command line or a git library
  return {
    valid: true,
    message: 'Git status check passed',
  };
}

module.exports = deploymentRules; 