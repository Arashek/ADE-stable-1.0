import fs from 'fs';
import path from 'path';
import Docker from 'dockerode';

const docker = new Docker();

async function validateDockerSetup() {
  const errors = [];
  
  // Check Docker daemon
  try {
    await docker.ping();
  } catch (error) {
    errors.push('Docker daemon is not running or not accessible');
    return { valid: false, errors };
  }

  // Check required files
  const requiredFiles = [
    'Dockerfile',
    'docker-compose.yml',
    'docker-compose.prod.test.yml',
    '.env',
    '.env.development',
    '.env.production'
  ];

  const missingFiles = requiredFiles.filter(file => !fs.existsSync(file));
  if (missingFiles.length > 0) {
    errors.push(`Missing required files: ${missingFiles.join(', ')}`);
  }

  // Validate Dockerfile
  if (fs.existsSync('Dockerfile')) {
    const dockerfile = fs.readFileSync('Dockerfile', 'utf8');
    const requiredInstructions = ['FROM', 'WORKDIR', 'COPY', 'RUN'];
    const missingInstructions = requiredInstructions.filter(
      instruction => !dockerfile.includes(instruction)
    );

    if (missingInstructions.length > 0) {
      errors.push(`Dockerfile missing required instructions: ${missingInstructions.join(', ')}`);
    }
  }

  // Check environment variables
  const requiredEnvVars = {
    docker: [
      'DOCKER_REGISTRY',
      'DOCKER_IMAGE_NAME',
      'DOCKER_IMAGE_TAG'
    ],
    database: [
      'MONGODB_URI',
      'MONGODB_USER',
      'MONGODB_PASSWORD'
    ],
    api: [
      'API_HOST',
      'API_PORT'
    ],
    security: [
      'JWT_SECRET',
      'JWT_ALGORITHM',
      'JWT_EXPIRATION',
      'ENCRYPTION_KEY'
    ],
    redis: [
      'REDIS_URI',
      'REDIS_PASSWORD'
    ],
    providers: [
      'OPENAI_API_KEY',
      'ANTHROPIC_API_KEY',
      'GOOGLE_API_KEY',
      'DEEPSEEK_API_KEY',
      'GROQ_API_KEY'
    ],
    models: [
      'DEFAULT_OPENAI_MODEL',
      'DEFAULT_ANTHROPIC_MODEL',
      'DEFAULT_GOOGLE_MODEL'
    ],
    github: [
      'GITHUB_CLIENT_ID',
      'GITHUB_CLIENT_SECRET',
      'GITHUB_CALLBACK_URL'
    ]
  };

  // Load environment file
  let envContent = {};
  try {
    const envFile = fs.readFileSync('.env', 'utf8');
    envContent = Object.fromEntries(
      envFile.split('\n')
        .map(line => line.match(/^([^#=]+)=(.*)$/))
        .filter(match => match)
        .map(([_, key, value]) => [key.trim(), value.trim()])
    );
  } catch (error) {
    errors.push('Failed to read .env file');
    return { valid: false, errors };
  }

  // Check each category of variables
  for (const [category, vars] of Object.entries(requiredEnvVars)) {
    const missingVars = vars.filter(
      variable => !envContent[variable]
    );

    if (missingVars.length > 0) {
      errors.push(`Missing ${category} environment variables: ${missingVars.join(', ')}`);
    }
  }

  // Check Docker Compose files
  const composeFiles = ['docker-compose.yml', 'docker-compose.prod.test.yml'];
  for (const file of composeFiles) {
    if (fs.existsSync(file)) {
      try {
        const compose = fs.readFileSync(file, 'utf8');
        if (!compose.includes('version:')) {
          errors.push(`Invalid Docker Compose file: ${file} (missing version)`);
        }
        if (!compose.includes('services:')) {
          errors.push(`Invalid Docker Compose file: ${file} (missing services)`);
        }
      } catch (error) {
        errors.push(`Error reading Docker Compose file: ${file}`);
      }
    }
  }

  // Validate model configuration
  const modelConfig = {
    temperature: parseFloat(envContent.TEMPERATURE),
    maxTokens: parseInt(envContent.MAX_TOKENS),
    topP: parseFloat(envContent.TOP_P)
  };

  if (isNaN(modelConfig.temperature) || modelConfig.temperature < 0 || modelConfig.temperature > 1) {
    errors.push('Invalid TEMPERATURE value (should be between 0 and 1)');
  }

  if (isNaN(modelConfig.maxTokens) || modelConfig.maxTokens <= 0) {
    errors.push('Invalid MAX_TOKENS value (should be a positive integer)');
  }

  if (isNaN(modelConfig.topP) || modelConfig.topP < 0 || modelConfig.topP > 1) {
    errors.push('Invalid TOP_P value (should be between 0 and 1)');
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

async function main() {
  console.log('Validating Docker setup...');
  const result = await validateDockerSetup();

  if (result.valid) {
    console.log('✅ Docker setup is valid');
    process.exit(0);
  } else {
    console.error('❌ Docker setup validation failed:');
    result.errors.forEach(error => console.error(`  - ${error}`));
    process.exit(1);
  }
}

main().catch(error => {
  console.error('Error during validation:', error);
  process.exit(1);
}); 