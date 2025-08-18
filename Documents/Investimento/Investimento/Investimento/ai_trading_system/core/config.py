"""
Configuração Principal do Sistema AI Trading
Arquivo central para configurar todos os parâmetros
"""

import os
from datetime import datetime
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

# Cria diretórios se não existirem
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Carrega variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    # Fallback: tentativa simples de carregar .env manualmente
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip())
        except Exception:
            pass

class TradingConfig:
    """Configuração centralizada do sistema de trading"""
    
    # ==========================================
    # CONFIGURAÇÕES GERAIS
    # ==========================================
    
    # Modo de operação - MUDANDO PARA USAR DADOS REAIS
    TESTNET_MODE = os.getenv('TESTNET_MODE', 'false').lower() == 'true'
    LIVE_TRADING = os.getenv('LIVE_TRADING', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = LOGS_DIR / f"trading_log_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configurações de checkpoint e logging
    CHECKPOINT_FREQUENCY = 5
    SAVE_BEST_CHECKPOINT = True
    STEP_LOG_SAMPLE = 3
    JSONL_MAX_LINES = 50000
    EARLY_STOP_ENABLED = False
    
    # ==========================================
    # CONFIGURAÇÕES DO AI TRADER
    # ==========================================
    
    # Parâmetros Q-Learning
    AI_EPISODES = 20  # Episódios de treinamento
    AI_WINDOW_SIZE = 10  # Tamanho da janela de estado
    AI_BATCH_SIZE = 32  # Tamanho do batch para treinamento
    AI_LEARNING_RATE = 0.001
    AI_GAMMA = 0.95  # Discount factor
    AI_EPSILON_START = 1.0
    AI_EPSILON_MIN = 0.01
    AI_EPSILON_DECAY = 0.997  # Ajuste de decaimento mais lento
    
    # Arquitetura da rede neural
    AI_HIDDEN_LAYERS = [64, 32, 16]
    AI_DROPOUT_RATE = 0.2
    AI_ACTIVATION = "relu"
    
    # ==========================================
    # CONFIGURAÇÕES SISTEMA HÍBRIDO
    # ==========================================
    
    # Pesos dos sinais
    AI_WEIGHT = 0.6  # Peso do AI Trader
    MOMENTUM_WEIGHT = 0.4  # Peso da estratégia momentum
    
    # Indicadores técnicos
    SMA_SHORT = 20
    SMA_LONG = 50
    RSI_PERIOD = 14
    MOMENTUM_PERIOD = 10
    VOLATILITY_PERIOD = 20
    
    # Thresholds para sinais
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    MOMENTUM_THRESHOLD = 0.0
    
    # ==========================================
    # CONFIGURAÇÕES DE TRADING
    # ==========================================
    
    # Pares de trading
    TRADING_PAIRS = [
        # Top principais (spot alta liquidez)
        'BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT','XRP/USDT','ADA/USDT','DOGE/USDT','TRX/USDT','LINK/USDT','AVAX/USDT',
        'MATIC/USDT','DOT/USDT','LTC/USDT','ATOM/USDT','UNI/USDT'
    ]
    
    # Gestão de risco (ajustado para possibilitar ordens com saldo baixo)
    MAX_POSITION_SIZE = 0.60  # antes 0.10
    MIN_TRADE_AMOUNT = 10     # volta para 10 para cumprir min notional da Binance
    STOP_LOSS_PCT = 0.05
    TAKE_PROFIT_PCT = 0.10
    
    # Timing
    SIGNAL_INTERVAL = 60
    MAX_TRADES_PER_DAY = 50
    
    # ==========================================
    # CONFIGURAÇÕES BINANCE
    # ==========================================
    
    # API Keys (usar variáveis de ambiente)
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', 'your_api_key_here')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', 'your_api_secret_here')
    
    # Configurações da exchange
    BINANCE_TESTNET_URL = 'https://testnet.binance.vision'
    BINANCE_LIVE_URL = 'https://api.binance.com'
    RATE_LIMIT = 1200  # ms entre requests
    
    # ==========================================
    # CONFIGURAÇÕES DE DADOS
    # ==========================================
    
    # Fontes de dados
    DATA_SOURCE = 'yfinance'  # ou 'binance'
    DATA_PERIOD = '1y'  # Período para treinamento
    DATA_INTERVAL = '1h'  # Intervalo dos dados
    
    # Símbolos para diferentes fontes
    YFINANCE_SYMBOLS = {
        'BTC/USDT': 'BTC-USD',
        'ETH/USDT': 'ETH-USD',
        'BNB/USDT': 'BNB-USD',
        'SOL/USDT': 'SOL-USD',
        'XRP/USDT': 'XRP-USD',
        'ADA/USDT': 'ADA-USD',
        'DOGE/USDT': 'DOGE-USD',
        'TRX/USDT': 'TRX-USD',
        'LINK/USDT': 'LINK-USD',
        'AVAX/USDT': 'AVAX-USD',
        'MATIC/USDT': 'MATIC-USD',
        'DOT/USDT': 'DOT-USD',
        'LTC/USDT': 'LTC-USD',
        'ATOM/USDT': 'ATOM-USD',
        'UNI/USDT': 'UNI-USD',
        # Ações permanecem
        'AAPL': 'AAPL',
        'GOOGL': 'GOOGL'
    }
    
    # ==========================================
    # CONFIGURAÇÕES DO DASHBOARD
    # ==========================================
    
    # Streamlit
    DASHBOARD_PORT = 8501
    DASHBOARD_TITLE = "🤖 AI Trading System"
    AUTO_REFRESH_SECONDS = 30
    
    # Gráficos
    CHART_HEIGHT = 600
    CHART_THEME = 'plotly_dark'
    
    # ==========================================
    # CONFIGURAÇÕES DE BACKTEST
    # ==========================================
    
    # Capital inicial
    INITIAL_CAPITAL = 1000  # USD
    
    # Custos de transação
    TRADING_FEE = 0.001  # 0.1% por trade
    SLIPPAGE = 0.0005  # 0.05% slippage
    
    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    @classmethod
    def validate_config(cls):
        """Valida configurações essenciais"""
        errors = []
        
        # Verifica API keys
        if cls.BINANCE_API_KEY == 'your_api_key_here':
            errors.append("❌ Configure BINANCE_API_KEY")
        
        if cls.BINANCE_API_SECRET == 'your_api_secret_here':
            errors.append("❌ Configure BINANCE_API_SECRET")
        
        # Verifica pesos
        if abs(cls.AI_WEIGHT + cls.MOMENTUM_WEIGHT - 1.0) > 0.001:
            errors.append("❌ AI_WEIGHT + MOMENTUM_WEIGHT deve somar 1.0")
        
        # Verifica valores mínimos
        if cls.AI_EPISODES < 5:
            errors.append("⚠️ AI_EPISODES muito baixo (mínimo 5)")
        
        # Ajuste: permitir até 0.60
        if cls.MAX_POSITION_SIZE > 0.60:
            errors.append("⚠️ MAX_POSITION_SIZE acima de 60% não permitido")
        elif cls.MAX_POSITION_SIZE > 0.30:
            # Apenas aviso, não bloqueia
            pass  # poderíamos adicionar um warning em logs se desejado
        
        return errors
    
    @classmethod
    def get_binance_url(cls):
        """Retorna URL da Binance baseada no modo"""
        return cls.BINANCE_TESTNET_URL if cls.TESTNET_MODE else cls.BINANCE_LIVE_URL
    
    @classmethod
    def get_yfinance_symbol(cls, binance_pair):
        """Converte par Binance para símbolo Yahoo Finance"""
        return cls.YFINANCE_SYMBOLS.get(binance_pair, binance_pair.replace('/', '-'))
    
    @classmethod
    def print_config(cls):
        """Imprime configuração atual"""
        print("⚙️ CONFIGURAÇÃO DO SISTEMA AI TRADING")
        print("=" * 50)
        print(f"🔧 Modo: {'TESTNET' if cls.TESTNET_MODE else 'LIVE'}")
        print(f"🤖 AI Weight: {cls.AI_WEIGHT:.1%}")
        print(f"📈 Momentum Weight: {cls.MOMENTUM_WEIGHT:.1%}")
        print(f"🎯 Trading Pairs: {', '.join(cls.TRADING_PAIRS)}")
        print(f"💰 Capital Inicial: ${cls.INITIAL_CAPITAL:,.2f}")
        print(f"🔒 Max Position: {cls.MAX_POSITION_SIZE:.1%}")
        print(f"📊 AI Episodes: {cls.AI_EPISODES}")
        print(f"💼 Percent Capital Treino: {getattr(cls, 'TRAIN_CAPITAL_PERCENT', 75):.0%}")
        print(f"💾 Checkpoint Freq: {cls.CHECKPOINT_FREQUENCY} | Best: {cls.SAVE_BEST_CHECKPOINT}")
        print(f"🧪 Step Sample: {cls.STEP_LOG_SAMPLE} | JSONL Max: {cls.JSONL_MAX_LINES}")
        print(f"🧘 Epsilon Decay: {cls.AI_EPSILON_DECAY} | EarlyStop: {cls.EARLY_STOP_ENABLED}")
        print("=" * 50)

# ==========================================
# CONFIGURAÇÕES ESPECÍFICAS POR AMBIENTE
# ==========================================

class DevConfig(TradingConfig):
    """Configuração para desenvolvimento"""
    TESTNET_MODE = True
    AI_EPISODES = 5
    TRADING_PAIRS = ['BTC/USDT','ETH/USDT','SOL/USDT']
    MAX_POSITION_SIZE = 0.15
    MIN_TRADE_AMOUNT = 5
    SIGNAL_INTERVAL = 30

class TestConfig(TradingConfig):
    """Configuração para testes"""
    TESTNET_MODE = True
    AI_EPISODES = 10
    TRADING_PAIRS = ['BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT']

class ProdConfig(TradingConfig):
    """Configuração para produção"""
    TESTNET_MODE = False  # CUIDADO!
    LIVE_TRADING = True
    AI_EPISODES = 50
    TRADING_PAIRS = TradingConfig.TRADING_PAIRS
    MAX_POSITION_SIZE = 0.55  # produção levemente reduzido
    MIN_TRADE_AMOUNT = 10
    SIGNAL_INTERVAL = 60
    TRAIN_CAPITAL_PERCENT = 0.75  # produção um pouco mais conservador
    STEP_LOG_SAMPLE = 2           # maior granularidade em produção

# ==========================================
# FUNÇÃO PARA ESCOLHER CONFIGURAÇÃO
# ==========================================

def get_config(env='prod'):
    """
    Retorna configuração baseada no ambiente
    env: 'dev', 'test', 'prod'
    """
    configs = {
        'dev': DevConfig,
        'test': TestConfig,
        'prod': ProdConfig
    }
    
    return configs.get(env, ProdConfig)

if __name__ == "__main__":
    # Exemplo de uso
    config = get_config('prod')
    
    # Valida configuração
    errors = config.validate_config()
    if errors:
        print("⚠️ ERROS DE CONFIGURAÇÃO:")
        for error in errors:
            print(f"  {error}")
    else:
        print("✅ Configuração válida!")
    
    # Mostra configuração
    config.print_config()
