import { useQuery } from "convex/react";
import { api } from "../../../convex/_generated/api";
import { Users, Briefcase, FileText, CheckCircle } from 'lucide-react';

const Dashboard = () => {
  const stats = useQuery(api.activity.dashboardStats);

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const statCards = [
    { label: 'Total Users', value: stats.totalUsers, icon: Users, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Active Portfolios', value: stats.activePortfolios, icon: Briefcase, color: 'text-green-600', bg: 'bg-green-50' },
    { label: 'Investment Memos', value: stats.totalMemos, icon: FileText, color: 'text-purple-600', bg: 'bg-purple-50' },
    { label: 'System Health', value: '100%', icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-50' },
  ];

  return (
    <div className="space-y-8 p-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">AlphaGalleon Command Center</h1>
        <p className="text-slate-500 mt-2">Real-time system intelligence and user metrics.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => (
          <div key={stat.label} className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 transition-all hover:shadow-md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">{stat.label}</p>
                <h3 className="text-3xl font-bold text-slate-900 mt-1">{stat.value}</h3>
              </div>
              <div className={`${stat.bg} ${stat.color} p-3 rounded-xl`}>
                <stat.icon size={24} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Recent Users</h3>
          <div className="space-y-4">
            {stats.recentUsers.map((user: any) => (
              <div key={user._id} className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-600">
                    {user.name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{user.name}</p>
                    <p className="text-xs text-slate-500">{user.email}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase ${
                    user.riskProfile === 'aggressive' ? 'bg-red-50 text-red-600' :
                    user.riskProfile === 'moderate' ? 'bg-orange-50 text-orange-600' : 'bg-blue-50 text-blue-600'
                  }`}>
                    {user.riskProfile || 'No Profile'}
                  </span>
                </div>
              </div>
            ))}
            {stats.recentUsers.length === 0 && (
              <p className="text-slate-400 text-center py-8 italic">No users onboarded yet.</p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Core Actions</h3>
          <div className="grid grid-cols-2 gap-4">
            <button className="flex flex-col items-center justify-center p-6 rounded-2xl border-2 border-dashed border-slate-200 hover:border-indigo-400 hover:bg-indigo-50 transition-all group">
              <FileText className="text-slate-400 group-hover:text-indigo-600 mb-2" size={32} />
              <span className="text-sm font-semibold text-slate-600 group-hover:text-indigo-700">Audit Memos</span>
            </button>
            <button className="flex flex-col items-center justify-center p-6 rounded-2xl border-2 border-dashed border-slate-200 hover:border-indigo-400 hover:bg-indigo-50 transition-all group">
              <Briefcase className="text-slate-400 group-hover:text-indigo-600 mb-2" size={32} />
              <span className="text-sm font-semibold text-slate-600 group-hover:text-indigo-700">Check Portfolios</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
