import asyncio
import time
import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import ccxt.async_support as ccxt
from sb3_contrib import RecurrentPPO

from services.data_service import DataService, FEATURE_COLS
from services.trading_engine import TradingEngine
from services.state_manager import StateManager
from services.news_service import NewsService
from loops.trading_loop import trading_loop, heartbeat_loop, news_loop

# Configurações
SYMBOL = 'BTC/USDT'
TIMEFRAME = '15m'
MODEL_PATH = "models/sniper_pro_gen_6.zip"
KRAKEN_TIMEOUT = 30000

# Globais (apenas para inicialização)
state_manager = None
data_service = None
trading_engine = None
news_service = None
startup_time = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown do app."""
    global state_manager, data_service, trading_engine, news_service, startup_time
    
    print(">>> 🚀 Iniciando IA Trader Pro v3.0.1...")
    startup_time = time.time()
    
    # Inicializa serviços
    try:
        # Exchange
        exchange = ccxt.kraken({'enableRateLimit': True, 'timeout': KRAKEN_TIMEOUT})
        print(">>> ✅ Kraken conectado")
        
        # State Manager
        state_manager = StateManager()
        state_manager.update(status='INICIALIZANDO')
        
        # Data Service
        data_service = DataService(exchange)
        
        # News Service
        news_service = NewsService(os.environ.get("CRYPTOCOMPARE_API_KEY", ""))
        
        # Carrega modelo em thread (não bloqueia)
        print(f">>> 📍 Carregando modelo de {MODEL_PATH} em thread...")
        model = None
        try:
            model = await asyncio.to_thread(
                RecurrentPPO.load,
                MODEL_PATH,
                device="cpu"
            )
            print(">>> ✅ Modelo carregado com sucesso!")
        except Exception as e:
            print(f">>> ⚠️ Erro ao carregar modelo: {e}")
        
        # Trading Engine
        trading_engine = TradingEngine(model=model, balance=100.0)
        
        # Inicia loops em background (não bloqueiam)
        asyncio.create_task(heartbeat_loop(state_manager, startup_time))
        asyncio.create_task(trading_loop(data_service, trading_engine, state_manager, FEATURE_COLS, SYMBOL, TIMEFRAME))
        asyncio.create_task(news_loop(news_service, state_manager))
        
        state_manager.update(status='OPERANDO', is_online=True)
        print(">>> 🟢 Sistema pronto para operar!")
    
    except Exception as e:
        print(f">>> ❌ Erro ao iniciar: {e}")
        state_manager.update(status=f'ERRO: {str(e)}')
    
    yield
    
    # Cleanup
    print(">>> 🛑 Encerrando...")
    try:
        await exchange.close()
    except:
        pass

# App FastAPI
app = FastAPI(title="IA Trader Pro", version="3.0.1", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ENDPOINTS

@app.get("/")
async def root():
    return {"status": "online", "version": "3.0.1"}

@app.get("/api/state")
async def get_state():
    """Retorna estado completo do sistema."""
    if state_manager is None:
        return {"error": "Sistema não inicializado"}
    
    state = state_manager.get()
    return Response(
        content=json.dumps(state),
        media_type="application/json"
    )

@app.post("/api/control/pause")
async def pause():
    """Pausa trading."""
    state_manager.update(status='PAUSADO')
    return {"status": "pausado"}

@app.post("/api/control/resume")
async def resume():
    """Retoma trading."""
    state_manager.update(status='OPERANDO')
    return {"status": "operando"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/ready")
async def ready():
    """Readiness probe para Render."""
    if state_manager is None:
        return Response(
            content=json.dumps({"ready": False, "status": "inicializando"}),
            status_code=503
        )
    
    state = state_manager.get()
    is_ready = state.get('is_online', False)
    
    return Response(
        content=json.dumps({
            "ready": is_ready,
            "status": state.get('status', 'desconhecido')
        }),
        status_code=200 if is_ready else 503
    )