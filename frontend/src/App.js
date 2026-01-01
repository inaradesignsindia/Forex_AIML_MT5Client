import React, { useState, useEffect } from 'react';
import { LayoutDashboard, Package, Settings, TrendingUp, AlertCircle, FileText, Menu, X, DollarSign, CheckCircle, ShoppingCart, Link, Coins } from 'lucide-react';
import axios from 'axios';

// --- CONFIGURATION ---
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// --- BRANDING ---
const BRAND = {
  primary: "bg-purple-600",
  primaryHover: "hover:bg-purple-700",
  primaryText: "text-purple-700",
  light: "bg-purple-50",
  accent: "text-purple-600",
  gradient: "bg-gradient-to-r from-purple-600 to-purple-800",
  bg: "bg-gray-50",
  card: "bg-white rounded-2xl shadow-xl border-0"
};

// --- UTILITY COMPONENTS ---
const Card = ({ children, className = "" }) => (
  <div className={`${BRAND.card} p-6 ${className}`}>{children}</div>
);

const Button = ({ children, onClick, variant = "primary", icon: Icon, className = "", disabled = false }) => {
  const variants = {
    primary: `${BRAND.primary} text-white ${BRAND.primaryHover} shadow-lg shadow-purple-600/30`,
    secondary: "bg-gray-100 text-gray-700 hover:bg-gray-200",
    danger: "bg-rose-50 text-rose-600 hover:bg-rose-100 border border-rose-200",
    ghost: "text-gray-500 hover:bg-gray-100",
  };
  return (
    <button onClick={onClick} disabled={disabled} className={`flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl font-semibold transition-all active:scale-95 disabled:opacity-50 ${variants[variant]} ${className}`}>
      {Icon && <Icon size={18} />}{children}
    </button>
  );
};

// --- DASHBOARD ---
const Dashboard = ({ liveState }) => {
  const metrics = liveState ? {
    equity: liveState.account?.equity || 0,
    trades: liveState.positions?.length || 0,
    signal: liveState.suggestion || 'N/A',
    confidence: liveState.ai_confidence || 0
  } : { equity: 0, trades: 0, signal: 'N/A', confidence: 0 };

  return (
    <div className="space-y-8 pb-20">
      <div className="flex justify-between items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">Forex AI Dashboard</h2>
          <p className="text-gray-500 mt-1">Real-time trading overview</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className={`${BRAND.gradient} text-white`}>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-purple-100 text-sm font-medium mb-1">Account Equity</p>
              <h3 className="text-3xl font-bold">${metrics.equity.toLocaleString()}</h3>
            </div>
            <div className="p-3 bg-white/20 rounded-xl"><TrendingUp size={24} className="text-white" /></div>
          </div>
        </Card>
        <Card>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm font-medium mb-1">Active Trades</p>
              <h3 className="text-3xl font-bold text-blue-600">{metrics.trades}</h3>
            </div>
            <div className="p-3 bg-blue-100 rounded-xl"><ShoppingCart size={24} className="text-blue-600" /></div>
          </div>
        </Card>
        <Card>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm font-medium mb-1">AI Signal</p>
              <h3 className="text-3xl font-bold text-green-600">{metrics.signal}</h3>
            </div>
            <div className="p-3 bg-green-100 rounded-xl"><CheckCircle size={24} className="text-green-600" /></div>
          </div>
        </Card>
        <Card>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm font-medium mb-1">AI Confidence</p>
              <h3 className="text-3xl font-bold text-purple-600">{metrics.confidence}%</h3>
            </div>
            <div className="p-3 bg-purple-100 rounded-xl"><Coins size={24} className="text-purple-600" /></div>
          </div>
        </Card>
      </div>

      <Card>
        <h3 className="font-bold text-gray-800 mb-6">Recent Activity</h3>
        {liveState?.positions?.length > 0 ? (
          <div className="space-y-4">
            {liveState.positions.slice(0, 5).map((pos, i) => (
              <div key={i} className="flex justify-between items-center p-4 hover:bg-gray-50 rounded-xl border border-transparent hover:border-gray-100 transition-all">
                <div>
                  <p className="font-bold text-gray-800">{pos.symbol}</p>
                  <p className="text-xs text-gray-500">{pos.type} • {pos.volume} lots</p>
                </div>
                <div className="text-right">
                  <div className="font-bold text-gray-800">${pos.price_current?.toFixed(5)}</div>
                  <div className="text-xs text-gray-400">{pos.profit?.toFixed(2)} profit</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No active positions</p>
        )}
      </Card>
    </div>
  );
};

// --- MANUAL TRADE ---
const ManualTrade = ({ onTradeSubmit }) => {
  const [trade, setTrade] = useState({
    symbol: 'EURUSD',
    action: 'buy',
    order_type: 'market',
    volume: 0.1,
    take_profit: 50,
    stop_loss: 30,
    trailing_stop: false,
    price: 0
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onTradeSubmit(trade);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Manual Trade</h2>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-bold text-gray-500 mb-1 block">Symbol</label>
              <select className="w-full p-3 border rounded-xl bg-gray-50" value={trade.symbol} onChange={e => setTrade({...trade, symbol: e.target.value})}>
                <option>EURUSD</option><option>GBPUSD</option><option>USDJPY</option><option>AUDUSD</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-bold text-gray-500 mb-1 block">Order Type</label>
              <select className="w-full p-3 border rounded-xl bg-gray-50" value={trade.order_type} onChange={e => setTrade({...trade, order_type: e.target.value})}>
                <option value="market">Market</option><option value="limit">Limit</option><option value="stop">Stop</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-bold text-gray-500 mb-1 block">Action</label>
              <select className="w-full p-3 border rounded-xl bg-gray-50" value={trade.action} onChange={e => setTrade({...trade, action: e.target.value})}>
                <option value="buy">Buy</option><option value="sell">Sell</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-bold text-gray-500 mb-1 block">Volume</label>
              <input type="number" step="0.01" className="w-full p-3 border rounded-xl bg-gray-50" value={trade.volume} onChange={e => setTrade({...trade, volume: parseFloat(e.target.value)})} />
            </div>
          </div>
          {trade.order_type !== 'market' && (
            <div>
              <label className="text-sm font-bold text-gray-500 mb-1 block">Price</label>
              <input type="number" step="0.00001" className="w-full p-3 border rounded-xl bg-gray-50" value={trade.price} onChange={e => setTrade({...trade, price: parseFloat(e.target.value)})} />
            </div>
          )}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-bold text-gray-500 mb-1 block">Take Profit (pips)</label>
              <input type="number" className="w-full p-3 border rounded-xl bg-gray-50" value={trade.take_profit} onChange={e => setTrade({...trade, take_profit: parseInt(e.target.value)})} />
            </div>
            <div>
              <label className="text-sm font-bold text-gray-500 mb-1 block">Stop Loss (pips)</label>
              <input type="number" className="w-full p-3 border rounded-xl bg-gray-50" value={trade.stop_loss} onChange={e => setTrade({...trade, stop_loss: parseInt(e.target.value)})} />
            </div>
            <div className="flex items-end">
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={trade.trailing_stop} onChange={e => setTrade({...trade, trailing_stop: e.target.checked})} />
                <span className="text-sm font-bold text-gray-500">Trailing Stop</span>
              </label>
            </div>
          </div>
          <Button className="w-full">Place Trade</Button>
        </form>
      </Card>
    </div>
  );
};

// --- MAIN APP ---
function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [liveState, setLiveState] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/live-state`);
        setLiveState(response.data);
      } catch (error) {
        console.error('Error fetching live state:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const handleTradeSubmit = async (trade) => {
    try {
      await axios.post(`${API_BASE}/api/trade`, trade);
      alert('Trade submitted successfully!');
    } catch (error) {
      alert('Error submitting trade: ' + error.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row text-slate-800">
      <div className={`${isMenuOpen ? 'block' : 'hidden'} md:block fixed md:relative z-40 w-full md:w-72 bg-white h-full border-r border-gray-100 flex flex-col shadow-xl`}>
        <div className="p-8 bg-purple-800 text-white hidden md:block">
          <h1 className="text-3xl font-extrabold tracking-wide">FOREX AI</h1>
          <p className="text-purple-200 text-xs mt-1">Trading Platform v1.0</p>
        </div>
        <nav className="flex-1 p-6 space-y-3 overflow-y-auto">
          {[
            { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
            { id: 'trade', icon: ShoppingCart, label: 'Manual Trade' },
            { id: 'settings', icon: Settings, label: 'Settings' },
          ].map(i => (
            <button key={i.id} onClick={() => {setActiveTab(i.id); setIsMenuOpen(false)}} className={`w-full flex items-center gap-4 p-3.5 rounded-xl transition-all font-medium ${activeTab === i.id ? 'bg-purple-50 text-purple-700 shadow-sm' : 'text-gray-500 hover:bg-gray-50 hover:text-purple-600'}`}>
              <i.icon size={20} />{i.label}
            </button>
          ))}
        </nav>
      </div>

      <main className="flex-1 p-6 md:p-10 overflow-auto h-[calc(100vh-60px)] md:h-screen bg-gray-50">
        <div className="md:hidden bg-purple-800 text-white p-4 flex justify-between items-center sticky top-0 z-50 shadow-md mb-6">
          <span className="font-bold text-lg tracking-wide">FOREX AI</span>
          <button onClick={() => setIsMenuOpen(!isMenuOpen)}><Menu/></button>
        </div>

        {activeTab === 'dashboard' && <Dashboard liveState={liveState} />}
        {activeTab === 'trade' && <ManualTrade onTradeSubmit={handleTradeSubmit} />}
        {activeTab === 'settings' && <div className="text-center text-gray-500 mt-20">Settings coming soon...</div>}
      </main>
    </div>
  );
}

export default App;