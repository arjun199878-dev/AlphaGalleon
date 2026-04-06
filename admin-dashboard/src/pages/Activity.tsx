import { useState, useEffect } from 'react';
import { listActivity, Activity } from '../api/client';
import { Activity as ActivityIcon, Clock, User, Zap } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const ActivityPage = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadActivity();
  }, []);

  const loadActivity = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listActivity(200);
      setActivities(data || []);
    } catch (err) {
      setError('Failed to load activity log');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action: string) => {
    if (action.includes('MEMO') || action.includes('BRAIN')) return 'bg-purple-100 text-purple-700';
    if (action.includes('DIAGNOSE') || action.includes('DOCTOR')) return 'bg-red-100 text-red-700';
    if (action.includes('CONSTRUCT') || action.includes('ARCHITECT')) return 'bg-blue-100 text-blue-700';
    if (action.includes('QUOTE') || action.includes('SCOUT')) return 'bg-orange-100 text-orange-700';
    return 'bg-slate-100 text-slate-700';
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
        <h1 className="text-3xl font-bold text-slate-900">Activity Log</h1>
        <p className="text-slate-500 mt-2">Complete audit trail of all system activities and user actions.</p>
      </header>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="p-6 border-b border-slate-100">
          <div className="flex items-center gap-2 text-slate-700 font-semibold">
            <Zap size={20} />
            Recent Activities: {activities.length}
          </div>
        </div>

        <div className="divide-y divide-slate-100">
          {activities.length === 0 ? (
            <div className="p-8 text-center text-slate-400">
              <ActivityIcon size={32} className="mx-auto mb-2 opacity-50" />
              <p>No activities recorded yet.</p>
            </div>
          ) : (
            activities.map((activity, idx) => (
              <div key={activity._id || idx} className="p-6 hover:bg-slate-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="mt-1">
                      <Zap size={18} className="text-slate-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${getActionColor(activity.action)}`}>
                          {activity.action}
                        </span>
                        <span className="text-xs text-slate-500 flex items-center gap-1">
                          <Clock size={12} />
                          {formatDistanceToNow(new Date(activity.timestamp))} ago
                        </span>
                      </div>
                      <p className="text-slate-700 text-sm">{activity.details}</p>
                      {activity.userId && (
                        <div className="text-xs text-slate-500 mt-2 flex items-center gap-1">
                          <User size={12} />
                          User ID: {activity.userId}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-blue-700 text-sm">
          💡 <strong>Tip:</strong> Filter activities by action type to monitor specific engine usage (Brain memos, Doctor diagnostics, Architect constructions).
        </p>
      </div>
    </div>
  );
};

export default ActivityPage;
