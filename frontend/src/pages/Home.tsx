import { Link } from 'react-router-dom'
import ChatResults from '../components/ChatResults.tsx'

const categories = [
  {
    title: 'Everyday Yale',
    text: 'Tees, crewnecks, hoodies, quarter-zips and fleece jackets in sizes XS to XXL.',
  },
  {
    title: 'Residential Colleges',
    text: 'Show which college you call home, from Benjamin Franklin and Berkeley to Saybrook and Trumbull.',
  },
  {
    title: 'Varsity Sports',
    text: 'Left-chest hoodies, crewnecks and tees for football, hockey, fencing, sailing, squash and more.',
  },
  {
    title: 'Grad & Professional Schools',
    text: 'Pieces for Law, Medicine, Nursing, Art, Architecture, Management and other Yale schools.',
  },
  {
    title: 'The Whole Family',
    text: 'Mom, Dad, Grandma, Grandpa, Aunt, Uncle and more. Gear for everyone cheering from the sidelines.',
  },
  {
    title: 'Vintage Bulldog',
    text: 'Throwback bulldog graphics and classic shields with a worn-in, old-school feel.',
  },
]

export default function Home() {
  return (
    <>
      <section className="hero">
        <p className="eyebrow">New Haven's Bulldog outfitter</p>
        <h1>
          Wear your Yale <span className="accent">every day.</span>
        </h1>
        <p className="lead">
          Officially licensed Yale gear that's soft and easy to wear. It's made for students, alumni and the
          families who cheer them on.
        </p>
        <div className="hero-actions">
          <Link to="/products" className="btn">
            Shop the collection
          </Link>
          <Link to="/about" className="btn btn-ghost">
            Our story
          </Link>
        </div>
      </section>

      <ChatResults />

      <section>
        <h2>Find your fit</h2>
        <div className="card-grid">
          {categories.map((c) => (
            <article key={c.title} className="card">
              <h3>{c.title}</h3>
              <p>{c.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="callout">
        <h2>Need a hand picking something?</h2>
        <p>
          Tap the chat bubble in the corner. Our shopping assistant is on the way, and soon you'll be able to ask
          it about sizes, stock and gift ideas right here on the site.
        </p>
      </section>
    </>
  )
}
