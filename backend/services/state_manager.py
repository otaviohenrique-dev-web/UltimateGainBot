import json
from typing import Callable, List
import asyncio

class StateManager:
    """Gerenciador de estado imutável e reativo."""
    
    def __init__(self):
        self._state = {
            'asset': 'BTC/USDT',
            'is_online': True,
            'uptime': '00:00:00',
            'status': 'INICIALIZANDO',
            'balance': 100.0,
            'position': 0,
            'entry_price': 0.0,
            'current_price': 0.0,
            'last_candle': {},
            'markers': [],
            'trades': [],
            'news': [],
        }
        self._subscribers: List[Callable] = []
    
    def get(self):
        """Retorna cópia completa do estado (imutável)."""
        return json.loads(json.dumps(self._state))
    
    def update(self, **kwargs):
        """Atualiza estado e notifica subscribers."""
        changed = False
        for key, value in kwargs.items():
            if key in self._state:
                if self._state[key] != value:
                    self._state[key] = value
                    changed = True
        
        if changed:
            self._notify_subscribers()
    
    def subscribe(self, callback: Callable):
        """Registra callback para ser chamado quando estado mudar."""
        self._subscribers.append(callback)
    
    def _notify_subscribers(self):
        """Notifica todos subscribers sobre mudança de estado."""
        state_copy = self.get()
        for callback in self._subscribers:
            try:
                # Se for async
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(state_copy))
                else:
                    callback(state_copy)
            except Exception as e:
                print(f">>> ❌ Erro ao notificar subscriber: {e}")