import Cursor from './components/Cursor'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Scene from './components/Scene'
import Players from './components/Players'
import Stats from './components/Stats'
import Pricing from './components/Pricing'
import { CupCTA, Footer } from './components/CupCTA'

const DRAFT_SCENE = {
  id: 'draft',
  imageSrc: '/images/minimapa.png',
  textSide: 'right',
  label: 'Pre-Game',
  title: 'Know who wins<br/>before <span class="text-stroke-gold" style="color:transparent;">first blood</span>',
  body: 'Random Forest trained on 12,276 professional matches. Input both drafts, get win probability before the game begins.',
  tags: ['76.75% accuracy', 'ROC-AUC 0.895', 'RF v1.0'],
  cta: { href: '#pricing', label: 'Try Pre-Game', variant: 'ghost' },
}

const BROADCAST_SCENE = {
  id: 'live',
  imageSrc: '/images/draft.png',
  textSide: 'left',
  label: 'In-Game',
  title: 'Real-time.<br/><span class="text-stroke-gold" style="color:transparent;">97.76%</span><br/>accurate.',
  body: 'Neural network reads 24 live features — gold, towers, dragons, barons — and delivers win probability on demand.',
  tags: ['NN v1.0', '24 features', 'ROC-AUC 0.9968'],
  cta: { href: '#pricing', label: 'Try Live', variant: 'gold' },
}

export default function App() {
  return (
    <>
      <Cursor />
      <Navbar />
      <main>
        <Hero />
        <Scene {...DRAFT_SCENE} />
        <Scene {...BROADCAST_SCENE} />
        <Players />
        <Stats />
        <Pricing />
        <CupCTA />
      </main>
      <Footer />
    </>
  )
}