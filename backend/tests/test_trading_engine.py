import pytest
from backend.services.trading_engine import TradingEngine

def test_execute_trade_buy_and_sell():
    # Inicializa com 100 dólares e taxa zero para facilitar a matemática do teste
    engine = TradingEngine(model=None, balance=100.0)
    
    # 1. Abre posição LONG (ação 1) no preço de 100
    engine.execute_trade(action=1, current_price=100.0, fee_rate=0.0)
    assert engine.position == 1
    assert engine.entry_price == 100.0
    
    # 2. Fecha a posição (ação 0) no preço de 110 (10% de lucro)
    engine.execute_trade(action=0, current_price=110.0, fee_rate=0.0)
    assert engine.position == 0
    assert engine.balance == 110.0  # 100 + 10% de lucro
    
    # 3. Verifica as estatísticas
    stats = engine.get_stats()
    assert stats['wins'] == 1
    assert stats['losses'] == 0
    assert stats['total_trades'] == 1
    assert stats['total_pnl'] == 10.0

def test_execute_trade_short_loss():
    engine = TradingEngine(model=None, balance=100.0)
    
    # 1. Abre posição SHORT (ação 2) no preço de 100
    engine.execute_trade(action=2, current_price=100.0, fee_rate=0.0)
    assert engine.position == -1
    
    # 2. Preço sobe para 110 (prejuízo de 10% em short), fecha posição
    engine.execute_trade(action=0, current_price=110.0, fee_rate=0.0)
    assert engine.balance == 90.0  # 100 - 10%
    
    stats = engine.get_stats()
    assert stats['losses'] == 1