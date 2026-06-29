import { useState, type FormEvent } from 'react';

// Define the shape of the data returned by our LangGraph API
interface QueryResponse {
  status: string;
  sql: string;
  data: Record<string, string | number | boolean | null>[];
  logs: string[];
}

export default function App() {
  const [prompt, setPrompt] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [errorLogs, setErrorLogs] = useState<string[]>([]);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setResponse(null);
    setErrorLogs([]);

    try {
      const res = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        // FastAPI returns errors in a 'detail' object
        throw data.detail;
      }
      
      setResponse(data as QueryResponse);
    } catch (err: any) {
      // Extract logs from the LangGraph error state, or provide a fallback
      setErrorLogs(err?.logs || ['An unexpected network failure occurred.']);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
      <header className="max-w-4xl mx-auto mb-8">
        <h1 className="text-3xl font-extrabold text-indigo-400">NL-Database Analyst</h1>
        <p className="text-slate-400 mt-1">Autonomous self-healing Text-to-SQL system powered by LangGraph</p>
      </header>

      <main className="max-w-4xl mx-auto space-y-6">
        {/* Input Card */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            <label className="block text-sm font-medium text-slate-300">
              Ask your database a question:
            </label>
            <div className="flex gap-3">
              <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g., Which product category generated the highest revenue last month?"
                className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
              <button
                type="submit"
                disabled={loading}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 px-6 py-3 rounded-lg font-semibold transition"
              >
                {loading ? 'Analyzing...' : 'Run Agent'}
              </button>
            </div>
          </form>
        </div>

        {/* Execution Terminal & Logs */}
        {(loading || response || errorLogs.length > 0) && (
          <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 font-mono text-xs space-y-3 shadow-inner">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
              LangGraph State Terminal
            </h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {loading && (
                <p className="text-amber-400 animate-pulse">
                   Booting system agent and compiling graph state...
                </p>
              )}
              {response?.logs.map((log, idx) => (
                <p 
                  key={idx} 
                  className={
                    log.includes('❌') ? 'text-rose-400' : 
                    log.includes('successful') ? 'text-emerald-400' : 
                    'text-slate-300'
                  }
                >
                   {log}
                </p>
              ))}
              {errorLogs.map((log, idx) => (
                <p key={`err-${idx}`} className="text-rose-500"> {log}</p>
              ))}
            </div>
          </div>
        )}

        {/* Result Data View */}
        {response?.status === 'success' && (
          <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-xl">
            <div className="p-4 bg-slate-750 border-b border-slate-700">
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wide block mb-1">
                Final Executed SQL
              </span>
              <code className="text-sm text-emerald-400">{response.sql}</code>
            </div>
            {response.data.length > 0 ? (
              <div className="p-6 overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-700 text-slate-400 text-sm">
                      {Object.keys(response.data[0]).map((key) => (
                        <th key={key} className="pb-3 px-4 font-semibold capitalize">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-750 text-sm">
                    {response.data.map((row, index) => (
                      <tr key={index} className="hover:bg-slate-750/50">
                        {Object.values(row).map((val, i) => (
                          <td key={i} className="py-3 px-4 text-slate-300">
                            {String(val)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-6 text-slate-400 text-sm">
                Query executed successfully, but returned 0 rows.
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}