import React, { useState, useEffect, ReactNode } from 'react';
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  DollarSign,
  Calendar,
  Plus,
  Home,
  CreditCard,
  Lightbulb,
  Settings,
} from 'lucide-react';

// ================== Error Boundary ==================

class ErrorBoundary extends React.Component<{ children: ReactNode }, { error: Error | null }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error, info: any) {
    console.error('Dashboard crashed:', error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: '2rem', fontFamily: 'system-ui' }}>
          <h1 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Something went wrong 💥</h1>
          <p style={{ marginBottom: '0.5rem' }}>
            {this.state.error.message}
          </p>
          <p style={{ fontSize: '0.85rem', color: '#6b7280' }}>
            Check your API responses or field names. This message is coming from the ErrorBoundary in <code>App.tsx</code>.
          </p>
        </div>
      );
    }
    return this.props.children;
  }
}

// ================== Types & API ==================

const API_URL = 'http://localhost:8000/api';

type Severity = 'success' | 'warning' | 'info' | string;

type Transaction = {
  id: number;
  description: string;
  amount: number;
  date: string;
  category: string;
  category_confidence: number;
};

type Insight = {
  title: string;
  description: string;
  severity: Severity;
};

type ForecastPoint = {
  date: string;
  upper: number;
  predicted: number;
  lower: number;
};

type NewTransactionPayload = {
  description: string;
  amount: number;
  date: string;
};

type Page = 'dashboard' | 'transactions' | 'insights' | 'forecast' | 'settings';

const api = {
  getTransactions: async (): Promise<Transaction[]> => {
    const res = await fetch(`${API_URL}/transactions`);
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  },
  createTransaction: async (data: NewTransactionPayload): Promise<Transaction> => {
    const res = await fetch(`${API_URL}/transactions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },
  getInsights: async (): Promise<Insight[]> => {
    const res = await fetch(`${API_URL}/insights`);
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  },
  getForecast: async (): Promise<ForecastPoint[]> => {
    const res = await fetch(`${API_URL}/forecast`);
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  },
};

// ================== Small Reusable Components ==================

type NavButtonProps = {
  icon: React.ComponentType<{ size?: number }>;
  label: string;
  page: Page;
  currentPage: Page;
  onClick: (page: Page) => void;
};

const NavButton: React.FC<NavButtonProps> = ({
  icon: Icon,
  label,
  page,
  currentPage,
  onClick,
}) => (
  <button
    onClick={() => onClick(page)}
    className={`flex items-center gap-3 w-full px-4 py-3 rounded-lg transition-colors ${
      currentPage === page
        ? 'bg-blue-50 text-blue-600 font-medium'
        : 'text-gray-600 hover:bg-gray-50'
    }`}
  >
    <Icon size={20} />
    <span>{label}</span>
  </button>
);

type AddTransactionModalProps = {
  onClose: () => void;
  onAdd: (data: NewTransactionPayload) => Promise<void> | void;
};

const AddTransactionModal: React.FC<AddTransactionModalProps> = ({ onClose, onAdd }) => {
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [type, setType] = useState<'expense' | 'income'>('expense');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!description || !amount) return;

    const numeric = parseFloat(amount);
    if (Number.isNaN(numeric)) return;

    const finalAmount = type === 'expense' ? -Math.abs(numeric) : Math.abs(numeric);

    await onAdd({
      description,
      amount: finalAmount,
      date: new Date(date).toISOString(),
    });

    setDescription('');
    setAmount('');
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Add Transaction</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setType('expense')}
                className={`flex-1 py-2 rounded-lg ${
                  type === 'expense' ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-700'
                }`}
              >
                Expense
              </button>
              <button
                type="button"
                onClick={() => setType('income')}
                className={`flex-1 py-2 rounded-lg ${
                  type === 'income' ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-700'
                }`}
              >
                Income
              </button>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Starbucks Coffee"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Amount</label>
            <input
              type="number"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="0.00"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Add Transaction
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ================== Dashboard App ==================

const DashboardApp: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [forecast, setForecast] = useState<ForecastPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddTransaction, setShowAddTransaction] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [txns, ins, fcst] = await Promise.all([
        api.getTransactions(),
        api.getInsights(),
        api.getForecast(),
      ]);
      setTransactions(Array.isArray(txns) ? txns : []);
      setInsights(Array.isArray(ins) ? ins : []);
      setForecast(Array.isArray(fcst) ? fcst : []);
    } catch (error) {
      console.error('Error loading data:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    void loadData();
  }, []);

  // Metrics with safe fallbacks
  const totalIncome = transactions
    .filter((t) => (t?.amount ?? 0) > 0)
    .reduce((sum, t) => sum + (t.amount ?? 0), 0);

  const totalExpenses = Math.abs(
    transactions
      .filter((t) => (t?.amount ?? 0) < 0)
      .reduce((sum, t) => sum + (t.amount ?? 0), 0)
  );

  const netCashFlow = totalIncome - totalExpenses;
  const currentBalance = 5234.67 + netCashFlow;

  const categoryData = transactions
    .filter((t) => (t?.amount ?? 0) < 0)
    .reduce<Record<string, number>>((acc, t) => {
      const cat = t.category || 'Uncategorized';
      const amt = Math.abs(t.amount ?? 0);
      acc[cat] = (acc[cat] || 0) + amt;
      return acc;
    }, {});

  const categoryChartData = Object.entries(categoryData).map(([name, value]) => ({
    name,
    value: Math.round(value * 100) / 100,
  }));

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444', '#6366f1'];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading your financial data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 p-6 flex flex-col">
        <div className="flex items-center gap-3 mb-8">
          <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
            <DollarSign className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">FinanceAI</h1>
            <p className="text-xs text-gray-500">Smart Money Manager</p>
          </div>
        </div>

        <nav className="space-y-2 flex-1">
          <NavButton
            icon={Home}
            label="Dashboard"
            page="dashboard"
            currentPage={currentPage}
            onClick={setCurrentPage}
          />
          <NavButton
            icon={CreditCard}
            label="Transactions"
            page="transactions"
            currentPage={currentPage}
            onClick={setCurrentPage}
          />
          <NavButton
            icon={Lightbulb}
            label="Insights"
            page="insights"
            currentPage={currentPage}
            onClick={setCurrentPage}
          />
          <NavButton
            icon={TrendingUp}
            label="Forecast"
            page="forecast"
            currentPage={currentPage}
            onClick={setCurrentPage}
          />
          <NavButton
            icon={Settings}
            label="Settings"
            page="settings"
            currentPage={currentPage}
            onClick={setCurrentPage}
          />
        </nav>

        <div className="mt-8 p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg">
          <p className="text-sm font-medium text-gray-900 mb-1">Current Balance</p>
          <p className="text-2xl font-bold text-blue-600">${currentBalance.toFixed(2)}</p>
          <p className="text-xs text-gray-500 mt-2">Updated just now</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {currentPage === 'dashboard' && 'Dashboard'}
                {currentPage === 'transactions' && 'Transactions'}
                {currentPage === 'insights' && 'AI Insights'}
                {currentPage === 'forecast' && 'Cash Flow Forecast'}
                {currentPage === 'settings' && 'Settings'}
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                {currentPage === 'dashboard' && 'Your financial overview'}
                {currentPage === 'transactions' && 'Manage your transactions'}
                {currentPage === 'insights' && 'AI-powered financial insights'}
                {currentPage === 'forecast' && '90-day balance prediction'}
                {currentPage === 'settings' && 'Manage your account'}
              </p>
            </div>
            {currentPage === 'transactions' && (
              <button
                onClick={() => setShowAddTransaction(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus size={18} />
                Add Transaction
              </button>
            )}
          </div>
        </div>

        {/* Page Content */}
        <div className="p-8">
          {/* Dashboard Page */}
          {currentPage === 'dashboard' && (
            <div className="space-y-6">
              {/* Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Current Balance</span>
                    <DollarSign className="text-blue-600" size={20} />
                  </div>
                  <div className="text-3xl font-bold text-gray-900">${currentBalance.toFixed(2)}</div>
                  <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
                    <TrendingUp size={16} />
                    <span>+12.3%</span>
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Income</span>
                    <TrendingUp className="text-green-600" size={20} />
                  </div>
                  <div className="text-3xl font-bold text-gray-900">${totalIncome.toFixed(2)}</div>
                  <div className="text-sm text-gray-500 mt-2">This month</div>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Expenses</span>
                    <TrendingDown className="text-red-600" size={20} />
                  </div>
                  <div className="text-3xl font-bold text-gray-900">${totalExpenses.toFixed(2)}</div>
                  <div className="text-sm text-gray-500 mt-2">This month</div>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Net Cash Flow</span>
                    <Calendar className="text-purple-600" size={20} />
                  </div>
                  <div className={`text-3xl font-bold ${netCashFlow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ${Math.abs(netCashFlow).toFixed(2)}
                  </div>
                  <div className="text-sm text-gray-500 mt-2">{netCashFlow >= 0 ? 'Positive' : 'Negative'}</div>
                </div>
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Spending by Category</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={categoryChartData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(props) => {
                          const name = props.name ?? '';
                          const percent = props.percent ?? 0;
                          return `${name} ${(percent * 100).toFixed(0)}%`;
                        }}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {categoryChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Transactions</h3>
                  <div className="space-y-3">
                    {transactions.slice(0, 5).map((txn) => (
                      <div
                        key={txn.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div>
                          <p className="font-medium text-gray-900">{txn.description}</p>
                          <p className="text-xs text-gray-500">
                            {txn.date ? new Date(txn.date).toLocaleDateString() : ''}
                          </p>
                        </div>
                        <div className="text-right">
                          <p
                            className={`font-semibold ${
                              txn.amount >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}
                          >
                            {txn.amount >= 0 ? '+' : '-'}${Math.abs(txn.amount).toFixed(2)}
                          </p>
                          <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                            {txn.category || 'Uncategorized'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Insights Preview */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {insights.slice(0, 4).map((insight, idx) => (
                    <div
                      key={idx}
                      className={`border rounded-lg p-4 ${
                        insight.severity === 'success'
                          ? 'border-green-200 bg-green-50'
                          : insight.severity === 'warning'
                          ? 'border-orange-200 bg-orange-50'
                          : 'border-blue-200 bg-blue-50'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <AlertTriangle
                          size={20}
                          className={
                            insight.severity === 'success'
                              ? 'text-green-600'
                              : insight.severity === 'warning'
                              ? 'text-orange-600'
                              : 'text-blue-600'
                          }
                        />
                        <div>
                          <h4 className="font-semibold mb-1">{insight.title}</h4>
                          <p className="text-sm opacity-90">{insight.description}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                  {insights.length === 0 && (
                    <p className="text-sm text-gray-500">No insights yet – add some transactions.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Transactions Page */}
          {currentPage === 'transactions' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Description
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Category
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Confidence
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        Amount
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {transactions.map((txn) => (
                      <tr key={txn.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {txn.date ? new Date(txn.date).toLocaleDateString() : ''}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">{txn.description}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                            {txn.category || 'Uncategorized'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {txn.category_confidence != null
                            ? `${(txn.category_confidence * 100).toFixed(0)}%`
                            : '—'}
                        </td>
                        <td
                          className={`px-6 py-4 whitespace-nowrap text-sm text-right font-medium ${
                            txn.amount >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}
                        >
                          {txn.amount >= 0 ? '+' : '-'}${Math.abs(txn.amount).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                    {transactions.length === 0 && (
                      <tr>
                        <td
                          colSpan={5}
                          className="px-6 py-4 text-center text-sm text-gray-500"
                        >
                          No transactions yet.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Insights Page */}
          {currentPage === 'insights' && (
            <div className="space-y-6">
              {insights.map((insight, idx) => (
                <div
                  key={idx}
                  className={`border-l-4 p-6 rounded-r-lg ${
                    insight.severity === 'success'
                      ? 'border-green-500 bg-green-50'
                      : insight.severity === 'warning'
                      ? 'border-orange-500 bg-orange-50'
                      : 'border-blue-500 bg-blue-50'
                  }`}
                >
                  <h4 className="font-semibold text-gray-900 text-lg mb-2">
                    {insight.title}
                  </h4>
                  <p className="text-gray-700">{insight.description}</p>
                </div>
              ))}
              {insights.length === 0 && (
                <p className="text-sm text-gray-500">No insights yet.</p>
              )}
            </div>
          )}

          {/* Forecast Page */}
          {currentPage === 'forecast' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">
                90-Day Cash Flow Forecast
              </h3>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={forecast}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="upper"
                    stroke="#93c5fd"
                    strokeDasharray="5 5"
                    name="Optimistic"
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="predicted"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    name="Predicted"
                  />
                  <Line
                    type="monotone"
                    dataKey="lower"
                    stroke="#93c5fd"
                    strokeDasharray="5 5"
                    name="Conservative"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
              {forecast.length === 0 && (
                <p className="mt-4 text-sm text-gray-500">
                  No forecast data available yet.
                </p>
              )}
            </div>
          )}

          {/* Settings Page */}
          {currentPage === 'settings' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">
                Account Settings
              </h3>
              <p className="text-gray-600">Settings page coming soon...</p>
            </div>
          )}
        </div>
      </div>

      {/* Add Transaction Modal */}
      {showAddTransaction && (
        <AddTransactionModal
          onClose={() => setShowAddTransaction(false)}
          onAdd={async (data) => {
            await api.createTransaction(data);
            await loadData();
            setShowAddTransaction(false);
          }}
        />
      )}
    </div>
  );
};

// Wrap Dashboard in ErrorBoundary so you never see a blank page
const App: React.FC = () => (
  <ErrorBoundary>
    <DashboardApp />
  </ErrorBoundary>
);

export default App;