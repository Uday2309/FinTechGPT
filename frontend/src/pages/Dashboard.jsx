import { useEffect, useState } from 'react'
import { ArrowUpRight, CircleDollarSign, PieChart, TrendingDown, TrendingUp } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import api from '../lib/api'

const money = (n) => `₹${Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
export default function Dashboard({ go }) {
  const [data, setData] = useState(null)
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7))
  useEffect(() => { api.get('/dashboard', { params: { month } }).then(r => setData(r.data)).catch(() => {}) }, [month])
  if (!data) return <section><Header title="Dashboard" subtitle="Your financial command center"/><div className="card">Loading…</div></section>
  const trend = data.category_breakdown.slice(0, 7)
  return <section><Header title="Dashboard" subtitle="Your financial command center"><input className="month-picker" type="month" value={month} onChange={e => setMonth(e.target.value)}/></Header><div className="kpi-grid"><Kpi title="Income" value={money(data.income)} icon={<TrendingUp size={20}/>} /><Kpi title="Expenses" value={money(data.expenses)} icon={<TrendingDown size={20}/>} /><Kpi title="Net cash flow" value={money(data.net_cash_flow)} icon={<CircleDollarSign size={20}/>} /><Kpi title="Portfolio" value={money(data.portfolio.current_value)} icon={<PieChart size={20}/>} /></div><div className="grid-2"><div className="card"><div className="card-head"><div><h3>Spending by category</h3><span className="muted">Current month vs previous month</span></div></div><div style={{height: 330}}><ResponsiveContainer><BarChart data={trend}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="category"/><YAxis/><Tooltip formatter={v => money(v)}/><Bar dataKey="current" name="Current"/><Bar dataKey="previous" name="Previous"/></BarChart></ResponsiveContainer></div></div><div className="card"><div className="card-head"><div><h3>AI-ready snapshot</h3><span className="muted">The assistant sees calculated facts, not raw credentials.</span></div></div><div className="snapshot"><div><span>Savings rate</span><strong>{data.savings_rate == null ? '—' : `${data.savings_rate.toFixed(1)}%`}</strong></div><div><span>Invested</span><strong>{money(data.portfolio.invested)}</strong></div><div><span>Portfolio P/L</span><strong className={data.portfolio.profit_loss >= 0 ? 'positive' : 'negative'}>{money(data.portfolio.profit_loss)}</strong></div></div><button className="primary" onClick={() => go('chat')}>Ask FinTechGPT <ArrowUpRight size={16}/></button></div></div></section>
}
function Header({title,subtitle,children}) { return <div className="header"><div><h1>{title}</h1><p>{subtitle}</p></div><div>{children}</div></div> }
function Kpi({title,value,icon}) { return <div className="kpi card"><div className="kpi-icon">{icon}</div><span>{title}</span><strong>{value}</strong></div> }
