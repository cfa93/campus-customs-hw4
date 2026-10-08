import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

// React Router keeps the old scroll position between pages. Reset it so a
// product page opens at the top, with the big picture in view.
export default function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  return null
}
