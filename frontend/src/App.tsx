import { useState, useEffect } from 'react';
import axios from 'axios';
import GraphCanvas from './GraphCanvas';

function App() {
  const [health, setHealth] = useState<string>('Loading...');
  const [syncData, setSyncData] = useState<{ entity_count: number; automation_count: number } | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    // API call to the backend using environment variable
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    axios.get(`${apiUrl}/health`)
      .then(res => setHealth(res.data.status))
      .catch(() => setHealth('Error connecting to backend'));
  }, []);

  const handleSync = async () => {
    setIsSyncing(true);
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    try {
      const response = await axios.post(`${apiUrl}/api/ingest`);
      setSyncData(response.data);
      console.log("Sync Data Payload:", response.data);
    } catch (error) {
      console.error("Sync failed:", error);
      alert("Sync failed. Check console for details.");
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-md">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-blue-600">HA Validator</h1>
        </div>
        <nav className="mt-6">
          <a href="#" className="block px-6 py-2 text-gray-700 hover:bg-gray-200 hover:text-blue-600">
            Dashboard
          </a>
          <a href="#" className="block px-6 py-2 text-gray-700 hover:bg-gray-200 hover:text-blue-600">
            System Graph
          </a>
          <a href="#" className="block px-6 py-2 text-gray-700 hover:bg-gray-200 hover:text-blue-600">
            Settings
          </a>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="flex justify-between items-center p-6 bg-white shadow-sm">
          <h2 className="text-xl font-semibold text-gray-800">Dashboard</h2>
          <div className="flex items-center space-x-4">
            <button
              onClick={handleSync}
              disabled={isSyncing}
              className={`px-4 py-2 rounded text-white font-bold transition ${isSyncing ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                }`}
            >
              {isSyncing ? 'Syncing...' : 'Sync Home Assistant'}
            </button>
            <span className="text-sm text-gray-500">Backend Status: <span className={health === 'ok' ? 'text-green-500 font-bold' : 'text-red-500'}>{health}</span></span>
            <div className="w-8 h-8 bg-blue-500 rounded-full"></div>
          </div>
        </header>

        {/* Content Body */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-6">
          {syncData && (
            <div className="mb-8 p-4 bg-green-50 border border-green-200 rounded-md">
              <h3 className="text-lg font-medium text-green-800">Sync Successful</h3>
              <p className="text-green-700">
                Found <strong>{syncData.entity_count}</strong> entities and <strong>{syncData.automation_count}</strong> automations.
              </p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="p-6 bg-white rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900">Total Entities</h3>
              <p className="mt-2 text-3xl font-bold text-blue-600">
                {syncData ? syncData.entity_count : '-'}
              </p>
            </div>
            <div className="p-6 bg-white rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900">Automations</h3>
              <p className="mt-2 text-3xl font-bold text-green-600">
                {syncData ? syncData.automation_count : '-'}
              </p>
            </div>
          </div>

          <div className="mb-8">
            <h3 className="text-lg font-medium text-gray-900 mb-4">System Graph</h3>
            <div className="w-full">
              <GraphCanvas />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
