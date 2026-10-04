import { useState } from 'react'
import api from '../lib/api'

export default function Login({ onLogin }) {
  const [register, setRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const submit = async (e) => {
    e.preventDefault(); setError('')
    try {
      const url = register ? '/auth/register' : '/auth/login'
      const { data } = await api.post(url, { email, password })
      onLogin(data.access_token)
    } catch (err) { setError(err.response?.data?.detail || 'Request failed') }
  }
  return <div className="auth-screen"><div className="auth-card"><div className="brand large"><div className="brand-dot">₹</div><div><strong>FinTechGPT</strong><small>Your private financial cockpit</small></div></div><h1>{register ? 'Create account' : 'Welcome back'}</h1><p className="muted">Your AI runs locally through Ollama. No paid AI key required.</p><form onSubmit={submit}><input placeholder="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} required/><input placeholder="Password (8+ chars)" type="password" value={password} onChange={e => setPassword(e.target.value)} minLength={8} required/><button className="primary full">{register ? 'Create account' : 'Sign in'}</button></form>{error && <div className="error">{error}</div>}<button className="link-btn" onClick={() => setRegister(!register)}>{register ? 'Already have an account? Sign in' : 'Create a new local account'}</button></div></div>
}
