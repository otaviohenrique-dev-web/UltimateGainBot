'use client';

import { useWebSocket } from '../hooks/useWebSocket';

export default function HomePage() {
  // Conecta ao backend que está rodando em http://127.0.0.1:8000
  const { data, connected } = useWebSocket('127.0.0.1:8000/ws');

  return (
    <main className="p-4">
      <h1 className="text-2xl font-bold">Ultimate Gain</h1>
      <p>Status da Conexão: {connected ? '🟢 Conectado' : '🔴 Desconectado'}</p>
      <pre className="mt-4 p-2 bg-gray-800 rounded-md overflow-auto">{JSON.stringify(data, null, 2)}</pre>
    </main>
  );
}