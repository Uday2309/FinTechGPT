import { useEffect, useState } from 'react'
import { BarChart3, Bot, FileText, LayoutDashboard, LogOut, PiggyBank, ReceiptIndianRupee, WalletCards } from 'lucide-react'
import api from './lib/api'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import Investments from './pages/Investments'
import Budgets from './pages/Budgets'
import Documents from './pages/Documents'
import Chat from './pages/Chat'
import Login from './pages/Login'

const nav = [
  ['dashboard', 'Dashboard', LayoutDashboard],
  ['transactions', 'Transactions', ReceiptIndianRupee],
  ['budgets', 'Budgets', PiggyBank],
  ['investments', 'Investments', WalletCards],
  ['documents', 'Documents', FileText],
  ['chat', 'FinTechGPT', Bot],
]

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('fintechgpt_token'))
  const [page, setPage] = useState('dashboard')

  useEffect(() => {
    const handler = () => setToken(localStorage.getItem('fintechgpt_token'))
    window.addEventListener('storage', handler)
    return () => window.removeEventListener('storage', handler)
  }, [])

  if (!token) return <Login onLogin={(t) => { localStorage.setItem('fintechgpt_token', t); setToken(t) }} />

  const logout = () => { localStorage.removeItem('fintechgpt_token'); setToken(null) }
  const Current = { dashboard: Dashboard, transactions: Transactions, budgets: Budgets, investments: Investments, documents: Documents, chat: Chat }[page]

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-dot">₹</div><div><strong>FinTechGPT</strong><small>Personal Finance AI</small></div></div>
        <nav>{nav.map(([id, label, Icon]) => <button className={page === id ? 'nav-item active' : 'nav-item'} onClick={() => setPage(id)} key={id}><Icon size={18}/><span>{label}</span></button>)}</nav>
        <button className="logout" onClick={logout}><LogOut size={18}/> Logout</button>
      </aside>
      <main className="main"><Current go={setPage}/></main>
    </div>
  )
}
