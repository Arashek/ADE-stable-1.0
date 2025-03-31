# PowerShell script to set up open-source LLMs using Ollama

Write-Host "🚀 Setting up open-source LLMs..." -ForegroundColor Cyan

# Function to check if Ollama is running
function Test-OllamaRunning {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -Method Get
        return $true
    } catch {
        return $false
    }
}

# Function to pull a model
function Pull-Model {
    param (
        [string]$modelName
    )
    Write-Host "📥 Pulling model: $modelName" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/pull" -Method Post -Body @{
            name = $modelName
        } | ConvertTo-Json
        Write-Host "✅ Successfully pulled $modelName" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to pull $modelName : $_" -ForegroundColor Red
    }
}

# Wait for Ollama to be ready
Write-Host "⏳ Waiting for Ollama to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
while (-not (Test-OllamaRunning) -and $attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    $attempt++
    Write-Host "Attempt $attempt of $maxAttempts..." -ForegroundColor Yellow
}

if (-not (Test-OllamaRunning)) {
    Write-Host "❌ Ollama is not running. Please start the Docker containers first." -ForegroundColor Red
    exit 1
}

# List of models to pull
$models = @(
    "llama2",
    "mistral",
    "codellama",
    "neural-chat",
    "starling-lm",
    "phi",
    "nous-hermes",
    "dolphin-phi",
    "openchat",
    "deepseek-coder"
)

# Pull each model
foreach ($model in $models) {
    Pull-Model -modelName $model
}

Write-Host "✨ LLM setup complete!" -ForegroundColor Green 