import { Layout, Rocket, Shield, Search } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-[#050505] text-slate-200 font-sans selection:bg-[#13ec5b] selection:text-black">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-[#050505]/80 backdrop-blur-md border-b border-white/5 px-8 py-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#13ec5b] rounded-lg flex items-center justify-center font-bold text-black">A</div>
          <span className="text-xl font-bold tracking-tight text-white">AlphaGalleon</span>
        </div>
        <button className="bg-[#13ec5b] text-black px-6 py-2 rounded-full font-bold text-sm hover:shadow-[0_0_20px_rgba(19,236,91,0.4)] transition-all active:scale-95">Waitlist Access</button>
      </nav>

      {/* Hero Section */}
      <header className="relative pt-40 pb-20 px-8 max-w-7xl mx-auto text-center overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-gradient-to-b from-[#13ec5b15] to-transparent pointer-events-none opacity-50" />
        <div className="relative z-10">
          <span className="inline-block px-4 py-1.5 rounded-full border border-[#13ec5b30] bg-[#13ec5b10] text-[#13ec5b] text-[10px] uppercase tracking-[0.3em] font-mono mb-6 animate-pulse">
            ● Phase 1 Deployment Live
          </span>
          <h1 className="text-6xl md:text-8xl font-serif italic text-white mb-8 leading-tight">
            Institutional Intelligence,<br />Direct to Your Vault.
          </h1>
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-12 font-light leading-relaxed">
            Stop chasing tips. AlphaGalleon uses a multi-agent AI Brain to analyze 4,000+ securities, architect portfolios, and diagnose risk in real-time.
          </p>
          <div className="flex flex-col md:row items-center justify-center gap-6">
            <button className="w-full md:w-auto bg-[#13ec5b] text-black px-12 py-4 rounded-xl font-bold text-lg hover:shadow-[0_0_30px_rgba(19,236,91,0.5)] transition-all">Enter the Cockpit</button>
            <p className="text-xs text-slate-500 font-mono">SCAN TO OPEN EXPO GO</p>
          </div>
        </div>
      </header>

      {/* The Hub Reveal */}
      <section className="py-32 px-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-end mb-16">
          <div>
            <h2 className="text-[#13ec5b] text-[10px] uppercase tracking-[0.5em] font-mono mb-4">AlphaGalleon Core</h2>
            <h3 className="text-4xl font-serif text-white">The Hub</h3>
          </div>
          <p className="text-slate-500 text-sm max-w-xs text-right italic">"While others give you reports to read, AlphaGalleon gives you the edge to act."</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[ 
            { name: 'The Brain', desc: 'Synthesizes multi-page annual reports into actionable 15-second memos.', icon: <Rocket />, color: '#13ec5b' },
            { name: 'The Doctor', desc: 'Real-time diagnostic for portfolio health, sector exposure, and risk scoring.', icon: <Shield />, color: '#ef4444' },
            { name: 'The Scout', desc: 'Proprietary CAPEX scanner for high-growth small-cap discovery.', icon: <Search />, color: '#f59e0b' },
            { name: 'The Architect', desc: 'Constructs bespoke allocation strategies based on your specific capital.', icon: <Layout />, color: '#3b82f6' },
          ].map((item, i) => (
            <div key={i} className="group glass-panel p-8 rounded-2xl border border-white/5 hover:border-[#13ec5b30] transition-all hover:bg-white/[0.02] cursor-default">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-6 text-white bg-white/5 group-hover:bg-[#13ec5b20] group-hover:text-[#13ec5b] transition-all">
                {item.icon}
              </div>
              <h4 className="text-xl font-serif text-white mb-3">{item.name}</h4>
              <p className="text-sm text-slate-500 font-light leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-20 px-8 border-t border-white/5 text-center">
        <div className="max-w-2xl mx-auto">
          <p className="text-slate-600 text-xs uppercase tracking-widest mb-4 font-mono">AlphaGalleon Institutional v1.0.0</p>
          <p className="text-slate-400 font-serif italic text-lg mb-8">"Precision, Performance, and Depth are non-negotiable."</p>
          <p className="text-[10px] text-slate-700 uppercase">Designed for Julian & The Elite. © 2026 AlphaGalleon AI.</p>
        </div>
      </footer>

      <style>{`
        .glass-panel {
          background: linear-gradient(145deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.01) 100%);
          backdrop-filter: blur(20px);
        }
      `}</style>
    </div>
  );
};

export default LandingPage;
