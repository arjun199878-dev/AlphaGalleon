import { Outlet, NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Briefcase,
  FileText,
  Activity,
  Settings as SettingsIcon,
  Anchor,
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Users', path: '/users', icon: Users },
  { name: 'Portfolios', path: '/portfolios', icon: Briefcase },
  { name: 'Memos', path: '/memos', icon: FileText },
  { name: 'Activity', path: '/activity', icon: Activity },
  { name: 'Settings', path: '/settings', icon: SettingsIcon },
];

const Sidebar = () => {
  return (
    <aside className="w-64 bg-[#0B1120] text-white min-h-screen flex flex-col fixed left-0 top-0 z-20">
      {/* Logo */}
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center">
            <Anchor size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight">AlphaGalleon</h1>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest">Admin Console</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-1 mt-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-600/20 text-blue-400 font-semibold'
                    : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
                }`
              }
            >
              <Icon size={18} />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-400 flex items-center justify-center text-white text-xs font-bold">
            AT
          </div>
          <div>
            <p className="text-xs font-medium text-slate-300">Arjun Tr</p>
            <p className="text-[10px] text-slate-500">Founder</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

const Header = () => {
  const location = useLocation();
  const current = navItems.find(
    (n) => n.path === location.pathname || (n.path !== '/' && location.pathname.startsWith(n.path))
  ) ?? navItems[0];

  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/60 h-16 flex items-center justify-between px-8 fixed top-0 left-64 right-0 z-10">
      <h2 className="text-lg font-semibold text-slate-800">{current.name}</h2>
      <div className="flex items-center gap-3">
        <div className="text-xs text-slate-400 bg-slate-100 px-3 py-1.5 rounded-full">
          Convex <span className="text-emerald-500">●</span> Connected
        </div>
      </div>
    </header>
  );
};

const Layout = () => {
  return (
    <div className="min-h-screen bg-slate-50 flex">
      <Sidebar />
      <div className="flex-1 ml-64">
        <Header />
        <main className="mt-16 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
