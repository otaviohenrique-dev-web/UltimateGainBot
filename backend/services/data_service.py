import asyncio
import time
import pandas as pd
import numpy as np
import pandas_ta_classic as ta
from datetime import datetime

FEATURE_COLS = ['log_ret', 'rsi', 'rsi_slope', 'macd_diff', 'bb_pband', 'bb_width', 'dist_ema50', 'dist_ema200', 'atr_pct']

class DataService:
    """Serviço responsável por buscar e processar dados de mercado."""
    
    def __init__(self, exchange):
        self.exchange = exchange
        self.last_fetch_ts = 0
        self.cached_df = None
    
    async def fetch_and_process(self, symbol, timeframe, limit=250):
        """
        Busca OHLCV da API e calcula indicadores.
        Retorna None se cache ainda é válido (<60s).
        """
        now = time.time()
        
        # Cache de 60 segundos
        if self.last_fetch_ts > 0 and (now - self.last_fetch_ts) < 60:
            return self.cached_df
        
        try:
            print(f">>> 📊 Buscando OHLCV ({symbol} {timeframe})...")
            ohlcv = await asyncio.wait_for(
                self.exchange.fetch_ohlcv(symbol, timeframe, limit),
                timeout=15.0
            )
            
            self.last_fetch_ts = now
            print(f">>> ✅ Recebido {len(ohlcv)} velas")
            
            # Processa indicadores em thread separada (não bloqueia)
            df = await asyncio.to_thread(self._process_indicators, ohlcv)
            self.cached_df = df
            
            return df
        
        except asyncio.TimeoutError:
            print(f">>> ⚠️ Timeout ao buscar OHLCV")
            return None
        except Exception as e:
            print(f">>> ❌ Erro ao buscar OHLCV: {type(e).__name__}: {e}")
            return None
    
    def _process_indicators(self, ohlcv):
        """Cálculo pesado de indicadores - roda em thread."""
        try:
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Log returns
            df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
            
            # RSI
            df['rsi'] = ta.rsi(df['close'], length=14)
            df['rsi_slope'] = df['rsi'].diff()
            
            # MACD
            macd = ta.macd(df['close'])
            if macd is not None and not macd.empty:
                macd_cols = [c for c in macd.columns if c.startswith('MACDH')]
                if macd_cols:
                    df['macd_diff'] = macd[macd_cols[0]]
                else:
                    df['macd_diff'] = 0.0
            else:
                df['macd_diff'] = 0.0
            
            # Bollinger Bands
            bb = ta.bbands(df['close'], length=20, std=2)
            if bb is not None and not bb.empty:
                upper_cols = [c for c in bb.columns if c.startswith('BBU')]
                lower_cols = [c for c in bb.columns if c.startswith('BBL')]
                width_cols = [c for c in bb.columns if c.startswith('BBB')]
                if upper_cols and lower_cols and width_cols:
                    df['bb_pband'] = (df['close'] - bb[lower_cols[0]]) / (bb[upper_cols[0]] - bb[lower_cols[0]])
                    df['bb_width'] = bb[width_cols[0]]
                else:
                    df['bb_pband'], df['bb_width'] = 0.0, 0.0
            else:
                df['bb_pband'], df['bb_width'] = 0.0, 0.0
            
            # EMAs
            df['ema50'] = ta.ema(df['close'], length=50)
            df['ema200'] = ta.ema(df['close'], length=200)
            df['dist_ema50'] = (df['close'] - df['ema50']) / df['ema50']
            df['dist_ema200'] = (df['close'] - df['ema200']) / df['ema200']
            
            # ATR
            df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
            df['atr_pct'] = df['atr'] / df['close']
            
            return df.dropna()
        
        except Exception as e:
            print(f">>> ❌ Erro ao processar indicadores: {e}")
            return None