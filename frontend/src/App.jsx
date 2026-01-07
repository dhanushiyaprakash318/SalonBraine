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
  <h3 className="text-[12px] font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-3 px-3">
    {title}
  </h3>
);

const NavButton = ({ active, onClick, icon, children }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-saas group ${active
      ? "bg-[var(--bg-tertiary)] text-[var(--accent-blue)]"
      : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)]"
      }`}
  >
    <div className={`shrink-0 ${active ? "text-[var(--accent-blue)]" : "text-[var(--text-secondary)] group-hover:text-[var(--text-primary)]"}`}>
      {icon}
    </div>
    {children}
  </button>
);

const DataTable = ({ data }) => {
  if (!data || data.length === 0) return null;
  const keys = Object.keys(data[0]);

  return (
    <div className="mt-4 border border-[var(--border-color)] rounded-md overflow-hidden bg-[var(--bg-secondary)]">
      <div className="overflow-x-auto max-h-[400px]">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="bg-[var(--bg-tertiary)] border-b border-[var(--border-color)] sticky top-0 z-10">
              {keys.map(key => (
                <th key={key} className="px-4 py-2.5 font-semibold text-[var(--text-secondary)] uppercase tracking-tight whitespace-nowrap">
                  {key.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border-color)]">
            {data.slice(0, 100).map((row, i) => (
              <tr key={i} className="hover:bg-[var(--surface-hover)] transition-saas">
                {Object.values(row).map((val, j) => (
                  <td key={j} className="px-4 py-2.5 whitespace-nowrap text-[var(--text-primary)]">
                    {val === null ? '-' : String(val)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-4 py-2 bg-[var(--bg-tertiary)] text-[11px] text-[var(--text-secondary)] border-t border-[var(--border-color)] flex justify-between">
        <span>{data.length} entries found</span>
        {data.length > 100 && <span>Showing first 100 entries</span>}
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
  const labelKey = keys.find(key => typeof data[0][key] === 'string') || keys[0];

  if (numericKeys.length === 0) return null;

  const chartData = {
    labels: data.map(row => row[labelKey]),
    datasets: numericKeys.map((key, index) => ({
      label: key.replace(/_/g, ' '),
      data: data.map(row => Number(row[key]) || 0),
      backgroundColor: index === 0 ? '#2F81F7' : '#1F6FEB',
      borderRadius: 4,
    })),
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: numericKeys.length > 1,
        position: 'top',
        labels: { color: 'var(--text-secondary)', boxWidth: 10, font: { size: 11 } }
      },
      tooltip: {
        padding: 8,
        backgroundColor: 'var(--bg-tertiary)',
        titleColor: 'var(--text-primary)',
        bodyColor: 'var(--text-secondary)',
        borderColor: 'var(--border-color)',
        borderWidth: 1
      }
    },
    scales: {
      y: { ticks: { color: 'var(--text-secondary)', font: { size: 10 } }, grid: { color: 'var(--border-color)' }, border: { display: false } },
      x: { ticks: { color: 'var(--text-secondary)', font: { size: 10 } }, grid: { display: false }, border: { display: false } },
    },
  };

  return (
    <div className="mt-6">
      <h4 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-widest mb-3">Visualization Overview</h4>
      <div className="h-64 border border-[var(--border-color)] p-4 rounded-md bg-[var(--bg-secondary)]">
        <Bar options={options} data={chartData} />
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
      <aside className="w-64 border-r border-[var(--border-color)] bg-[var(--bg-secondary)] flex flex-col pt-6 shrink-0 h-full">
        <div className="px-6 mb-8 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-[var(--accent-blue)] rounded flex items-center justify-center text-[10px] font-bold text-white">SG</div>
            <h1 className="text-sm font-bold tracking-tight">SalonGenius</h1>
          </div>
          <button
            onClick={toggleTheme}
            className="p-1.5 rounded-md hover:bg-[var(--surface-hover)] text-[var(--text-secondary)] transition-saas"
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme === 'dark' ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v1m0 16v1m9-9h-1M4 11H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M16.95 16.95l.707.707M7.05 7.05l.707.707M12 8a4 4 0 100 8 4 4 0 000-8z" /></svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
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
      <main className="flex-1 flex flex-col min-w-0 bg-[var(--bg-primary)]">
        <header className="h-12 border-b border-[var(--border-color)] flex items-center px-6 bg-[var(--bg-secondary)] shrink-0">
          <span className="text-xs font-semibold uppercase tracking-widest text-[var(--text-secondary)]">
            {activeTab === "chat" ? "Analysis Session" : "Executive Dashboard"}
          </span>
        </header>

        {activeTab === "chat" ? (
          <>
            <div className="flex-1 overflow-y-auto px-6 py-8">
              <div className="max-w-4xl mx-auto space-y-10">
                {messages.map((msg, idx) => (
                  <div key={idx} className="flex flex-col gap-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
                    <div className={`text-[11px] font-bold uppercase tracking-widest ${msg.type === 'user' ? 'text-[var(--accent-blue)] self-end' : 'text-[var(--text-secondary)]'}`}>
                      {msg.type === 'user' ? 'Client Request' : 'Analyst Output'}
                    </div>

                    <div className={`p-4 rounded-md border ${msg.type === 'user'
                      ? 'bg-[var(--bg-tertiary)] border-[var(--border-color)] self-end max-w-[80%]'
                      : 'bg-transparent border-transparent max-w-none px-0'
                      }`}>
                      {msg.content && <p className="text-[14px] leading-relaxed text-[var(--text-primary)]">{msg.content}</p>}

                      <div className="space-y-8">
                        {msg.insights && msg.insights.length > 1 && (
                          <div className="space-y-3">
                            <h4 className="text-[10px] font-bold uppercase tracking-widest text-[var(--accent-blue)]">Key Insights</h4>
                            <div className="grid gap-2">
                              {msg.insights.map((insight, i) => (
                                <div key={i} className="flex gap-3 p-3 rounded-md bg-[var(--bg-tertiary)] border border-[var(--border-color)]">
                                  <div className="w-1.5 h-1.5 rounded-full bg-[var(--accent-blue)] mt-1.5 shrink-0" />
                                  <p className="text-sm text-[var(--text-primary)]">{insight}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {msg.sql && (
                          <div className="space-y-2">
                            <h4 className="text-[10px] font-bold uppercase tracking-widest text-[var(--text-secondary)]">Technical Query</h4>
                            <code className="block p-3 rounded bg-[var(--bg-tertiary)] text-[11px] text-[var(--accent-blue)] font-mono border border-[var(--border-color)] overflow-x-auto whitespace-pre">
                              {msg.sql}
                            </code>
                          </div>
                        )}

                        {msg.data && msg.data.length > 0 && (
                          <>
                            <DataTable data={msg.data} />
                            <DataVisualizer data={msg.data} />
                          </>
                        )}
                      </div>

                      {msg.type === 'error' && (
                        <div className="p-3 bg-red-900/10 border border-red-500/20 rounded-md text-red-400 text-xs flex items-center gap-2">
                          <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                          {msg.content}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="flex flex-col gap-2">
                    <div className="text-[11px] font-bold uppercase tracking-widest text-[var(--text-secondary)]">Analyst Thinking</div>
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

            <footer className="p-6 border-t border-[var(--border-color)] bg-[var(--bg-secondary)]">
              <div className="max-w-4xl mx-auto flex items-center gap-3">
                <input
                  type="text"
                  autoFocus
                  className="flex-1 bg-[var(--bg-tertiary)] text-[var(--text-primary)] border border-[var(--border-color)] rounded-md px-4 py-2.5 text-sm focus:outline-none focus:border-[var(--accent-blue)] transition-saas placeholder:text-[var(--text-secondary)]"
                  placeholder="Query specialized salon metrics..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && askQuestion()}
                  disabled={loading}
                />
                <button
                  onClick={() => askQuestion()}
                  disabled={loading || !question.trim()}
                  className="px-4 py-2.5 bg-[var(--accent-blue)] hover:bg-[var(--accent-muted)] disabled:opacity-50 text-white rounded-md text-sm font-semibold transition-saas shrink-0"
                >
                  Run Query
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
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="p-4 border border-[var(--border-color)] rounded-md bg-[var(--bg-secondary)]">
                      <p className="text-[10px] uppercase font-bold text-[var(--text-secondary)] tracking-wider mb-1">Total Revenue</p>
                      <p className="text-xl font-bold">${Number(insights?.metrics?.revenue || 0)?.toLocaleString()}</p>
                    </div>
                    <div className="p-4 border border-[var(--border-color)] rounded-md bg-[var(--bg-secondary)]">
                      <p className="text-[10px] uppercase font-bold text-[var(--text-secondary)] tracking-wider mb-1">Transactions</p>
                      <p className="text-xl font-bold">{Number(insights?.metrics?.transactions || 0)?.toLocaleString()}</p>
                    </div>
                    <div className="p-4 border border-[var(--border-color)] rounded-md bg-[var(--bg-secondary)]">
                      <p className="text-[10px] uppercase font-bold text-green-500 tracking-wider mb-1">Net Profit</p>
                      <p className="text-xl font-bold text-green-400">${Number(insights?.metrics?.profit || 0)?.toLocaleString()}</p>
                    </div>
                    <div className="p-4 border border-[var(--border-color)] rounded-md bg-[var(--bg-secondary)]">
                      <p className="text-[10px] uppercase font-bold text-yellow-500 tracking-wider mb-1">Stock Anomalies</p>
                      <p className="text-xl font-bold text-yellow-400">{insights?.anomalies?.length || 0}</p>
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
                      <div className="border border-[var(--border-color)] rounded-md overflow-hidden">
                        <table className="w-full text-xs text-left">
                          <thead className="bg-[var(--bg-tertiary)] text-[var(--text-secondary)] uppercase">
                            <tr>
                              <th className="px-4 py-3">Account</th>
                              <th className="px-4 py-3 text-right">Lifetime Spent</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[var(--border-color)]">
                            {insights?.top_customers?.map((c, i) => (
                              <tr key={i} className="hover:bg-[var(--surface-hover)] transition-saas">
                                <td className="px-4 py-3 font-medium">{c.customer_name}</td>
                                <td className="px-4 py-3 text-right font-bold text-[var(--accent-blue)]">${Number(c.total_spent).toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-4">
                    <div className="space-y-4">
                      <SectionHeader title="Inventory Alerts" />
                      <div className="space-y-2">
                        {insights?.anomalies?.map((a, i) => (
                          <div key={i} className="flex items-center justify-between p-3 border border-[var(--border-color)] rounded-md bg-[var(--bg-secondary)] text-sm">
                            <span className="font-medium">{a.name}</span>
                            <span className="text-[10px] px-2 py-0.5 border border-yellow-500/20 text-yellow-500 rounded uppercase font-bold">{a.issue}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-4">
                      <SectionHeader title="Customer Churn Alerts" />
                      <div className="space-y-2">
                        {insights?.churn_risk?.map((c, i) => (
                          <div key={i} className="flex items-center justify-between p-3 border border-[var(--border-color)] rounded-md bg-[var(--bg-secondary)] text-sm">
                            <span className="font-medium">{c.customer_name}</span>
                            <span className="text-xs text-red-500 font-medium">Inactive since {new Date(c.last_visit).toLocaleDateString()}</span>
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
