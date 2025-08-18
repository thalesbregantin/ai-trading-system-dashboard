# Script para habilitar Long Path Support no Windows
# Execute como Administrador

Write-Host "🔧 Habilitando Long Path Support..." -ForegroundColor Yellow

try {
    # Habilita Long Path Support
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -Type DWord
    
    Write-Host "✅ Long Path Support habilitado com sucesso!" -ForegroundColor Green
    Write-Host "🔄 Reinicie o computador para aplicar as mudanças" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ Erro ao habilitar Long Path Support" -ForegroundColor Red
    Write-Host "💡 Execute este script como Administrador" -ForegroundColor Yellow
    Write-Host "Erro: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📋 Para executar como Administrador:" -ForegroundColor Cyan
Write-Host "1. Clique com botão direito no PowerShell" -ForegroundColor White
Write-Host "2. Selecione 'Executar como administrador'" -ForegroundColor White
Write-Host "3. Execute: .\enable_long_path.ps1" -ForegroundColor White
