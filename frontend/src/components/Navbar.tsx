import { NavLink, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth-context.ts'

const mainLinks = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]

const navClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? 'nav-link active' : 'nav-link'

export default function Navbar() {
  const { user, setUser } = useAuth()
  const navigate = useNavigate()

  function logout() {
    setUser(null)
    navigate('/')
  }

  return (
    <header className="navbar">
      <Link to="/" className="brand">
        Campus <span>Customs</span>
      </Link>
      <nav className="nav-main" aria-label="Main">
        {mainLinks.map((link) => (
          <NavLink key={link.to} to={link.to} end={link.end} className={navClass}>
            {link.label}
          </NavLink>
        ))}
      </nav>
      <div className="nav-auth">
        {user ? (
          <>
            <span className="nav-greeting">Hi, {user.first_name ?? user.name}</span>
            <button type="button" className="btn btn-small" onClick={logout}>
              Log out
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login" className={navClass}>
              Log in
            </NavLink>
            <NavLink to="/signup" className="btn btn-small">
              Create account
            </NavLink>
          </>
        )}
      </div>
    </header>
  )
}
