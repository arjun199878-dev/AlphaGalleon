import { useState, useEffect } from 'react';
import axios from 'axios';

const BrainLogs = () => {
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    // Placeholder logs until backend endpoint is ready
    setLogs([
      { id: 1, timestamp: '2023-10-27 10:30:00', level: 'INFO', message: 'Brain initialized' },
      { id: 2, timestamp: '2023-10-27 10:32:15', level: 'WARN', message: 'Market data feed delayed' },
      { id: 3, timestamp: '2023-10-27 10:35:00', level: 'INFO', message: 'User request processed' },
    ]);
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden">
      <div className="p-6 border-b border-slate-200 flex justify-between items-center">
        <h3 className="text-lg font-semibold text-slate-800">System Logs</h3>
        <input
          type="search"
          placeholder="Filter logs..."
          className="border border-slate-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <table className="w-full text-left text-sm text-slate-600">
        <thead className="bg-slate-50 border-b border-slate-200">
          <tr>
            <th className="px-6 py-3 font-semibold text-slate-900">Time</th>
            <th className="px-6 py-3 font-semibold text-slate-900">Level</th>
            <th className="px-6 py-3 font-semibold text-slate-900">Message</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap font-mono text-xs">{log.timestamp}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                    log.level === 'INFO'
                      ? 'bg-blue-100 text-blue-800'
                      : log.level === 'WARN'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {log.level}
                </span>
              </td>
              <td className="px-6 py-4 text-slate-800">{log.message}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BrainLogs;
