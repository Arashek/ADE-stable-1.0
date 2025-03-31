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
    backupDir: path.resolve(__dirname, '..', 'environments', 'backups'),
    maxBackups: 5,
    backupRetentionDays: 7
};

// Utility functions
const log = {
    info: (msg) => console.log(chalk.blue(`[INFO] ${msg}`)),
    success: (msg) => console.log(chalk.green(`[SUCCESS] ${msg}`)),
    error: (msg) => console.log(chalk.red(`[ERROR] ${msg}`)),
    warning: (msg) => console.log(chalk.yellow(`[WARNING] ${msg}`))
};

function createBackup(env) {
    const envPath = path.join(config.environmentsDir, env);
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = path.join(config.backupDir, `${env}_${timestamp}`);
    const spinner = ora(`Creating backup of ${env} environment`).start();

    try {
        // Create backup directory if it doesn't exist
        if (!fs.existsSync(config.backupDir)) {
            fs.mkdirSync(config.backupDir, { recursive: true });
        }

        // Stop running containers if any
        const dockerComposePath = path.join(envPath, 'docker-compose.yml');
        if (fs.existsSync(dockerComposePath)) {
            try {
                execSync(`docker-compose -f ${dockerComposePath} down`, { stdio: 'pipe' });
            } catch (error) {
                log.warning(`No running containers found in ${env} environment`);
            }
        }

        // Copy environment files
        fs.cpSync(envPath, backupPath, { recursive: true });

        // Create backup metadata
        const metadata = {
            environment: env,
            timestamp: new Date().toISOString(),
            version: process.env.npm_package_version || 'unknown',
            files: fs.readdirSync(backupPath)
        };
        fs.writeFileSync(
            path.join(backupPath, 'backup-metadata.json'),
            JSON.stringify(metadata, null, 2)
        );

        spinner.succeed(`Created backup at ${backupPath}`);
        return true;
    } catch (error) {
        spinner.fail(`Failed to create backup of ${env} environment`);
        log.error(error.message);
        return false;
    }
}

function cleanupOldBackups() {
    const spinner = ora('Cleaning up old backups').start();

    try {
        if (!fs.existsSync(config.backupDir)) {
            spinner.succeed('No backup directory found');
            return true;
        }

        const backups = fs.readdirSync(config.backupDir)
            .filter(file => file.startsWith('development_') || file.startsWith('testing_') || file.startsWith('production_'))
            .map(file => ({
                name: file,
                path: path.join(config.backupDir, file),
                timestamp: fs.statSync(path.join(config.backupDir, file)).mtime
            }))
            .sort((a, b) => b.timestamp - a.timestamp);

        // Remove backups exceeding retention period
        const now = new Date();
        for (const backup of backups) {
            const daysOld = (now - backup.timestamp) / (1000 * 60 * 60 * 24);
            if (daysOld > config.backupRetentionDays) {
                fs.rmSync(backup.path, { recursive: true, force: true });
                log.info(`Removed old backup: ${backup.name}`);
            }
        }

        // Keep only the latest N backups per environment
        const envBackups = {
            development: backups.filter(b => b.name.startsWith('development_')),
            testing: backups.filter(b => b.name.startsWith('testing_')),
            production: backups.filter(b => b.name.startsWith('production_'))
        };

        for (const [env, envBackups] of Object.entries(envBackups)) {
            if (envBackups.length > config.maxBackups) {
                const toRemove = envBackups.slice(config.maxBackups);
                for (const backup of toRemove) {
                    fs.rmSync(backup.path, { recursive: true, force: true });
                    log.info(`Removed excess backup: ${backup.name}`);
                }
            }
        }

        spinner.succeed('Cleaned up old backups');
        return true;
    } catch (error) {
        spinner.fail('Failed to clean up old backups');
        log.error(error.message);
        return false;
    }
}

function verifyBackup(backupPath) {
    const spinner = ora('Verifying backup integrity').start();

    try {
        // Check if backup directory exists
        if (!fs.existsSync(backupPath)) {
            throw new Error('Backup directory does not exist');
        }

        // Verify required files
        const requiredFiles = ['docker-compose.yml', '.env', 'package.json', 'requirements.txt'];
        for (const file of requiredFiles) {
            if (!fs.existsSync(path.join(backupPath, file))) {
                throw new Error(`Missing required file: ${file}`);
            }
        }

        // Verify backup metadata
        const metadataPath = path.join(backupPath, 'backup-metadata.json');
        if (!fs.existsSync(metadataPath)) {
            throw new Error('Missing backup metadata');
        }

        const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
        if (!metadata.environment || !metadata.timestamp || !metadata.files) {
            throw new Error('Invalid backup metadata');
        }

        // Verify Docker Compose configuration
        const dockerComposePath = path.join(backupPath, 'docker-compose.yml');
        execSync(`docker-compose -f ${dockerComposePath} config`, { stdio: 'pipe' });

        spinner.succeed('Backup verification successful');
        return true;
    } catch (error) {
        spinner.fail('Backup verification failed');
        log.error(error.message);
        return false;
    }
}

async function main() {
    log.info('Starting backup process');

    // Create backups for all environments
    const environments = ['development', 'testing', 'production'];
    for (const env of environments) {
        if (!createBackup(env)) {
            log.error(`Failed to create backup for ${env} environment`);
            process.exit(1);
        }
    }

    // Clean up old backups
    if (!cleanupOldBackups()) {
        log.error('Failed to clean up old backups');
        process.exit(1);
    }

    // Verify latest backups
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    for (const env of environments) {
        const backupPath = path.join(config.backupDir, `${env}_${timestamp}`);
        if (!verifyBackup(backupPath)) {
            log.error(`Failed to verify backup for ${env} environment`);
            process.exit(1);
        }
    }

    log.success('Backup process completed successfully');
}

// Run the script
main().catch(error => {
    log.error(`Backup process failed: ${error.message}`);
    process.exit(1);
}); 