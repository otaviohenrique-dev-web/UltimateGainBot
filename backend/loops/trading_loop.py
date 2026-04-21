import asyncio
import time
from typing import Optional

async def trading_loop(
    data_service,
    trading_engine,
    state_manager,
    feature_cols,
    symbol='BTC/USDT',
    timeframe='15m'
):
    """Loop principal de trading - simples e testável."""
    
    print(">>> 🟢 Trading loop iniciado...")
    
    while True:
        try:
            # Verifica status
            current_state = state_manager.get()
            if current_state['status'] not in ['OPERANDO', 'INICIALIZANDO']:
                await asyncio.sleep(1)
                continue
            
            # 1. Busca dados (com cache 60s)
            df = await data_service.fetch_and_process(symbol, timeframe)
            if df is None or len(df) < 2:
                await asyncio.sleep(1)
                continue
            
            # 2. Prediz ação (se modelo pronto)
            action = await trading_engine.predict_action(df, feature_cols)
            
            # 3. Executa trade
            last_candle = df.iloc[-1]
            current_price = float(last_candle['close'])
            result = trading_engine.execute_trade(action, current_price)
            
            # 4. Atualiza estado
            stats = trading_engine.get_stats()
            state_manager.update(
                status='OPERANDO',
                balance=round(trading_engine.balance, 2),
                position=trading_engine.position,
                entry_price=round(trading_engine.entry_price, 2),
                current_price=round(current_price, 2),
                last_candle={
                    'time': int(last_candle['timestamp'].timestamp()),
                    'open': float(last_candle['open']),
                    'high': float(last_candle['high']),
                    'low': float(last_candle['low']),
                    'close': current_price
                },
                adaptation={
                    'wins': stats['wins'],
                    'losses': stats['losses'],
                    'win_rate': round(stats['win_rate'], 1),
                    'total_trades': stats['total_trades']
                }
            )
            
            await asyncio.sleep(1)
        
        except Exception as e:
            print(f">>> ❌ Erro no trading loop: {type(e).__name__}: {e}")
            await asyncio.sleep(5)

async def heartbeat_loop(state_manager, start_time):
    """Atualiza uptime a cada segundo."""
    while True:
        try:
            elapsed = int(time.time() - start_time)
            uptime = f"{elapsed // 3600:02d}:{(elapsed % 3600) // 60:02d}:{elapsed % 60:02d}"
            state_manager.update(uptime=uptime)
            await asyncio.sleep(1)
        except Exception as e:
            print(f">>> ❌ Erro no heartbeat: {e}")
            await asyncio.sleep(1)

async def news_loop(news_service, state_manager):
    """Busca notícias a cada 5 minutos."""
    while True:
        try:
            headlines = await news_service.fetch_news()
            state_manager.update(news=headlines)
            await asyncio.sleep(300)  # 5 minutos
        except Exception as e:
            print(f">>> ❌ Erro no news loop: {e}")
            await asyncio.sleep(300)