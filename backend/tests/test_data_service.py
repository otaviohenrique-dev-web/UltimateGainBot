import pytest
import asyncio
import pandas as pd
from backend.services.data_service import DataService

class MockExchange:
    """Simula o comportamento da ccxt.kraken para testes."""
    async def fetch_ohlcv(self, symbol, timeframe, limit):
        base_ts = 1600000000000
        # Retorna a quantidade pedida (precisamos de > 200 para a EMA200)
        return [[base_ts + (i * 900000), 100, 105, 95, 102 + (i*0.1), 1000] for i in range(limit)]

@pytest.mark.asyncio
async def test_fetch_and_process_indicators():
    exchange = MockExchange()
    service = DataService(exchange)
    
    # Pedimos 250 velas para garantir o cálculo correto da EMA200
    df = await service.fetch_and_process('BTC/USDT', '15m', limit=250)
    
    assert df is not None
    assert not df.empty
    
    # Verifica se os indicadores principais foram adicionados ao DataFrame
    assert 'rsi' in df.columns
    assert 'ema50' in df.columns
    assert 'ema200' in df.columns
    assert 'log_ret' in df.columns

@pytest.mark.asyncio
async def test_data_service_caching():
    exchange = MockExchange()
    service = DataService(exchange)
    
    # Primeira chamada: faz o fetch real
    df1 = await service.fetch_and_process('BTC/USDT', '15m')
    
    # Segunda chamada imediata: deve retornar do cache (muito mais rápido)
    df2 = await service.fetch_and_process('BTC/USDT', '15m')
    
    assert df1 is df2  # Verifica se é exatamente o mesmo objeto na memória