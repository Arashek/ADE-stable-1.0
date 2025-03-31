const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

// Load ADE core rules
const loadADECoreRules = () => {
  try {
    const rulesPath = path.join(__dirname, 'ade_core_rules.yaml');
    const rulesContent = fs.readFileSync(rulesPath, 'utf8');
    const rules = yaml.load(rulesContent);
    
    // Register core rules with Cursor
    return {
      name: rules.name,
      version: rules.version,
      purpose: rules.purpose,
      agent_system: rules.agent_system,
      development_process: rules.development_process,
      user_collaboration: rules.user_collaboration,
      integration: rules.integration,
      direction: rules.direction,
      priorities: rules.priorities,
      priority_management: rules.priority_management
    };
  } catch (error) {
    console.error('Error loading ADE core rules:', error);
    return null;
  }
};

// Apply core rules to new chat
const applyCoreRulesToChat = (chat) => {
  const rules = loadADECoreRules();
  if (!rules) return;

  // Apply core purpose
  chat.addContext({
    type: 'core_purpose',
    content: rules.purpose
  });

  // Apply development process
  chat.addContext({
    type: 'development_process',
    content: rules.development_process
  });

  // Apply user collaboration rules
  rules.user_collaboration.forEach(collaboration => {
    chat.addContext({
      type: 'user_collaboration',
      name: collaboration.name,
      description: collaboration.description,
      content: collaboration
    });

    // Special handling for design collaboration
    if (collaboration.name === 'design_collaboration') {
      chat.addContext({
        type: 'design_system',
        components: collaboration.components
      });
    }

    // Special handling for autonomous delivery
    if (collaboration.name === 'autonomous_delivery') {
      chat.addContext({
        type: 'autonomous_system',
        features: collaboration.features
      });
    }
  });

  // Set up integration points and triggers
  rules.integration.forEach(integration => {
    // Register integration points
    chat.addContext({
      type: 'integration_point',
      name: integration.name,
      points: integration.points
    });

    // Set up triggers
    if (integration.triggers) {
      integration.triggers.forEach(trigger => {
        chat.on(trigger, () => {
          // Apply relevant rules based on trigger
          const relevantRules = {
            purpose: rules.purpose,
            agent_system: rules.agent_system,
            direction: rules.direction,
            priority_management: rules.priority_management
          };
          chat.addContext({
            type: 'triggered_rules',
            trigger,
            rules: relevantRules
          });
        });
      });
    }
  });

  // Apply development priorities with weights and dependencies
  rules.priorities.forEach(priority => {
    chat.addContext({
      type: 'development_priority',
      name: priority.name,
      description: priority.description,
      order: priority.order.map(item => ({
        name: item,
        weight: priority.order[item].weight,
        dependencies: priority.order[item].dependencies,
        success_criteria: priority.order[item].success_criteria
      }))
    });
  });

  // Apply priority management
  chat.addContext({
    type: 'priority_management',
    content: rules.priority_management
  });

  // Apply agent workflows
  if (rules.development_process) {
    rules.development_process.forEach(process => {
      if (process.name === 'development_workflow' && process.agent_workflows) {
        chat.addContext({
          type: 'agent_workflows',
          workflows: process.agent_workflows
        });
      }
    });
  }
};

// Export rule loader
module.exports = {
  loadADECoreRules,
  applyCoreRulesToChat
}; 