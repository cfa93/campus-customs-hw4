import { Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar.tsx'
import ChatBox from './components/ChatBox.tsx'
import ScrollToTop from './components/ScrollToTop.tsx'
import Home from './pages/Home.tsx'
import Products from './pages/Products.tsx'
import ProductDetail from './pages/ProductDetail.tsx'
import About from './pages/About.tsx'
import Login from './pages/Login.tsx'
import Signup from './pages/Signup.tsx'
import ResetPassword from './pages/ResetPassword.tsx'
import NotFound from './pages/NotFound.tsx'

export default function App() {
  return (
    <>
      <ScrollToTop />
      <Navbar />
      <main className="page">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:productId" element={<ProductDetail />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <footer className="footer">
        <p>Campus Customs · 57 Broadway, New Haven, CT 06511</p>
        <p className="muted">Officially licensed Yale merchandise</p>
      </footer>
      <ChatBox />
    </>
  )
}
