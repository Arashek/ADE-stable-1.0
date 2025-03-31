# Install dependencies
npm install react react-dom @types/react @types/react-dom
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
npm install reactflow @types/reactflow
npm install recharts @types/recharts
npm install zustand
npm install typescript @types/node
npm install vite @vitejs/plugin-react
npm install eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install eslint-plugin-react-hooks eslint-plugin-react-refresh

# Install dev dependencies
npm install -D @types/node
npm install -D prettier
npm install -D @typescript-eslint/parser
npm install -D @typescript-eslint/eslint-plugin

# Create tsconfig.json if it doesn't exist
if (-not (Test-Path tsconfig.json)) {
    @'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
'@ | Out-File -FilePath tsconfig.json -Encoding UTF8
}

# Create tsconfig.node.json if it doesn't exist
if (-not (Test-Path tsconfig.node.json)) {
    @'
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
'@ | Out-File -FilePath tsconfig.node.json -Encoding UTF8
}

Write-Host "Dependencies installed successfully!" 