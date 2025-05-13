# Format code with Black
Write-Host "Running Black formatter on codebase..." -ForegroundColor Cyan

try {
    black src tests
    Write-Host "✅ Formatting complete!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error running Black: $_" -ForegroundColor Red
    exit 1
}
