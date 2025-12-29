import { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [health, setHealth] = useState<string>('Loading...');

  useEffect(() => {
    // Example API call to the backend
    axios.get('http://localhost:8000/health')
      .then(res => setHealth(res.data.status))
      .catch(() => setHealth('Error connecting to backend'));
  }, []);

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
            <span className="text-sm text-gray-500">Backend Status: <span className={health === 'ok' ? 'text-green-500 font-bold' : 'text-red-500'}>{health}</span></span>
            <div className="w-8 h-8 bg-blue-500 rounded-full"></div>
          </div>
        </header>

        {/* Content Body */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="p-6 bg-white rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900">Statistic 1</h3>
              <p className="mt-2 text-3xl font-bold text-blue-600">1,234</p>
            </div>
            <div className="p-6 bg-white rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900">Statistic 2</h3>
              <p className="mt-2 text-3xl font-bold text-green-600">56%</p>
            </div>
            <div className="p-6 bg-white rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900">Statistic 3</h3>
              <p className="mt-2 text-3xl font-bold text-purple-600">89</p>
            </div>
          </div>

          <div className="mt-8">
            <div className="p-6 bg-white rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
              <div className="border-t border-gray-200">
                <ul className="divide-y divide-gray-200">
                  {[1, 2, 3].map((item) => (
                    <li key={item} className="py-4">
                      <div className="flex space-x-3">
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center justify-between">
                            <h3 className="text-sm font-medium">Activity {item}</h3>
                            <p className="text-sm text-gray-500">Just now</p>
                          </div>
                          <p className="text-sm text-gray-500">Description of activity {item} goes here.</p>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
