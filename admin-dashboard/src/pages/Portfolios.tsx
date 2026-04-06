import { useState, useEffect } from 'react';
import { useQuery } from 'convex/react';
import { api } from '../../../convex/_generated/api';
import { Briefcase, TrendingUp, AlertCircle, Calendar } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const Portfolios = () => {
  const portfolios = useQuery(api.portfolios.listAll);
  const [loading, setLoading] = useState(!portfolios);

  useEffect(() => {
    if (portfolios) setLoading(false);
  }, [portfolios]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const getRiskColor = (risk: string) => {
    if (risk === 'aggressive') return 'bg-red-100 text-red-700';
    if (risk === 'moderate') return 'bg-orange-100 text-orange-700';
    return 'bg-blue-100 text-blue-700';
  };

  const getStatusBadge = (status: string) => {
    return status === 'active' 
      ? 'bg-green-100 text-green-700' 
      : 'bg-slate-100 text-slate-700';
  };

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Portfolio Management</h1>
        <p className="text-slate-500 mt-2">Monitor all user portfolios and investment allocations.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
          <p className="text-slate-500 text-sm uppercase tracking-widest font-semibold">Total Portfolios</p>
          <h3 className="text-3xl font-bold text-slate-900 mt-2">{portfolios?.length || 0}</h3>
        </div>
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
          <p className="text-slate-500 text-sm uppercase tracking-widest font-semibold">Active</p>
          <h3 className="text-3xl font-bold text-green-600 mt-2">
            {portfolios?.filter(p => p.status === 'active').length || 0}
          </h3>
        </div>
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
          <p className="text-slate-500 text-sm uppercase tracking-widest font-semibold">Total Capital Deployed</p>
          <h3 className="text-3xl font-bold text-slate-900 mt-2">
            ₹{(portfolios?.reduce((sum, p) => sum + (p.capital || 0), 0) || 0).toLocaleString()}
          </h3>
        </div>
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
          <p className="text-slate-500 text-sm uppercase tracking-widest font-semibold">Avg. Capital</p>
          <h3 className="text-3xl font-bold text-slate-900 mt-2">
            ₹{portfolios && portfolios.length > 0 
              ? (portfolios.reduce((sum, p) => sum + (p.capital || 0), 0) / portfolios.length).toLocaleString()
              : 0}
          </h3>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center gap-2">
          <Briefcase size={20} className="text-slate-700" />
          <h2 className="text-lg font-semibold text-slate-900">All Portfolios</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 font-semibold text-slate-900">Portfolio Name</th>
                <th className="px-6 py-4 font-semibold text-slate-900">Owner</th>
                <th className="px-6 py-4 font-semibold text-slate-900">Capital</th>
                <th className="px-6 py-4 font-semibold text-slate-900">Risk Profile</th>
                <th className="px-6 py-4 font-semibold text-slate-900">Time Horizon</th>
                <th className="px-6 py-4 font-semibold text-slate-900">Status</th>
                <th className="px-6 py-4 font-semibold text-slate-900">Created</th>
                <th className="px-6 py-4 font-semibold text-slate-900">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {!portfolios || portfolios.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-8 text-center text-slate-400">
                    <AlertCircle size={24} className="mx-auto mb-2 opacity-50" />
                    No portfolios created yet.
                  </td>
                </tr>
              ) : (
                portfolios.map((portfolio: any) => (
                  <tr key={portfolio._id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                          <Briefcase size={16} className="text-indigo-600" />
                        </div>
                        <span className="font-semibold text-slate-900">{portfolio.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-600 text-xs">{portfolio.userId?.substring(0, 8)}...</td>
                    <td className="px-6 py-4 font-semibold text-slate-900">₹{portfolio.capital?.toLocaleString()}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${getRiskColor(portfolio.riskProfile)}`}>
                        {portfolio.riskProfile}
                      </span>
                    </td>
                    <td className="px-6 py-4">{portfolio.timeHorizon}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${getStatusBadge(portfolio.status)}`}>
                        {portfolio.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1 text-slate-600">
                        <Calendar size={14} />
                        {formatDistanceToNow(new Date(portfolio.createdAt))} ago
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <button className="text-indigo-600 hover:text-indigo-800 text-sm font-semibold">
                        View Details →
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

export default Portfolios;
