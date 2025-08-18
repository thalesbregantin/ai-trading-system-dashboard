#!/usr/bin/env python3
"""
Teste de Conexão com Binance (Refatorado - Passo 1)
- Separa cada teste em função
- Adiciona logging estruturado
- Mede latência por teste
- Suporte a saída JSON (--json)
- (Extensão) Teste de drift de tempo, exchangeInfo e headers de rate limit
"""

import os
import sys
import time
import json
import logging
import argparse
from typing import Dict, Any, List

# Adiciona caminho para módulo core
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.binance_real_data import binance_data  # type: ignore

# =============================
# Configuração de Logging
# =============================

def create_logger(verbose: bool = True) -> logging.Logger:
    logger = logging.getLogger("binance_connection_test")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    return logger

# =============================
# Utilidades
# =============================

def check_api_keys() -> Dict[str, Any]:
    start = time.time()
    # Suporta ambos os padrões de nome para evitar inconsistência
    api_key = os.getenv("BINANCE_API_KEY") or os.getenv("BINANCE_KEY")
    secret_candidates = {
        "BINANCE_API_SECRET": os.getenv("BINANCE_API_SECRET"),
        "BINANCE_SECRET_KEY": os.getenv("BINANCE_SECRET_KEY")
    }
    # Escolhe o primeiro não vazio
    secret_key = next((v for v in secret_candidates.values() if v), None)
    ok = bool(api_key and secret_key)
    details = {
        "has_api_key": bool(api_key),
        "has_BINANCE_API_SECRET": bool(secret_candidates["BINANCE_API_SECRET"]),
        "has_BINANCE_SECRET_KEY": bool(secret_candidates["BINANCE_SECRET_KEY"]),
    }
    missing = []
    if not api_key:
        missing.append("BINANCE_API_KEY")
    if not secret_key:
        missing.append("BINANCE_API_SECRET|BINANCE_SECRET_KEY")
    return {
        "name": "api_keys",
        "ok": ok,
        "latency_ms": int((time.time() - start) * 1000),
        "error": None if ok else f"Variáveis ausentes: {', '.join(missing)}",
        "details": details
    }

# =============================
# Testes Individuais
# =============================

def test_time_sync(logger: logging.Logger, max_drift_ms: int = 2000) -> Dict[str, Any]:
    start = time.time()
    name = "time_sync"
    try:
        ex = getattr(binance_data, 'exchange', None)
        if not ex:
            return {"name": name, "ok": False, "latency_ms": int((time.time()-start)*1000), "error": "Exchange não inicializada", "details": {}}
        server_ms = ex.fetch_time()  # ms epoch
        local_ms = int(time.time()*1000)
        drift = abs(server_ms - local_ms)
        ok = drift <= max_drift_ms
        return {"name": name, "ok": ok, "latency_ms": int((time.time()-start)*1000),
                "error": None if ok else f"Drift {drift}ms > {max_drift_ms}ms", 
                "details": {"server_time": server_ms, "local_time": local_ms, "drift_ms": drift, "max_allowed_ms": max_drift_ms}}
    except Exception as e:  # noqa
        logger.exception("Erro em test_time_sync")
        return {"name": name, "ok": False, "latency_ms": int((time.time()-start)*1000), "error": str(e), "details": {}}

def test_balance(logger: logging.Logger) -> Dict[str, Any]:
    start = time.time()
    name = "balance"
    try:
        data = binance_data.get_account_balance()
        ok = bool(data)
        details = {}
        if ok:
            details = {
                "total_usdt": data.get("total_usdt"),
                "free_usdt": data.get("free_usdt"),
                "timestamp": data.get("timestamp"),
                "currencies": len([c for c, v in data.get("balances", {}).items() if v.get("total", 0) > 0])
            }
        return {
            "name": name,
            "ok": ok,
            "latency_ms": int((time.time() - start) * 1000),
            "error": None if ok else "Falha ao obter saldo",
            "details": details
        }
    except Exception as e:  # noqa
        logger.exception("Erro em test_balance")
        return {
            "name": name,
            "ok": False,
            "latency_ms": int((time.time() - start) * 1000),
            "error": str(e),
            "details": {}
        }

def test_trades(logger: logging.Logger, days: int = 7) -> Dict[str, Any]:
    start = time.time()
    name = "trades"
    try:
        trades = binance_data.get_trading_history(days=days)
        ok = not trades.empty
        details = {
            "count": int(len(trades)),
            "days": days
        }
        if ok:
            tail = trades.tail(3)
            details["last_trades"] = [
                {
                    "timestamp": str(row.get("timestamp")),
                    "symbol": row.get("symbol"),
                    "side": row.get("side"),
                    "cost": float(row.get("cost", 0) or 0)
                } for _, row in tail.iterrows()
            ]
        return {
            "name": name,
            "ok": ok,
            "latency_ms": int((time.time() - start) * 1000),
            "error": None if ok else "Nenhum trade recente",
            "details": details
        }
    except Exception as e:  # noqa
        logger.exception("Erro em test_trades")
        return {
            "name": name,
            "ok": False,
            "latency_ms": int((time.time() - start) * 1000),
            "error": str(e),
            "details": {}
        }

def test_positions(logger: logging.Logger) -> Dict[str, Any]:
    start = time.time()
    name = "positions"
    try:
        positions = binance_data.get_current_positions()
        ok = bool(positions)
        details = {"count": len(positions) if positions else 0}
        if ok:
            details["positions_sample"] = positions[:3]
        return {
            "name": name,
            "ok": ok,
            "latency_ms": int((time.time() - start) * 1000),
            "error": None,
            "details": details
        }
    except Exception as e:  # noqa
        logger.exception("Erro em test_positions")
        return {
            "name": name,
            "ok": False,
            "latency_ms": int((time.time() - start) * 1000),
            "error": str(e),
            "details": {}
        }

def test_exchange_info(logger: logging.Logger, symbol: str) -> Dict[str, Any]:
    start = time.time()
    name = "exchange_info"
    try:
        ex = getattr(binance_data, 'exchange', None)
        if not ex:
            return {"name": name, "ok": False, "latency_ms": int((time.time()-start)*1000), "error": "Exchange não inicializada", "details": {}}
        market = ex.market(symbol) if symbol in ex.markets else None
        if not market:
            return {"name": name, "ok": False, "latency_ms": int((time.time()-start)*1000), "error": f"Símbolo {symbol} não encontrado", "details": {}}
        limits = market.get('limits', {})
        filters = {
            'price_min': limits.get('price', {}).get('min'),
            'price_max': limits.get('price', {}).get('max'),
            'price_precision': market.get('precision', {}).get('price'),
            'qty_min': limits.get('amount', {}).get('min'),
            'qty_max': limits.get('amount', {}).get('max'),
            'qty_precision': market.get('precision', {}).get('amount'),
            'notional_min': limits.get('cost', {}).get('min')
        }
        ok = filters['qty_min'] is not None and filters['price_min'] is not None
        return {"name": name, "ok": ok, "latency_ms": int((time.time()-start)*1000), "error": None if ok else "Filtros incompletos", "details": {"symbol": symbol, **filters}}
    except Exception as e:  # noqa
        logger.exception("Erro em test_exchange_info")
        return {"name": name, "ok": False, "latency_ms": int((time.time()-start)*1000), "error": str(e), "details": {}}

def test_market_data(logger: logging.Logger, symbol: str = 'BTC/USDT', timeframe: str = '1h', limit: int = 5) -> Dict[str, Any]:
    start = time.time()
    name = "market_data"
    try:
        market = binance_data.get_market_data(symbol, timeframe, limit)
        ok = not market.empty
        details = {"symbol": symbol, "timeframe": timeframe, "candles": len(market) if ok else 0}
        if ok:
            last = market.iloc[-1]
            details["last"] = {
                "close": float(last.get("close", 0)),
                "volume": float(last.get("volume", 0))
            }
        # Headers de rate limit (se expostos pelo ccxt)
        ex = getattr(binance_data, 'exchange', None)
        headers = getattr(ex, 'last_response_headers', {}) if ex else {}
        if headers:
            used_weights = {k.lower(): v for k, v in headers.items() if k.lower().startswith('x-mbx-used-weight')}
            if used_weights:
                details['used_weight_headers'] = used_weights
        return {
            "name": name,
            "ok": ok,
            "latency_ms": int((time.time() - start) * 1000),
            "error": None if ok else "Falha ao obter market data",
            "details": details
        }
    except Exception as e:  # noqa
        logger.exception("Erro em test_market_data")
        return {
            "name": name,
            "ok": False,
            "latency_ms": int((time.time() - start) * 1000),
            "error": str(e),
            "details": {}
        }

def test_order_test_endpoint(logger: logging.Logger, symbol: str, side: str = 'BUY', qty: float = 0.001) -> Dict[str, Any]:
    start = time.time()
    name = "order_test"
    try:
        ex = getattr(binance_data, 'exchange', None)
        if not ex:
            return {"name": name, "ok": False, "latency_ms": int((time.time()-start)*1000), "error": "Exchange não inicializada", "details": {}}
        # Usa endpoint /order/test via método raw se disponível
        # Monta preço aproximado (último ticker) para LIMIT, mas usa MARKET para simplificar
        params = {}
        # ccxt não possui create_test_order padronizado; fallback: tentar endpoint específico se existir
        ok = True
        error_msg = None
        try:
            # Para evitar execução real em live se não é testnet, só roda se sandbox ou flag ENABLE_ORDER_TEST=="1"
            if not ex.urls.get('test', False) and os.getenv('ENABLE_ORDER_TEST', '0') != '1':
                return {"name": name, "ok": False, "latency_ms": int((time.time()-start)*1000), "error": "Teste de ordem desabilitado (ENABLE_ORDER_TEST!=1)", "details": {}}
            # Tenta usar método binance privado para order test
            method = getattr(ex, 'private_post_order_test', None)
            if method:
                symbol_ccxt = symbol.replace('/', '')  # binance style se necessário nos params? ccxt converte
                res = method({"symbol": symbol_ccxt, "side": side, "type": "MARKET", "quantity": qty})
                details = {"response": res}
            else:
                ok = False
                error_msg = "Método private_post_order_test não disponível"
                details = {}
        except Exception as inner:
            ok = False
            error_msg = str(inner)
            details = {}
        return {"name": name, "ok": ok, "latency_ms": int((time.time()-start)*1000), "error": error_msg, "details": {"symbol": symbol, "side": side, "qty": qty, **details}}
    except Exception as e:  # noqa
        logger.exception("Erro em test_order_test_endpoint")
        return {"name": name, "ok": False, "latency_ms": int((time.time()-start)*1000), "error": str(e), "details": {}}

# =============================
# Orquestrador
# =============================

def test_binance_connection(json_output: bool = False, verbose: bool = True, symbol: str = 'BTC/USDT', timeframe: str = '1h', limit: int = 5, enable_order_test: bool = False) -> Any:
    logger = create_logger(verbose=verbose)
    unicode_ok = sys.stdout.encoding.lower().startswith('utf') if sys.stdout.encoding else False

    def sym(ok: bool) -> str:
        if not unicode_ok:
            return "OK" if ok else "FAIL"
        return "✅" if ok else "❌"

    tests: List[Dict[str, Any]] = []

    tests.append(check_api_keys())
    if not tests[-1]["ok"]:
        logger.warning("Chaves de API ausentes; demais testes podem falhar.")

    # nova ordem lógica: time_sync antes de chamadas intensas
    for fn in (
        lambda lg: test_time_sync(lg),
        test_balance,
        test_trades,
        test_positions,
        lambda lg: test_exchange_info(lg, symbol),
        lambda lg: test_market_data(lg, symbol=symbol, timeframe=timeframe, limit=limit),
    ):
        try:
            result = fn(logger)  # type: ignore
        except Exception as e:  # noqa
            logger.exception("Erro inesperado em execução de teste")
            result = {"name": getattr(fn, '__name__', 'unknown'), "ok": False, "latency_ms": 0, "error": str(e), "details": {}}
        tests.append(result)

    if enable_order_test:
        tests.append(test_order_test_endpoint(logger, symbol=symbol))

    scored = [t for t in tests if t["name"] not in ("api_keys",)]
    success_points = sum(1 for t in scored if t["ok"])
    success_rate = int((success_points / len(scored)) * 100) if scored else 0

    overall_ok = success_rate >= 50
    overall = {
        "ok": overall_ok,
        "success_rate": success_rate,
        "tests_passed": success_points,
        "tests_total": len(scored),
        "timestamp": int(time.time())
    }

    if verbose and not json_output:
        print("\n==== RESUMO TESTE BINANCE ====")
        for t in tests:
            logger.info(f"[{t['name']}] {sym(t['ok'])} | {t['latency_ms']} ms" + (f" | erro: {t['error']}" if t['error'] else ""))
        print(f"Sucesso: {success_rate}% ({success_points}/{len(scored)})")
        if overall_ok:
            logger.info("Condição mínima atingida (>=50%).")
        else:
            logger.error("Condição mínima NÃO atingida (<50%).")

    result = {"overall": overall, "tests": tests, "params": {"symbol": symbol, "timeframe": timeframe, "limit": limit, "order_test": enable_order_test}}
    if json_output:
        # Normaliza objetos não serializáveis
        def _convert(o):
            import datetime
            if isinstance(o, (datetime.datetime, datetime.date)):
                return o.isoformat()
            return o
        return json.dumps(result, ensure_ascii=False, indent=2, default=_convert)
    return overall_ok

# =============================
# CLI
# =============================

def _parse_args():
    parser = argparse.ArgumentParser(description="Testa conexão com Binance")
    parser.add_argument("--json", action="store_true", help="Saída em JSON estruturado")
    parser.add_argument("--quiet", action="store_true", help="Menos logs verbosos")
    parser.add_argument("--symbol", default="BTC/USDT", help="Símbolo para testes de market data/exchangeInfo")
    parser.add_argument("--timeframe", default="1h", help="Timeframe para market data")
    parser.add_argument("--limit", type=int, default=5, help="Número de candles a buscar")
    parser.add_argument("--order-test", action="store_true", help="Executa endpoint de teste de ordem (requer testnet ou ENABLE_ORDER_TEST=1)")
    return parser.parse_args()

if __name__ == "__main__":
    args = _parse_args()
    output = test_binance_connection(json_output=args.json, verbose=not args.quiet, symbol=args.symbol, timeframe=args.timeframe, limit=args.limit, enable_order_test=args.order_test)
    if isinstance(output, str):  # JSON
        print(output)
