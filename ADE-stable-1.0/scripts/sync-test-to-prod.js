#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const chalk = require('chalk');
const ora = require('ora');

// Configuration
const config = {
    sourceEnv: 'testing',
    targetEnv: 'production',
    projectRoot: path.resolve(__dirname, '..'),
    environmentsDir: path.resolve(__dirname, '..', 'environments'),
    requiredFiles: [
        'docker-compose.yml',
        '.env',
        'package.json',
        'requirements.txt'
    ],
    sensitiveKeys: [
        'API_KEY',
        'SECRET_KEY',
        'DATABASE_PASSWORD',
        'AWS_ACCESS_KEY',
        'AWS_SECRET_KEY'
    ],
    productionChecks: {
        minNodeVersion: '14.0.0',
        requiredEnvVars: [
            'NODE_ENV=production',
            'ENABLE_LOGGING=true',
            'ENABLE_MONITORING=true'
        ]
    }
};

// Utility functions
const log = {
    info: (msg) => console.log(chalk.blue(`[INFO] ${msg}`)),
    success: (msg) => console.log(chalk.green(`[SUCCESS] ${msg}`)),
    error: (msg) => console.log(chalk.red(`[ERROR] ${msg}`)),
    warning: (msg) => console.log(chalk.yellow(`[WARNING] ${msg}`))
};

function validateEnvironment(env) {
    const envPath = path.join(config.environmentsDir, env);
    const spinner = ora(`Validating ${env} environment`).start();

    try {
        // Check if environment directory exists
        if (!fs.existsSync(envPath)) {
            throw new Error(`Environment directory ${env} does not exist`);
        }

        // Validate required files
        for (const file of config.requiredFiles) {
            const filePath = path.join(envPath, file);
            if (!fs.existsSync(filePath)) {
                throw new Error(`Required file ${file} is missing in ${env} environment`);
            }
        }

        // Validate Docker Compose configuration
        execSync(`docker-compose -f ${path.join(envPath, 'docker-compose.yml')} config`, {
            stdio: 'pipe'
        });

        // Additional production-specific validations
        if (env === 'production') {
            validateProductionEnvironment(envPath);
        }

        spinner.succeed(`Validated ${env} environment`);
        return true;
    } catch (error) {
        spinner.fail(`Failed to validate ${env} environment`);
        log.error(error.message);
        return false;
    }
}

function validateProductionEnvironment(envPath) {
    // Check Node.js version
    const nodeVersion = execSync('node --version').toString().trim();
    if (nodeVersion < config.productionChecks.minNodeVersion) {
        throw new Error(`Node.js version ${nodeVersion} is below minimum required version ${config.productionChecks.minNodeVersion}`);
    }

    // Validate required environment variables
    const envContent = fs.readFileSync(path.join(envPath, '.env'), 'utf8');
    for (const requiredVar of config.productionChecks.requiredEnvVars) {
        if (!envContent.includes(requiredVar)) {
            throw new Error(`Missing required environment variable: ${requiredVar}`);
        }
    }

    // Validate security settings
    const dockerCompose = fs.readFileSync(path.join(envPath, 'docker-compose.yml'), 'utf8');
    if (!dockerCompose.includes('security_opt:')) {
        throw new Error('Missing security options in Docker Compose configuration');
    }
}

function backupEnvironment(env) {
    const envPath = path.join(config.environmentsDir, env);
    const backupDir = path.join(config.environmentsDir, 'backups');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = path.join(backupDir, `${env}_${timestamp}`);
    const spinner = ora(`Creating backup of ${env} environment`).start();

    try {
        // Create backup directory if it doesn't exist
        if (!fs.existsSync(backupDir)) {
            fs.mkdirSync(backupDir, { recursive: true });
        }

        // Copy environment files
        fs.cpSync(envPath, backupPath, { recursive: true });
        spinner.succeed(`Created backup at ${backupPath}`);
        return true;
    } catch (error) {
        spinner.fail(`Failed to create backup of ${env} environment`);
        log.error(error.message);
        return false;
    }
}

function syncFiles(sourceEnv, targetEnv) {
    const sourcePath = path.join(config.environmentsDir, sourceEnv);
    const targetPath = path.join(config.environmentsDir, targetEnv);
    const spinner = ora(`Synchronizing files from ${sourceEnv} to ${targetEnv}`).start();

    try {
        // Sync docker-compose.yml with production-specific modifications
        const dockerCompose = fs.readFileSync(path.join(sourcePath, 'docker-compose.yml'), 'utf8');
        const modifiedDockerCompose = modifyDockerComposeForProduction(dockerCompose);
        fs.writeFileSync(path.join(targetPath, 'docker-compose.yml'), modifiedDockerCompose);

        // Sync and merge .env files
        const sourceEnv = fs.readFileSync(path.join(sourcePath, '.env'), 'utf8');
        const targetEnv = fs.readFileSync(path.join(targetPath, '.env'), 'utf8');
        
        const mergedEnv = mergeEnvFiles(sourceEnv, targetEnv);
        fs.writeFileSync(path.join(targetPath, '.env'), mergedEnv);

        // Sync other configuration files
        const filesToSync = ['package.json', 'requirements.txt'];
        for (const file of filesToSync) {
            fs.copyFileSync(
                path.join(sourcePath, file),
                path.join(targetPath, file)
            );
        }

        spinner.succeed(`Synchronized files from ${sourceEnv} to ${targetEnv}`);
        return true;
    } catch (error) {
        spinner.fail(`Failed to synchronize files from ${sourceEnv} to ${targetEnv}`);
        log.error(error.message);
        return false;
    }
}

function modifyDockerComposeForProduction(dockerCompose) {
    // Add production-specific configurations
    let modified = dockerCompose;

    // Add health checks if not present
    if (!modified.includes('healthcheck:')) {
        modified = modified.replace(
            /services:/,
            `services:\n  healthcheck:\n    test: ["CMD", "curl", "-f", "http://localhost:3000/health"]\n    interval: 30s\n    timeout: 10s\n    retries: 3`
        );
    }

    // Add resource limits if not present
    if (!modified.includes('deploy:')) {
        modified = modified.replace(
            /services:/,
            `services:\n  deploy:\n    resources:\n      limits:\n        cpus: '1'\n        memory: 1G\n      reservations:\n        cpus: '0.5'\n        memory: 512M`
        );
    }

    return modified;
}

function mergeEnvFiles(sourceEnv, targetEnv) {
    const sourceLines = sourceEnv.split('\n');
    const targetLines = targetEnv.split('\n');
    const mergedLines = [];
    const processedKeys = new Set();

    // Process target environment first to preserve sensitive values
    for (const line of targetLines) {
        if (line.trim() && !line.startsWith('#')) {
            const [key] = line.split('=');
            if (key) {
                processedKeys.add(key);
                mergedLines.push(line);
            }
        }
    }

    // Add source environment variables that don't exist in target
    for (const line of sourceLines) {
        if (line.trim() && !line.startsWith('#')) {
            const [key] = line.split('=');
            if (key && !processedKeys.has(key)) {
                mergedLines.push(line);
            }
        }
    }

    return mergedLines.join('\n');
}

function verifySync(sourceEnv, targetEnv) {
    const spinner = ora(`Verifying synchronization from ${sourceEnv} to ${targetEnv}`).start();

    try {
        // Validate target environment after sync
        if (!validateEnvironment(targetEnv)) {
            throw new Error(`Target environment ${targetEnv} validation failed after sync`);
        }

        // Run Docker Compose validation
        const targetPath = path.join(config.environmentsDir, targetEnv);
        execSync(`docker-compose -f ${path.join(targetPath, 'docker-compose.yml')} config`, {
            stdio: 'pipe'
        });

        // Additional production-specific verifications
        if (targetEnv === 'production') {
            verifyProductionDeployment(targetPath);
        }

        spinner.succeed(`Verified synchronization from ${sourceEnv} to ${targetEnv}`);
        return true;
    } catch (error) {
        spinner.fail(`Failed to verify synchronization from ${sourceEnv} to ${targetEnv}`);
        log.error(error.message);
        return false;
    }
}

function verifyProductionDeployment(envPath) {
    // Verify SSL certificates
    const sslPath = path.join(envPath, 'ssl');
    if (!fs.existsSync(sslPath)) {
        throw new Error('SSL certificates directory is missing');
    }

    // Verify monitoring setup
    const dockerCompose = fs.readFileSync(path.join(envPath, 'docker-compose.yml'), 'utf8');
    if (!dockerCompose.includes('prometheus:') || !dockerCompose.includes('grafana:')) {
        throw new Error('Monitoring services are not properly configured');
    }

    // Verify backup configuration
    if (!dockerCompose.includes('backup:')) {
        throw new Error('Backup service is not configured');
    }
}

async function main() {
    log.info(`Starting synchronization from ${config.sourceEnv} to ${config.targetEnv}`);

    // Validate source environment
    if (!validateEnvironment(config.sourceEnv)) {
        log.error('Source environment validation failed');
        process.exit(1);
    }

    // Create backup of target environment
    if (!backupEnvironment(config.targetEnv)) {
        log.error('Failed to create backup of target environment');
        process.exit(1);
    }

    // Synchronize files
    if (!syncFiles(config.sourceEnv, config.targetEnv)) {
        log.error('Failed to synchronize files');
        process.exit(1);
    }

    // Verify synchronization
    if (!verifySync(config.sourceEnv, config.targetEnv)) {
        log.error('Synchronization verification failed');
        process.exit(1);
    }

    log.success(`Successfully synchronized ${config.sourceEnv} to ${config.targetEnv}`);
}

// Run the script
main().catch(error => {
    log.error(`Synchronization failed: ${error.message}`);
    process.exit(1);
}); 