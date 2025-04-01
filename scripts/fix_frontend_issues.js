/**
 * Frontend Issues Fix Script
 * 
 * This script addresses common frontend issues in the ADE platform:
 * 1. Installs missing npm dependencies
 * 2. Updates TypeScript configuration if needed
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const frontendDir = path.join(__dirname, '..', 'frontend');

// Helper function to run commands
function runCommand(command) {
  console.log(`Running: ${command}`);
  try {
    const output = execSync(command, { 
      cwd: frontendDir,
      stdio: 'inherit'
    });
    return true;
  } catch (error) {
    console.error(`Error running command: ${command}`);
    console.error(error.message);
    return false;
  }
}

// Install missing dependencies
function installMissingDependencies() {
  console.log('\n=== Installing Missing Dependencies ===\n');
  
  const dependencies = [
    'react-syntax-highlighter',
    'react-markdown', 
    '@types/react-syntax-highlighter',
    'axios'
  ];
  
  dependencies.forEach(dep => {
    console.log(`Checking/installing ${dep}...`);
    runCommand(`npm list ${dep} || npm install ${dep} --save`);
  });
  
  // Some packages might need dev dependencies
  const devDependencies = [
    'typescript',
    '@types/node',
    '@types/react',
    '@types/react-dom'
  ];
  
  devDependencies.forEach(dep => {
    console.log(`Checking/installing ${dep} as dev dependency...`);
    runCommand(`npm list ${dep} || npm install ${dep} --save-dev`);
  });
}

// Fix TypeScript configuration
function fixTypeScriptConfig() {
  console.log('\n=== Fixing TypeScript Configuration ===\n');
  
  const tsconfigPath = path.join(frontendDir, 'tsconfig.json');
  
  try {
    let tsconfig = JSON.parse(fs.readFileSync(tsconfigPath, 'utf8'));
    
    // Make sure we have all the necessary compiler options
    tsconfig.compilerOptions = {
      ...tsconfig.compilerOptions,
      "skipLibCheck": true,
      "esModuleInterop": true,
      "allowSyntheticDefaultImports": true,
      "forceConsistentCasingInFileNames": true,
      "noImplicitAny": false,
      "strictNullChecks": false,
      "resolveJsonModule": true
    };
    
    // Ensure we have all the necessary paths in includes
    if (!tsconfig.include) {
      tsconfig.include = ["src/**/*"];
    }
    
    // Write back the updated config
    fs.writeFileSync(tsconfigPath, JSON.stringify(tsconfig, null, 2));
    console.log(`Updated TypeScript configuration in ${tsconfigPath}`);
    
  } catch (error) {
    console.error(`Error updating TypeScript config: ${error.message}`);
  }
}

// Main function
function main() {
  console.log('\n============================================');
  console.log('  ADE Frontend Issues Fix Script');
  console.log('============================================\n');
  
  console.log(`Working in frontend directory: ${frontendDir}\n`);
  
  installMissingDependencies();
  fixTypeScriptConfig();
  
  console.log('\n=== Checking for TypeScript Errors ===\n');
  runCommand('npx tsc --noEmit');
  
  console.log('\n============================================');
  console.log('  Fix Process Complete');
  console.log('============================================\n');
  
  console.log('To start the frontend development server:');
  console.log('  cd frontend');
  console.log('  npm start');
  console.log('\n');
}

// Run the main function
main();
