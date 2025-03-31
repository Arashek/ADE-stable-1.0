import fs from 'fs';
import path from 'path';

function loadEnvFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const env = {
      _comments: new Map(), // Store comments and their associated keys
      _order: [], // Maintain the order of variables
      _sections: new Map() // Store section comments
    };

    let currentSection = '';
    let lastKey = '';

    content.split('\n').forEach(line => {
      // Store section comments
      if (line.startsWith('# ') && !lastKey) {
        currentSection = line;
        env._sections.set(currentSection, []);
        return;
      }

      // Store inline comments
      const commentMatch = line.match(/^#\s*(.+)$/);
      if (commentMatch) {
        if (lastKey) {
          env._comments.set(lastKey, (env._comments.get(lastKey) || []).concat(line));
        }
        return;
      }

      // Parse environment variables
      const match = line.match(/^([^#=]+)=(.*)$/);
      if (match) {
        const key = match[1].trim();
        const value = match[2].trim();
        env[key] = value;
        env._order.push(key);
        lastKey = key;

        // Associate variable with current section
        if (currentSection) {
          env._sections.get(currentSection).push(key);
        }
      } else {
        lastKey = ''; // Reset lastKey on empty lines
      }
    });
    return env;
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error.message);
    return null;
  }
}

function writeEnvFile(filePath, env) {
  try {
    let content = '';
    
    // Write sections in order
    for (const [section, variables] of env._sections) {
      content += `${section}\n`;
      
      for (const key of variables) {
        // Write any comments associated with the variable
        const comments = env._comments.get(key);
        if (comments) {
          comments.forEach(comment => {
            content += `${comment}\n`;
          });
        }

        if (env[key] !== undefined) {
          content += `${key}=${env[key]}\n`;
        }
      }
      content += '\n';
    }

    // Write any remaining variables that aren't in sections
    const remainingVars = env._order.filter(key => 
      ![...env._sections.values()].flat().includes(key)
    );

    if (remainingVars.length > 0) {
      content += '# Additional Variables\n';
      remainingVars.forEach(key => {
        const comments = env._comments.get(key);
        if (comments) {
          comments.forEach(comment => {
            content += `${comment}\n`;
          });
        }
        content += `${key}=${env[key]}\n`;
      });
    }

    fs.writeFileSync(filePath, content);
    return true;
  } catch (error) {
    console.error(`Error writing ${filePath}:`, error.message);
    return false;
  }
}

function mergeEnvs(source, target) {
  const merged = {
    ...target,
    ...source,
    _comments: new Map([...target._comments, ...source._comments]),
    _order: [...new Set([...target._order, ...source._order])],
    _sections: new Map([...target._sections, ...source._sections])
  };

  // Ensure critical values are properly set
  const criticalVars = {
    NODE_ENV: source.NODE_ENV || target.NODE_ENV,
    ENVIRONMENT: source.ENVIRONMENT || target.ENVIRONMENT,
    DEBUG: source.DEBUG || target.DEBUG,
    LOG_LEVEL: source.LOG_LEVEL || target.LOG_LEVEL,
    
    // Database
    MONGODB_URI: source.MONGODB_URI || target.MONGODB_URI,
    MONGODB_USER: source.MONGODB_USER || target.MONGODB_USER,
    MONGODB_PASSWORD: source.MONGODB_PASSWORD || target.MONGODB_PASSWORD,
    
    // API Keys
    OPENAI_API_KEY: source.OPENAI_API_KEY || target.OPENAI_API_KEY,
    ANTHROPIC_API_KEY: source.ANTHROPIC_API_KEY || target.ANTHROPIC_API_KEY,
    GOOGLE_API_KEY: source.GOOGLE_API_KEY || target.GOOGLE_API_KEY,
    DEEPSEEK_API_KEY: source.DEEPSEEK_API_KEY || target.DEEPSEEK_API_KEY,
    GROQ_API_KEY: source.GROQ_API_KEY || target.GROQ_API_KEY,
    
    // Docker
    DOCKER_REGISTRY: source.DOCKER_REGISTRY || target.DOCKER_REGISTRY,
    DOCKER_IMAGE_NAME: source.DOCKER_IMAGE_NAME || target.DOCKER_IMAGE_NAME,
    DOCKER_IMAGE_TAG: source.DOCKER_IMAGE_TAG || target.DOCKER_IMAGE_TAG,
    
    // Security
    JWT_SECRET: source.JWT_SECRET || target.JWT_SECRET,
    ENCRYPTION_KEY: source.ENCRYPTION_KEY || target.ENCRYPTION_KEY
  };

  return { ...merged, ...criticalVars };
}

async function syncEnvironments() {
  const environments = {
    development: '.env.development',
    production: '.env.production'
  };

  // Determine current environment
  const nodeEnv = process.env.NODE_ENV || 'development';
  const targetEnvFile = environments[nodeEnv];

  if (!targetEnvFile) {
    console.error(`Invalid environment: ${nodeEnv}`);
    return false;
  }

  // Load environment files
  const targetEnv = loadEnvFile(targetEnvFile);
  const existingEnv = loadEnvFile('.env');

  if (!targetEnv || !existingEnv) {
    console.error('Failed to load environment files');
    return false;
  }

  // Create backup of current .env
  const backupFile = `.env.backup.${Date.now()}`;
  try {
    fs.copyFileSync('.env', backupFile);
    console.log(`Created backup: ${backupFile}`);
  } catch (error) {
    console.error('Failed to create backup:', error.message);
    return false;
  }

  // Merge and write new environment
  const mergedEnv = mergeEnvs(targetEnv, existingEnv);
  if (!writeEnvFile('.env', mergedEnv)) {
    // Restore backup if write fails
    try {
      fs.copyFileSync(backupFile, '.env');
      console.log('Restored backup due to write failure');
    } catch (error) {
      console.error('Failed to restore backup:', error.message);
    }
    return false;
  }

  // Validate critical variables
  const criticalCategories = {
    'API Keys': ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY'],
    'Docker': ['DOCKER_REGISTRY', 'DOCKER_IMAGE_NAME', 'DOCKER_IMAGE_TAG'],
    'Database': ['MONGODB_URI', 'MONGODB_USER', 'MONGODB_PASSWORD'],
    'Security': ['JWT_SECRET', 'ENCRYPTION_KEY']
  };

  const missingByCategory = {};
  for (const [category, vars] of Object.entries(criticalCategories)) {
    const missing = vars.filter(v => !mergedEnv[v]);
    if (missing.length > 0) {
      missingByCategory[category] = missing;
    }
  }

  if (Object.keys(missingByCategory).length > 0) {
    console.warn('Warning: Missing critical variables:');
    for (const [category, vars] of Object.entries(missingByCategory)) {
      console.warn(`  ${category}: ${vars.join(', ')}`);
    }
  }

  return true;
}

async function main() {
  console.log('Synchronizing Docker environments...');
  const success = await syncEnvironments();

  if (success) {
    console.log('✅ Environment synchronization complete');
    process.exit(0);
  } else {
    console.error('❌ Environment synchronization failed');
    process.exit(1);
  }
}

main().catch(error => {
  console.error('Error during synchronization:', error);
  process.exit(1);
}); 