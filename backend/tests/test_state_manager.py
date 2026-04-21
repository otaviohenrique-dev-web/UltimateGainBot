import pytest
from backend.services.state_manager import StateManager

def test_state_initialization():
    sm = StateManager()
    state = sm.get()
    assert state['status'] == 'INICIALIZANDO'
    assert state['balance'] == 100.0
    assert state['position'] == 0

def test_state_update():
    sm = StateManager()
    sm.update(status='OPERANDO', balance=105.5)
    
    state = sm.get()
    assert state['status'] == 'OPERANDO'
    assert state['balance'] == 105.5

def test_state_subscription():
    sm = StateManager()
    called = False
    
    # Callback mockado simulando o envio via WebSocket
    def mock_callback(state):
        nonlocal called
        called = True
        assert state['position'] == 1
    
    sm.subscribe(mock_callback)
    
    # Ao atualizar a posição, o callback deve ser acionado
    sm.update(position=1)
    
    assert called is True, "O callback não foi acionado após o update"