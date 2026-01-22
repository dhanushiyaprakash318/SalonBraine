import { useState, useRef, useEffect } from "react";
import "./App.css";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  ArcElement
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const SectionHeader = ({ title }) => (
  <div className="flex items-center gap-3 mb-4 px-4 opacity-50">
    <div className="h-[1px] flex-1 bg-gradient-to-r from-[var(--accent-blue)]/50 to-transparent" />
    <h3 className="text-[9px] font-black text-[var(--text-secondary)] uppercase tracking-[0.3em]">
      {title}
    </h3>
    <div className="h-[1px] w-4 bg-[var(--accent-blue)]/20" />
  </div>
);

const NavButton = ({ active, onClick, icon, children }) => (
  <button
    onClick={onClick}
    className={`w-full relative flex items-center gap-3 px-4 py-2.5 rounded-xl text-[13px] font-semibold transition-saas group overflow-hidden ${active
      ? "text-[var(--accent-blue)] shadow-[var(--glow-inner)] active-pill-bg"
      : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)]"
      }`}
  >
    {active && <div className="active-indicator" />}
    <div className={`shrink-0 transition-saas ${active ? "scale-110 drop-shadow-[0_0_8px_var(--accent-blue)]" : "opacity-60 group-hover:opacity-100"}`}>
      {icon}
    </div>
    <span className="relative z-10">{children}</span>
    {active && <div className="absolute inset-0 bg-gradient-to-r from-[var(--accent-blue)]/10 to-transparent pointer-events-none" />}
  </button>
);

const DataTable = ({ data }) => {
  if (!data || data.length === 0) return null;
  const keys = Object.keys(data[0]);

  return (
    <div className="mt-6 premium-card border-[var(--border-color)]/50 shadow-2xl overflow-hidden glass">
      <div className="overflow-x-auto max-h-[400px]">
        <table className="w-full text-[13px] text-left border-separate border-spacing-0">
          <thead>
            <tr className="bg-[var(--bg-tertiary)]/30 border-b border-[var(--border-color)] sticky top-0 z-10 backdrop-blur-xl">
              {keys.map(key => (
                <th key={key} className="px-6 py-4 font-black text-[var(--text-secondary)] uppercase tracking-[0.2em] text-[9px] border-b border-[var(--border-color)]">
                  {key.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border-color)]/30">
            {data.slice(0, 100).map((row, i) => (
              <tr key={i} className="hover:bg-[var(--accent-blue)]/[0.03] transition-saas group">
                {Object.values(row).map((val, j) => (
                  <td key={j} className="px-6 py-4 whitespace-nowrap text-[var(--text-primary)] group-hover:text-[var(--accent-blue)] font-medium transition-colors">
                    {val === null ? <span className="opacity-20 font-light">-</span> : String(val)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-6 py-3.5 bg-[var(--bg-tertiary)]/20 text-[9px] text-[var(--text-secondary)] border-t border-[var(--border-color)]/50 flex justify-between font-black uppercase tracking-[0.2em] opacity-60">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>{data.length} records identified</span>
        </div>
        {data.length > 100 && <span className="text-[var(--accent-blue)]">Optimizer: viewing primary 100</span>}
      </div>
    </div>
  );
};

const DataVisualizer = ({ data }) => {
  if (!data || data.length === 0) return null;

  const keys = Object.keys(data[0]);
  const numericKeys = keys.filter(key => {
    const val = data[0][key];
    return typeof val === 'number' || (!isNaN(parseFloat(val)) && isFinite(val));
  });
  const labelKey = keys.find(key => {
    const k = key.toLowerCase();
    return k.includes('month') || k.includes('year') || k.includes('date');
  }) || keys.find(key => typeof data[0][key] === 'string') || keys[0];

  if (numericKeys.length === 0) return null;

  // Determine if we should use a Line chart (for trends)
  const isTrend = labelKey.toLowerCase().includes('month') ||
    labelKey.toLowerCase().includes('year') ||
    labelKey.toLowerCase().includes('date') ||
    data.length > 8;

  const chartData = {
    labels: data.map(row => row[labelKey]),
    datasets: numericKeys.map((key, index) => ({
      label: key.replace(/_/g, ' '),
      data: data.map(row => Number(row[key]) || 0),
      backgroundColor: index === 0 ? 'rgba(56, 189, 248, 0.2)' : 'rgba(129, 140, 248, 0.2)',
      hoverBackgroundColor: index === 0 ? '#0ea5e9' : '#6366f1',
      borderColor: index === 0 ? '#38bdf8' : '#818cf8',
      borderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
      fill: isTrend,
      tension: 0.4, // Smooth spline
      borderRadius: 8,
      barThickness: 32,
    })),
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: numericKeys.length > 1,
        position: 'top',
        align: 'end',
        labels: {
          color: 'var(--text-secondary)',
          boxWidth: 6, boxHeight: 6,
          usePointStyle: true,
          padding: 20,
          font: { size: 10, weight: '700', family: 'Inter' }
        }
      },
      tooltip: {
        padding: 16,
        backgroundColor: 'rgba(2, 6, 23, 0.85)',
        backdropFilter: 'blur(12px)',
        titleColor: '#fff',
        titleFont: { size: 14, weight: '800' },
        bodyColor: 'rgba(255,255,255,0.8)',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
        displayColors: true,
        cornerRadius: 12,
        boxPadding: 8
      }
    },
    scales: {
      y: {
        ticks: { color: 'var(--text-secondary)', font: { size: 10, weight: '600' }, padding: 10 },
        grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
        border: { display: false }
      },
      x: {
        ticks: { color: 'var(--text-secondary)', font: { size: 10, weight: '600' }, padding: 10 },
        grid: { display: false },
        border: { display: false }
      },
    },
    animation: {
      duration: 1500,
      easing: 'easeOutQuart'
    }
  };

  const ChartComponent = isTrend ? Line : Bar;

  return (
    <div className="mt-12 animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-2 h-5 bg-gradient-to-b from-[var(--accent-blue)] to-blue-600 rounded-full shadow-[0_0_10px_var(--accent-blue)]" />
          <h4 className="text-[10px] font-black text-[var(--text-secondary)] uppercase tracking-[0.4em]">
            {isTrend ? 'Performance Trend Analysis' : 'Statistical Distribution'}
          </h4>
        </div>
        {isTrend && (
          <div className="px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-[9px] font-black text-blue-400 uppercase tracking-widest">
            Time-Series Active
          </div>
        )}
      </div>
      <div className="h-96 p-8 premium-card glass shadow-2xl relative">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[var(--accent-blue)]/20 to-transparent" />
        <ChartComponent options={options} data={chartData} />
      </div>
    </div>
  );
};

export default function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    { type: "bot", content: "System ready. Ask me anything about salon analytics." }
  ]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("chat");
  const [insights, setInsights] = useState(null);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [theme, setTheme] = useState("dark");
  const scrollRef = useRef(null);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === "dark" ? "light" : "dark"));
  };

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const askQuestion = async (queryOverride = null) => {
    const queryText = typeof queryOverride === 'string' ? queryOverride : question;
    if (!queryText.trim()) return;

    setMessages(prev => [...prev, { type: "user", content: queryText }]);
    if (typeof queryOverride !== 'string') setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: queryText }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Backend error");

      setMessages(prev => [...prev, {
        type: data.data && data.data.length > 0 ? "analysis" : "bot",
        content: data.answer || (data.insights && data.insights.length > 0 ? data.insights[0] : "I've processed your request."),
        insights: data.insights || [],
        data: data.data || [],
        sql: data.sql
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { type: "error", content: err.message }]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "dashboard" && !insights) fetchInsights();
  }, [activeTab]);

  const fetchInsights = async () => {
    setInsightsLoading(true);
    try {
      const resp = await fetch("http://localhost:8000/insights");
      const data = await resp.json();
      setInsights(data);
    } catch (err) {
      console.error(err);
    } finally {
      setInsightsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen bg-[var(--bg-primary)] text-[var(--text-primary)] font-sans transition-colors duration-300">
      {/* Sidebar */}
      <aside className="w-72 border-r border-[var(--border-color)]/60 bg-[var(--bg-secondary)]/80 backdrop-blur-3xl sidebar-gradient flex flex-col pt-10 shrink-0 h-full relative z-20">
        <div className="px-8 mb-12 flex items-center justify-between">
          <div className="flex items-center gap-4 group cursor-default">
            <div className="w-10 h-10 bg-gradient-to-br from-[var(--accent-blue)] to-blue-700 rounded-2xl flex items-center justify-center text-[14px] font-black text-white shadow-2xl shadow-blue-500/20 glow-card transition-saas group-hover:scale-110 group-hover:rotate-3">
              SB
            </div>
            <div>
              <h1 className="text-lg font-black tracking-[-0.03em] bg-gradient-to-r from-[var(--text-primary)] via-[var(--text-primary)] to-[var(--text-secondary)] bg-clip-text text-transparent">
                SalonBraine
              </h1>
            </div>
          </div>
          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-xl hover:bg-[var(--surface-hover)] text-[var(--text-secondary)] transition-saas border border-transparent hover:border-[var(--border-color)] group"
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme === 'dark' ? (
              <svg className="w-4.5 h-4.5 group-hover:rotate-45 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v1m0 16v1m9-9h-1M4 11H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M16.95 16.95l.707.707M7.05 7.05l.707.707M12 8a4 4 0 100 8 4 4 0 000-8z" /></svg>
            ) : (
              <svg className="w-4.5 h-4.5 group-hover:-rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
            )}
          </button>
        </div>

        <nav className="flex-1 px-3 space-y-6 overflow-y-auto">
          <div>
            <SectionHeader title="Analytics" />
            <div className="space-y-1">
              <NavButton active={activeTab === "chat"} onClick={() => setActiveTab("chat")} icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>}>
                Query Assistant
              </NavButton>
              <NavButton active={activeTab === "dashboard"} onClick={() => setActiveTab("dashboard")} icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>}>
                Executive Overview
              </NavButton>
            </div>
          </div>

          <div>
            <SectionHeader title="Revenue" />
            <div className="space-y-1">
              <button onClick={() => { setActiveTab("chat"); askQuestion("Show revenue trend for last 6 months"); }} className="w-full text-left px-3 py-1.5 rounded-md text-[13px] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-saas">Monthly Performance</button>
              <button onClick={() => { setActiveTab("chat"); askQuestion("Show top 5 services by revenue"); }} className="w-full text-left px-3 py-1.5 rounded-md text-[13px] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-saas">Service Valuation</button>
            </div>
          </div>

          <div>
            <SectionHeader title="Inventory" />
            <div className="space-y-1">
              <button onClick={() => { setActiveTab("chat"); askQuestion("Which products are low on stock?"); }} className="w-full text-left px-3 py-1.5 rounded-md text-[13px] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-saas">Low Stock Alerts</button>
              <button onClick={() => { setActiveTab("chat"); askQuestion("Which products have never been sold?"); }} className="w-full text-left px-3 py-1.5 rounded-md text-[13px] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-saas">Dormant Inventory</button>
            </div>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 bg-[var(--bg-primary)] relative">
        <header className="h-16 border-b border-[var(--border-color)]/60 flex items-center px-10 bg-[var(--bg-secondary)]/50 backdrop-blur-2xl sticky top-0 z-10 shrink-0">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
              <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping opacity-20" />
            </div>
            <span className="text-[10px] font-black uppercase tracking-[0.4em] text-[var(--text-secondary)] opacity-70">
              {activeTab === "chat" ? "Business Intelligence" : "Executive Overview"}
            </span>
          </div>
        </header>

        {activeTab === "chat" ? (
          <>
            <div className="flex-1 overflow-y-auto px-6 py-8">
              <div className="max-w-4xl mx-auto space-y-10">
                {messages.map((msg, idx) => (
                  <div key={idx} className="flex flex-col gap-1 animate-fade-in group">
                    <div className={`p-6 rounded-3xl ${msg.type === 'user'
                      ? 'bg-gradient-to-br from-[var(--accent-blue)] to-blue-600 text-white self-end max-w-[80%] shadow-2xl shadow-blue-500/10 border border-white/10'
                      : 'bg-transparent border-transparent max-w-none px-0'
                      }`}>
                      {/* Show user content always, show bot content only if no data/insights or if specifically desired */}
                      {msg.content && (msg.type === 'user' || (!msg.data?.length && !msg.insights?.length)) && (
                        <div className={`${msg.type !== 'user' ? 'premium-card glass p-8 border-[var(--border-color)]/30 shadow-2xl' : ''}`}>
                          {msg.type !== 'user' && (
                            <div className="flex items-center gap-2 mb-4 opacity-70">
                              <div className="w-1.5 h-1.5 rounded-full bg-[var(--accent-blue)] shadow-[0_0_8px_var(--accent-blue)]" />
                              <span className="text-[9px] font-black uppercase tracking-[0.3em] text-[var(--text-primary)]">Analysis Summary</span>
                            </div>
                          )}
                          <p className={`text-[16px] leading-[1.6] ${msg.type === 'user' ? 'text-white font-semibold' : 'text-[var(--text-primary)] font-medium italic'}`}>
                            {msg.type === 'user' ? msg.content : `"${msg.content}"`}
                          </p>
                        </div>
                      )}

                      <div className="space-y-10">
                        {msg.insights && msg.insights.length > 0 && (
                          <div className="space-y-6 pt-4">
                            <div className="flex items-center gap-3 px-1">
                              <div className="w-2 h-6 bg-[var(--accent-blue)] rounded-full shadow-[0_0_15px_var(--accent-blue)]" />
                              <h4 className="text-[11px] font-black uppercase tracking-[0.4em] text-[var(--text-primary)]">
                                Intelligence Report
                              </h4>
                            </div>
                            <div className="grid gap-4">
                              {msg.insights.map((insight, i) => (
                                <div key={i} className="flex gap-5 p-5 rounded-3xl glass shadow-2xl border border-white/5 group/insight hover:border-[var(--accent-blue)]/50 transition-saas animate-fade-in" style={{ animationDelay: `${i * 0.1}s` }}>
                                  <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[var(--bg-tertiary)] to-[var(--bg-secondary)] flex items-center justify-center text-[var(--accent-blue)] shrink-0 font-black text-sm ring-1 ring-[var(--accent-blue)]/20 shadow-xl group-hover/insight:scale-110 transition-transform">
                                    {i + 1}
                                  </div>
                                  <div className="pt-1">
                                    <p className="text-[15px] text-[var(--text-primary)] leading-[1.6] font-medium">{insight}</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {msg.data && msg.data.length > 0 && (
                          <div className="animate-fade-in [animation-delay:0.2s]">
                            <DataTable data={msg.data} />
                            <DataVisualizer data={msg.data} />
                          </div>
                        )}
                      </div>

                      {msg.type === 'error' && (
                        <div className="p-4 bg-red-900/10 border border-red-500/20 rounded-xl text-red-400 text-sm flex items-center gap-3">
                          <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                          <span>{msg.content}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="flex flex-col gap-2">
                    <div className="text-[11px] font-bold uppercase tracking-widest text-[var(--text-secondary)]">Processing Analysis</div>
                    <div className="flex gap-1.5 px-1 py-2">
                      <div className="w-2 h-2 rounded-full bg-[var(--accent-blue)] animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-2 h-2 rounded-full bg-[var(--accent-blue)] animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-2 h-2 rounded-full bg-[var(--accent-blue)] animate-bounce"></div>
                    </div>
                  </div>
                )}
                <div ref={scrollRef} />
              </div>
            </div>

            <footer className="p-10 border-t border-[var(--border-color)]/60 bg-[var(--bg-secondary)]/50 backdrop-blur-2xl">
              <div className="max-w-5xl mx-auto flex items-center gap-5">
                <div className="relative flex-1 group">
                  <div className="absolute inset-0 bg-blue-500/10 blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity rounded-3xl" />
                  <input
                    type="text"
                    autoFocus
                    className="w-full relative z-10 bg-[var(--bg-tertiary)]/50 text-[var(--text-primary)] border border-[var(--border-color)] rounded-2xl px-6 py-4.5 text-sm focus:outline-none focus:border-[var(--accent-blue)] focus:ring-8 focus:ring-[var(--accent-blue)]/5 transition-saas placeholder:text-[var(--text-secondary)]/50 shadow-inner font-medium backdrop-blur-sm"
                    placeholder="Ask about revenue trends, low stock, or high-value services..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && askQuestion()}
                    disabled={loading}
                  />
                  <div className="absolute right-6 top-1/2 -translate-y-1/2 flex items-center gap-2 text-[var(--text-secondary)] opacity-40 group-focus-within:opacity-80 transition-saas z-10 pointer-events-none">
                    <span className="text-[9px] font-black border border-[var(--text-secondary)]/20 px-2 py-1 rounded-md bg-[var(--bg-secondary)] shadow-sm">RETURN</span>
                  </div>
                </div>
                <button
                  onClick={() => askQuestion()}
                  disabled={loading || !question.trim()}
                  className="btn-premium flex items-center gap-3 h-[56px] px-8 rounded-2xl shadow-2xl group shadow-blue-500/20"
                >
                  {loading ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 5l7 7-7 7M5 5l7 7-7 7" /></svg>
                  )}
                  <span className="font-black uppercase tracking-widest text-[11px]">Execute</span>
                </button>
              </div>
            </footer>
          </>
        ) : (
          <div className="flex-1 overflow-y-auto px-10 py-8">
            <div className="max-w-6xl mx-auto space-y-10">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold">Executive Overview</h2>
                  <p className="text-sm text-[var(--text-secondary)]">Real-time business performance and anomalies.</p>
                </div>
                <button onClick={fetchInsights} className="px-3 py-1.5 border border-[var(--border-color)] rounded text-xs font-semibold hover:bg-[var(--surface-hover)] transition-saas">
                  Refresh Data
                </button>
              </div>

              {(insightsLoading || !insights) ? (
                <div className="h-64 flex flex-col items-center justify-center gap-3 text-[var(--text-secondary)]">
                  <div className="w-5 h-5 border-2 border-[var(--accent-blue)] border-t-transparent rounded-full animate-spin" />
                  <span className="text-xs uppercase tracking-widest font-bold">Synchronizing...</span>
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="p-6 premium-card animate-fade-in [animation-delay:0.1s] group">
                      <div className="flex items-center justify-between mb-6">
                        <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center text-emerald-500 group-hover:scale-110 transition-saas shadow-inner border border-emerald-500/10">
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="text-[10px] font-black text-emerald-500 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20 uppercase tracking-tighter">+12.5%</span>
                        </div>
                      </div>
                      <p className="text-[10px] uppercase font-black text-[var(--text-secondary)] tracking-[0.2em] mb-2 opacity-60">Total Revenue</p>
                      <p className="text-3xl font-black tracking-[-0.03em] flex items-baseline gap-1">
                        <span className="text-[var(--text-primary)]">${Number(insights?.metrics?.revenue || 0)?.toLocaleString()}</span>
                        <span className="text-sm font-bold text-[var(--text-secondary)] opacity-50">USD</span>
                      </p>
                    </div>

                    <div className="p-6 premium-card animate-fade-in [animation-delay:0.2s] group">
                      <div className="flex items-center justify-between mb-6">
                        <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-500 group-hover:scale-110 transition-saas shadow-inner border border-blue-500/10">
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg>
                        </div>
                        <span className="text-[10px] font-black text-blue-500 bg-blue-500/10 px-2.5 py-1 rounded-lg border border-blue-500/20 uppercase tracking-tighter">Healthy</span>
                      </div>
                      <p className="text-[10px] uppercase font-black text-[var(--text-secondary)] tracking-[0.2em] mb-2 opacity-60">Volume</p>
                      <p className="text-3xl font-black tracking-[-0.03em] font-mono">
                        {Number(insights?.metrics?.transactions || 0)?.toLocaleString()}
                      </p>
                    </div>

                    <div className="p-6 premium-card animate-fade-in [animation-delay:0.3s] group">
                      <div className="flex items-center justify-between mb-6">
                        <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-500 group-hover:scale-110 transition-saas shadow-inner border border-indigo-500/10">
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
                        </div>
                        <span className="text-[10px] font-black text-green-500 bg-green-500/10 px-2.5 py-1 rounded-lg border border-green-500/20 uppercase tracking-tighter">Accelerated</span>
                      </div>
                      <p className="text-[10px] uppercase font-black text-[var(--text-secondary)] tracking-[0.2em] mb-2 opacity-60">Net Profit</p>
                      <p className="text-3xl font-black tracking-[-0.03em] text-emerald-500">
                        ${Number(insights?.metrics?.profit || 0)?.toLocaleString()}
                      </p>
                    </div>

                    <div className="p-6 premium-card animate-fade-in [animation-delay:0.4s] group">
                      <div className="flex items-center justify-between mb-6">
                        <div className="w-12 h-12 rounded-2xl bg-amber-500/10 flex items-center justify-center text-amber-500 group-hover:scale-110 transition-saas shadow-inner border border-amber-500/10">
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                        </div>
                        <span className="text-[10px] font-black text-amber-500 bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/20 uppercase tracking-tighter">Critical</span>
                      </div>
                      <p className="text-[10px] uppercase font-black text-[var(--text-secondary)] tracking-[0.2em] mb-2 opacity-60">Active Anomalies</p>
                      <p className="text-3xl font-black tracking-[-0.03em] text-amber-500">
                        {insights?.anomalies?.length || 0}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="space-y-4">
                      <SectionHeader title="Category Performance" />
                      <div className="h-72 p-4 border border-[var(--border-color)] rounded-md bg-[var(--bg-secondary)]">
                        <Bar
                          data={{
                            labels: insights.top_services.map(s => s.service_name),
                            datasets: [{
                              label: 'Revenue',
                              data: insights.top_services.map(s => s.total_revenue),
                              backgroundColor: '#2F81F7',
                              borderRadius: 4
                            }]
                          }}
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { display: false } },
                            scales: {
                              y: { ticks: { color: 'var(--text-secondary)', font: { size: 10 } }, grid: { color: 'var(--border-color)' }, border: { display: false } },
                              x: { ticks: { color: 'var(--text-secondary)', font: { size: 10 } }, grid: { display: false }, border: { display: false } },
                            }
                          }}
                        />
                      </div>
                    </div>

                    <div className="space-y-4">
                      <SectionHeader title="Top Valuation Accounts" />
                      <div className="premium-card overflow-hidden">
                        <table className="w-full text-[13px] text-left">
                          <thead className="bg-[var(--bg-tertiary)]/50 text-[10px] font-bold text-[var(--text-secondary)] uppercase tracking-wider border-b border-[var(--border-color)]">
                            <tr>
                              <th className="px-5 py-3">Account Reference</th>
                              <th className="px-5 py-3 text-right">Lifetime Valuation</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[var(--border-color)]">
                            {insights?.top_customers?.map((c, i) => (
                              <tr key={i} className="hover:bg-[var(--accent-blue)]/[0.04] transition-saas group">
                                <td className="px-5 py-4 font-semibold text-[var(--text-primary)] group-hover:text-[var(--accent-blue)] transition-saas">{c.customer_name}</td>
                                <td className="px-5 py-4 text-right font-bold text-[var(--accent-blue)] shadow-sm">${Number(c.total_spent).toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-6">
                    <div className="space-y-6">
                      <SectionHeader title="Inventory Intelligence" />
                      <div className="space-y-4">
                        {insights?.anomalies?.map((a, i) => (
                          <div key={i} className="flex items-center justify-between p-5 premium-card group animate-fade-in border-l-4 border-l-amber-500/50" style={{ animationDelay: `${0.1 * i}s` }}>
                            <div className="flex items-center gap-4">
                              <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-600 transition-saas group-hover:scale-110">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>
                              </div>
                              <div>
                                <span className="font-bold text-sm block mb-0.5">{a.name}</span>
                                <span className="text-[10px] text-[var(--text-secondary)] opacity-60 uppercase font-black tracking-widest">{a.issue}</span>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-[9px] px-3 py-1.5 border border-amber-500/20 text-amber-500 bg-amber-500/10 rounded-xl uppercase font-black tracking-[0.1em]">Requires Attention</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-6">
                      <SectionHeader title="Retention Risk Analysis" />
                      <div className="space-y-4">
                        {insights?.churn_risk?.map((c, i) => (
                          <div key={i} className="flex items-center justify-between p-5 premium-card group animate-fade-in border-l-4 border-l-red-500/50" style={{ animationDelay: `${0.1 * i}s` }}>
                            <div className="flex items-center gap-4">
                              <div className="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center text-red-600 transition-saas group-hover:scale-110">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                              </div>
                              <div>
                                <span className="font-bold text-sm block mb-0.5">{c.customer_name}</span>
                                <span className="text-[10px] text-[var(--text-secondary)] opacity-60 uppercase font-black tracking-widest">High Risk Member</span>
                              </div>
                            </div>
                            <span className="text-[9px] text-red-500 font-black bg-red-500/10 px-3 py-1.5 rounded-xl border border-red-500/20 uppercase tracking-widest">
                              Inactive Since: {new Date(c.last_visit).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </main>

      <style>{`
        @keyframes loading {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
}
