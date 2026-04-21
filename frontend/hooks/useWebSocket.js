import { useEffect, useRef, useState } from 'react';

export function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const ws = useRef(null);
  const reconnectAttempts = useRef(0);

  useEffect(() => {
    const connect = () => {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${url.replace(/^https?:\/\//, '')}`;
        
        console.log(`🔌 Conectando WebSocket: ${wsUrl}`);
        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
          console.log("✅ WebSocket conectado");
          setConnected(true);
          reconnectAttempts.current = 0;
        };

        ws.current.onmessage = (event) => {
          try {
            const state = JSON.parse(event.data);
            setData(state);
          } catch (e) {
            console.error("❌ Erro ao parsear WebSocket message:", e);
          }
        };

        ws.current.onclose = () => {
          console.log("⚠️ WebSocket desconectado");
          setConnected(false);
          
          // Reconnect com back-off exponencial
          const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectAttempts.current++;
          
          setTimeout(connect, timeout);
        };

        ws.current.onerror = (error) => {
          console.error("❌ WebSocket error:", error);
        };
      } catch (e) {
        console.error("❌ Erro ao conectar WebSocket:", e);
      }
    };

    connect();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url]);

  const send = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };

  return { data, connected, send };
}