import StatusPanel from './StatusPanel';

export default function Dashboard({ data, connected, sendCommand }) {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
          <div>
            <h1 className="text-3xl font-extrabold text-blue-400 tracking-tight">Ultimate Gain</h1>
            <p className="text-gray-400 text-sm mt-1">v3.0.1 - Latência Zero via WebSocket</p>
          </div>
          <div className="text-right">
            <p className="text-gray-400 text-sm">Uptime</p>
            <p className="text-xl font-mono">{data?.uptime || '00:00:00'}</p>
          </div>
        </header>

        <StatusPanel data={data} connected={connected} />

        {/* Controles do Bot */}
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 mb-6 flex gap-4">
          <button 
            onClick={() => sendCommand('resume')}
            disabled={!connected || data?.status === 'OPERANDO'}
            className="bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white font-bold py-2 px-6 rounded transition"
          >
            ▶ Iniciar / Resumir
          </button>
          <button 
            onClick={() => sendCommand('pause')}
            disabled={!connected || data?.status === 'PAUSADO'}
            className="bg-yellow-600 hover:bg-yellow-500 disabled:opacity-50 text-white font-bold py-2 px-6 rounded transition"
          >
            ⏸ Pausar Trading
          </button>
        </div>

        {/* Aqui no futuro você pode importar o seu Chart.js */}
        <div className="bg-gray-800 h-96 rounded-lg border border-gray-700 flex items-center justify-center text-gray-500">
          [ Área Reservada para o Gráfico (Lightweight Charts) ]
        </div>
      </div>
    </div>
  );
}