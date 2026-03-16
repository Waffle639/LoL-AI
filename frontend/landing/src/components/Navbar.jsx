import { NAV_LINKS } from '../data/content'
import { useNavScroll } from '../hooks'

export default function Navbar() {
  const scrolled = useNavScroll()

  return (
    <nav
      className={`
        fixed top-0 left-0 right-0 z-50
        flex items-center justify-between
        px-13 h-17
        transition-all duration-400
        ${scrolled
          ? 'bg-bg/96 border-b border-gold-faint'
          : 'bg-gradient-to-b from-bg/90 to-transparent'
        }
      `}
      style={{ padding: '0 52px', height: '68px' }}
    >
      {/* Logo */}
      <a href="#" className="flex items-center gap-3 no-underline" data-cursor-hover>
        <img src="/images/LoL-Esports-Logo-PNG-SVG-Vector.png" alt="LoL AI Logo" className="h-8 object-contain" />
      </a>

      {/* Links */}
      <div className="flex gap-8">
        {NAV_LINKS.map(({ label, href }) => (
          <a
            key={label}
            href={href}
            className="font-mono text-[10px] tracking-widest text-[#3a4560] uppercase no-underline transition-colors hover:text-gold"
            data-cursor-hover
          >
            {label}
          </a>
        ))}
      </div>

      {/* CTA */}
      <a
        href="#pricing"
        className="font-rajdhani text-[11px] font-bold tracking-widest text-gold uppercase no-underline
                   px-6 py-2 clip-skew-xs
                   border border-gold-dim
                   transition-all hover:bg-gold/10 hover:border-gold"
        style={{ borderColor: '#7a5f38' }}
        data-cursor-hover
      >
        Enter the Rift
      </a>
    </nav>
  )
}