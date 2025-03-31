# Setup Ollama models
$models = @(
    "codellama:13b",
    "deepseek-coder:6.7b",
    "wizardcoder-python:7b",
    "wizardcoder-js:7b",
    "codellama-rust:7b",
    "sqlcoder:7b",
    "neural-chat:7b"
)

Write-Host "Setting up Ollama models..."
foreach ($model in $models) {
    Write-Host "Pulling model: $model"
    ollama pull $model
}

Write-Host "All models have been pulled successfully!"
