// Main Cursor Rules Configuration
const workflowRules = require('./rules/workflow');
const deploymentRules = require('./rules/deployment');
const dockerRules = require('./rules/docker');

module.exports = {
  // Enable all rule categories
  rules: {
    ...workflowRules,
    ...deploymentRules,
    ...dockerRules,
  },

  // Global configuration
  config: {
    environments: ['development', 'staging', 'production'],
    dockerFiles: {
      development: 'docker-compose.yml',
      production: 'docker-compose.prod.test.yml',
    },
    envFiles: {
      development: '.env.development',
      production: '.env.production',
    },
  },

  // Global hooks
  hooks: {
    beforeDockerBuild: async (context) => {
      await dockerRules.validateDockerConfig(context);
      await workflowRules.syncEnvironment(context);
    },
    beforeDeploy: async (context) => {
      await deploymentRules.validateDeployment(context);
    },
  },
}; 