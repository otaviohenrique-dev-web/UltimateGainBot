export default function StatusPanel({ data, connected }) {
  if (!data) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 shadow">
        <h3 className="text-gray-400 text-sm font-semibold">Status do Sistema</h3>
        <div className="flex items-center mt-2">
          <div className={`w-3 h-3 rounded-full mr-2 ${connected ? 'bg-green-500' : 'bg-red-500 animate-pulse'}`}></div>
          <span className="text-white font-bold">{connected ? data.status : 'DESCONECTADO'}</span>
        </div>
      </div>

      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 shadow">
        <h3 className="text-gray-400 text-sm font-semibold">Saldo Atual (USDT)</h3>
        <p className="text-2xl text-white font-bold mt-1">
          ${data.balance?.toFixed(2)}
        </p>
      </div>

      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 shadow">
        <h3 className="text-gray-400 text-sm font-semibold">Posição Atual</h3>
        <p className={`text-2xl font-bold mt-1 ${
          data.position === 1 ? 'text-green-400' : 
          data.position === -1 ? 'text-red-400' : 'text-gray-300'
        }`}>
          {data.position === 1 ? 'LONG 📈' : data.position === -1 ? 'SHORT 📉' : 'HOLD ⏸️'}
        </p>
      </div>

      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 shadow">
        <h3 className="text-gray-400 text-sm font-semibold">Preço do Ativo</h3>
        <p className="text-2xl text-white font-bold mt-1">
          ${data.current_price?.toFixed(2) || '---'}
        </p>
      </div>
    </div>
  );
}