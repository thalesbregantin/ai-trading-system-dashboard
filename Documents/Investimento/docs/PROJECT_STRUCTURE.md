# AI Trading System - Estrutura do Projeto

## 📁 Organização

```
Investimento/
├── 📁 core/                    # Sistema principal (v8.0)
│   ├── genetic_optimizer.py    # Otimizador genético final
│   └── walk_forward_optimizer.py # Walk-Forward principal
├── 📁 archive/                 # Versões antigas (backup)
│   ├── v6_ml/                  # Versão 6 com ML
│   ├── v7_evolution/           # Evolução da versão 7
│   └── v3_v4_v5/               # Versões 3, 4 e 5
├── 📁 scripts/                 # Scripts de execução
│   └── run_optimization.bat    # Executar otimização
├── 📁 logs/                    # Logs de execução
├── 📁 data/                    # Dados de mercado
├── 📁 results/                 # Resultados da otimização
├── 📁 cache/                   # Cache de dados
└── 📁 docs/                    # Documentação
```

## 🚀 Como Executar

### Opção 1: Script Batch (Recomendado)
```bash
scripts/run_optimization.bat
```

### Opção 2: Terminal
```bash
# Ativar ambiente virtual
.venv\Scripts\activate

# Executar otimização
python -c "from core.walk_forward_optimizer import WalkForwardOptimizerV7; optimizer = WalkForwardOptimizerV7(); results = optimizer.run()"
```

## 📊 Versões

### v8.0 (Atual) - Produção
- **Status:** ✅ Estável
- **Características:** 
  - Tratamento de casos extremos
  - Fitness multi-objetivo
  - Sem warnings do NumPy
  - Pronto para produção

### v7.x (Arquivado)
- **v7.1:** Correção de erros XGBoost
- **v7.3:** Consistência de retornos
- **v7.4:** Correção SettingWithCopyWarning
- **v7.5:** Correção DEAP
- **v7.6:** Resiliência a dados desequilibrados
- **v7.7:** Feature engineering avançado
- **v7.9:** Otimização estratégica

### v6.x (Arquivado)
- **v6.0:** Primeira versão com ML
- **Características:** XGBoost básico

## 🔧 Configuração

1. **Ambiente Virtual:** `.venv/`
2. **Dependências:** `requirements.txt`
3. **Variáveis:** `.env` (baseado em `env.example`)

## 📈 Monitoramento

- **Logs:** `logs/genetic_optimizer_v8_production.log`
- **Resultados:** `results/`
- **Cache:** `cache/`

## 🎯 Próximos Passos

1. ✅ Organização do projeto
2. 🔄 Implementar suporte Parquet
3. 📊 Análise de resultados
4. 🚀 Deploy em produção
