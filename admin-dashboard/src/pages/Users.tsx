import { useState, useEffect } from 'react';
import { listUsers, User } from '../api/client';
import { Users as UsersIcon, Mail, Calendar, Zap } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const Users = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listUsers(100);
      setUsers(data || []);
    } catch (err) {
      setError('Failed to load users');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">User Management</h1>
        <p className="text-slate-500 mt-2">Monitor and manage all registered users on AlphaGalleon.</p>
      </header>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="p-6 border-b border-slate-100">
          <div className="flex items-center gap-2 text-slate-700 font-semibold">
            <UsersIcon size={20} />
            Total Users: {users.length}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 font-semibold text-slate-900">Name</th>
                <th className="px-6 py-4 font-semibold text-slate-900">Email</th>
                <th className="px-6 py-4 font-semibold text-slate-900">Risk Profile</th>
                <th className="px-6 py-4 font-semibold text-slate-900">Joined</th>
                <th className="px-6 py-4 font-semibold text-slate-900">Actions</th>
              </tr>
            </thead>
            <tbody divide-y divide-slate-100>
              {users.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-slate-400">
                    No users found.
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user._id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center font-bold text-indigo-700">
                          {user.name.charAt(0).toUpperCase()}
                        </div>
                        <span className="font-semibold text-slate-900">{user.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-slate-600">
                        <Mail size={14} />
                        {user.email}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${
                        user.riskProfile === 'aggressive' ? 'bg-red-100 text-red-700' :
                        user.riskProfile === 'moderate' ? 'bg-orange-100 text-orange-700' :
                        user.riskProfile === 'conservative' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {user.riskProfile || 'Not Set'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-slate-600">
                        <Calendar size={14} />
                        {user.createdAt ? formatDistanceToNow(new Date(user.createdAt)) + ' ago' : 'Unknown'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <button className="text-indigo-600 hover:text-indigo-800 text-sm font-semibold">
                        View Portfolio →
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Users;
