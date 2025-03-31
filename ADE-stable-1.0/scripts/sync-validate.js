#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const chalk = require('chalk');
const ora = require('ora');

// Configuration
const config = {
    projectRoot: path.resolve(__dirname, '..'),
    environmentsDir: path.resolve(__dirname, '..', 'environments'),
    environments: ['development', 'testing', 'production'],
    requiredFiles: [
        'docker-compose.yml',
        '.env',
        'package.json',
        'requirements.txt'
    ],
    validationRules: {
        dockerCompose: {
            requiredServices: ['app', 'database', 'redis'],
            requiredNetworks: ['app-network'],
            requiredVolumes: ['app-data']
        },
        env: {
            requiredVars: [
                'NODE_ENV',
                'DATABASE_URL',
                'REDIS_URL',
                'API_KEY'
            ]
        }
    }
};

// Utility functions
const log = {
    info: (msg) => console.log(chalk.blue(`[INFO] ${msg}`)),
    success: (msg) => console.log(chalk.green(`[SUCCESS] ${msg}`)),
    error: (msg) => console.log(chalk.red(`[ERROR] ${msg}`)),
    warning: (msg) => console.log(chalk.yellow(`[WARNING] ${msg}`))
};

function validateDockerCompose(envPath) {
    const dockerComposePath = path.join(envPath, 'docker-compose.yml');
    const dockerCompose = fs.readFileSync(dockerComposePath, 'utf8');
    const errors = [];

    // Check required services
    for (const service of config.validationRules.dockerCompose.requiredServices) {
        if (!dockerCompose.includes(`${service}:`)) {
            errors.push(`Missing required service: ${service}`);
        }
    }

    // Check required networks
    for (const network of config.validationRules.dockerCompose.requiredNetworks) {
        if (!dockerCompose.includes(`${network}:`)) {
            errors.push(`Missing required network: ${network}`);
        }
    }

    // Check required volumes
    for (const volume of config.validationRules.dockerCompose.requiredVolumes) {
        if (!dockerCompose.includes(`${volume}:`)) {
            errors.push(`Missing required volume: ${volume}`);
        }
    }

    // Validate Docker Compose syntax
    try {
        execSync(`docker-compose -f ${dockerComposePath} config`, { stdio: 'pipe' });
    } catch (error) {
        errors.push(`Invalid Docker Compose syntax: ${error.message}`);
    }

    return errors;
}

function validateEnvFile(envPath) {
    const envPath = path.join(envPath, '.env');
    const envContent = fs.readFileSync(envPath, 'utf8');
    const errors = [];

    // Check required environment variables
    for (const varName of config.validationRules.env.requiredVars) {
        if (!envContent.includes(`${varName}=`)) {
            errors.push(`Missing required environment variable: ${varName}`);
        }
    }

    // Check for empty values
    const lines = envContent.split('\n');
    for (const line of lines) {
        if (line.trim() && !line.startsWith('#')) {
            const [key, value] = line.split('=');
            if (key && (!value || value.trim() === '')) {
                errors.push(`Empty value for environment variable: ${key}`);
            }
        }
    }

    return errors;
}

function validatePackageJson(envPath) {
    const packageJsonPath = path.join(envPath, 'package.json');
    const errors = [];

    try {
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

        // Check required dependencies
        const requiredDeps = ['express', 'dotenv', 'docker-compose'];
        for (const dep of requiredDeps) {
            if (!packageJson.dependencies[dep]) {
                errors.push(`Missing required dependency: ${dep}`);
            }
        }

        // Check Node.js version
        if (packageJson.engines && packageJson.engines.node) {
            const nodeVersion = execSync('node --version').toString().trim();
            if (nodeVersion < packageJson.engines.node) {
                errors.push(`Node.js version ${nodeVersion} is below required version ${packageJson.engines.node}`);
            }
        }
    } catch (error) {
        errors.push(`Invalid package.json: ${error.message}`);
    }

    return errors;
}

function validateRequirements(envPath) {
    const requirementsPath = path.join(envPath, 'requirements.txt');
    const errors = [];

    try {
        const requirements = fs.readFileSync(requirementsPath, 'utf8');

        // Check required Python packages
        const requiredPkgs = ['flask', 'python-dotenv', 'requests'];
        for (const pkg of requiredPkgs) {
            if (!requirements.includes(pkg)) {
                errors.push(`Missing required Python package: ${pkg}`);
            }
        }
    } catch (error) {
        errors.push(`Invalid requirements.txt: ${error.message}`);
    }

    return errors;
}

function validateEnvironment(env) {
    const envPath = path.join(config.environmentsDir, env);
    const spinner = ora(`Validating ${env} environment`).start();
    const errors = [];

    try {
        // Check if environment directory exists
        if (!fs.existsSync(envPath)) {
            throw new Error(`Environment directory ${env} does not exist`);
        }

        // Validate required files
        for (const file of config.requiredFiles) {
            const filePath = path.join(envPath, file);
            if (!fs.existsSync(filePath)) {
                errors.push(`Missing required file: ${file}`);
            }
        }

        // Validate Docker Compose configuration
        const dockerComposeErrors = validateDockerCompose(envPath);
        errors.push(...dockerComposeErrors);

        // Validate environment variables
        const envErrors = validateEnvFile(envPath);
        errors.push(...envErrors);

        // Validate package.json
        const packageJsonErrors = validatePackageJson(envPath);
        errors.push(...packageJsonErrors);

        // Validate requirements.txt
        const requirementsErrors = validateRequirements(envPath);
        errors.push(...requirementsErrors);

        if (errors.length === 0) {
            spinner.succeed(`Validated ${env} environment`);
            return true;
        } else {
            spinner.fail(`Validation failed for ${env} environment`);
            errors.forEach(error => log.error(error));
            return false;
        }
    } catch (error) {
        spinner.fail(`Failed to validate ${env} environment`);
        log.error(error.message);
        return false;
    }
}

function validateEnvironmentConsistency() {
    const results = {
        development: validateEnvironment('development'),
        testing: validateEnvironment('testing'),
        production: validateEnvironment('production')
    };

    // Check environment consistency
    const allValid = Object.values(results).every(result => result);
    if (allValid) {
        log.success('All environments are valid and consistent');
        return true;
    } else {
        log.error('Environment validation failed');
        return false;
    }
}

async function main() {
    log.info('Starting environment validation');
    
    const isValid = validateEnvironmentConsistency();
    
    if (!isValid) {
        process.exit(1);
    }
}

// Run the script
main().catch(error => {
    log.error(`Validation failed: ${error.message}`);
    process.exit(1);
}); 