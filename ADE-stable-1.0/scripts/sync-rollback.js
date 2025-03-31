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
    backupDir: path.resolve(__dirname, '..', 'environments', 'backups')
};

// Utility functions
const log = {
    info: (msg) => console.log(chalk.blue(`[INFO] ${msg}`)),
    success: (msg) => console.log(chalk.green(`[SUCCESS] ${msg}`)),
    error: (msg) => console.log(chalk.red(`[ERROR] ${msg}`)),
    warning: (msg) => console.log(chalk.yellow(`[WARNING] ${msg}`))
};

function listBackups(env) {
    const backups = fs.readdirSync(config.backupDir)
        .filter(file => file.startsWith(`${env}_`))
        .map(file => {
            const metadataPath = path.join(config.backupDir, file, 'backup-metadata.json');
            const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
            return {
                name: file,
                timestamp: metadata.timestamp,
                version: metadata.version
            };
        })
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    return backups;
}

function selectBackup(env) {
    const backups = listBackups(env);
    
    if (backups.length === 0) {
        throw new Error(`No backups found for ${env} environment`);
    }

    // If running in non-interactive mode, use the latest backup
    if (process.env.NON_INTERACTIVE) {
        return backups[0];
    }

    // Interactive mode
    console.log('\nAvailable backups:');
    backups.forEach((backup, index) => {
        console.log(`${index + 1}. ${backup.name} (${backup.timestamp}) - Version: ${backup.version}`);
    });

    const readline = require('readline').createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve, reject) => {
        readline.question('\nSelect backup number (or press Enter for latest): ', (answer) => {
            readline.close();
            
            if (!answer) {
                resolve(backups[0]);
                return;
            }

            const index = parseInt(answer) - 1;
            if (isNaN(index) || index < 0 || index >= backups.length) {
                reject(new Error('Invalid backup selection'));
                return;
            }

            resolve(backups[index]);
        });
    });
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

function performRollback(env, backup) {
    const envPath = path.join(config.environmentsDir, env);
    const backupPath = path.join(config.backupDir, backup.name);
    const spinner = ora(`Rolling back ${env} environment to ${backup.name}`).start();

    try {
        // Stop running containers
        const dockerComposePath = path.join(envPath, 'docker-compose.yml');
        if (fs.existsSync(dockerComposePath)) {
            try {
                execSync(`docker-compose -f ${dockerComposePath} down`, { stdio: 'pipe' });
            } catch (error) {
                log.warning(`No running containers found in ${env} environment`);
            }
        }

        // Remove current environment files
        fs.rmSync(envPath, { recursive: true, force: true });

        // Restore from backup
        fs.cpSync(backupPath, envPath, { recursive: true });

        // Start services
        execSync(`docker-compose -f ${path.join(envPath, 'docker-compose.yml')} up -d`, {
            stdio: 'pipe'
        });

        spinner.succeed(`Successfully rolled back ${env} environment to ${backup.name}`);
        return true;
    } catch (error) {
        spinner.fail(`Failed to roll back ${env} environment`);
        log.error(error.message);
        return false;
    }
}

function verifyRollback(env) {
    const spinner = ora(`Verifying ${env} environment after rollback`).start();

    try {
        const envPath = path.join(config.environmentsDir, env);

        // Verify required files
        const requiredFiles = ['docker-compose.yml', '.env', 'package.json', 'requirements.txt'];
        for (const file of requiredFiles) {
            if (!fs.existsSync(path.join(envPath, file))) {
                throw new Error(`Missing required file: ${file}`);
            }
        }

        // Verify Docker Compose configuration
        const dockerComposePath = path.join(envPath, 'docker-compose.yml');
        execSync(`docker-compose -f ${dockerComposePath} config`, { stdio: 'pipe' });

        // Check container health
        const containers = execSync('docker ps --format "{{.Names}}"', { stdio: 'pipe' })
            .toString()
            .split('\n')
            .filter(name => name.includes(env));

        for (const container of containers) {
            const health = execSync(`docker inspect --format "{{.State.Health.Status}}" ${container}`, {
                stdio: 'pipe'
            }).toString().trim();
            
            if (health !== 'healthy') {
                throw new Error(`Container ${container} is not healthy after rollback`);
            }
        }

        spinner.succeed(`Verified ${env} environment after rollback`);
        return true;
    } catch (error) {
        spinner.fail(`Failed to verify ${env} environment after rollback`);
        log.error(error.message);
        return false;
    }
}

async function main() {
    const env = process.argv[2];
    if (!env) {
        log.error('Please specify an environment to roll back');
        process.exit(1);
    }

    if (!['development', 'testing', 'production'].includes(env)) {
        log.error('Invalid environment specified');
        process.exit(1);
    }

    log.info(`Starting rollback process for ${env} environment`);

    try {
        // Select backup to restore
        const backup = await selectBackup(env);

        // Verify backup integrity
        const backupPath = path.join(config.backupDir, backup.name);
        if (!verifyBackup(backupPath)) {
            log.error('Backup verification failed');
            process.exit(1);
        }

        // Perform rollback
        if (!performRollback(env, backup)) {
            log.error('Rollback failed');
            process.exit(1);
        }

        // Verify rollback
        if (!verifyRollback(env)) {
            log.error('Rollback verification failed');
            process.exit(1);
        }

        log.success(`Successfully rolled back ${env} environment to ${backup.name}`);
    } catch (error) {
        log.error(`Rollback failed: ${error.message}`);
        process.exit(1);
    }
}

// Run the script
main().catch(error => {
    log.error(`Rollback process failed: ${error.message}`);
    process.exit(1);
}); 