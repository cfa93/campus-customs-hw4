import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { resetPassword } from '../api.ts'
import { useAuth } from '../auth-context.ts'

export default function ResetPassword() {
  const { setUser } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }
    setBusy(true)
    try {
      const user = await resetPassword(email, password)
      setUser(user)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="auth-card">
      <h1>Reset password</h1>
      <p className="muted">Enter your account email and choose a new password.</p>
      <form onSubmit={handleSubmit}>
        <label>
          Email
          <input type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          New password
          <input
            type="password"
            autoComplete="new-password"
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        <label>
          Confirm new password
          <input
            type="password"
            autoComplete="new-password"
            minLength={8}
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
          />
        </label>
        <button type="submit" className="btn" disabled={busy}>
          {busy ? 'Saving…' : 'Set new password'}
        </button>
      </form>
      {error && <p className="notice">{error}</p>}
      <p className="muted">
        Remembered it? <Link to="/login">Log in</Link>
      </p>
    </section>
  )
}
