import { useState, useEffect } from 'react'
import anime from 'animejs'
import AppLayout from '@/components/layout/AppLayout'
import Panel, { PanelTitle } from '@/components/ui/Panel'
import FormField from '@/components/ui/FormField'
import Button from '@/components/ui/Button'
import styles from './Account.module.css'

// ─────────────────────────────────────────────────────────────────
// Account
// Profile · API Key (hidden by default) · Danger zone
// ─────────────────────────────────────────────────────────────────

const REAL_KEY  = 'lol_k8Xm2pQzVnRjF9cLsYwTuA3bGhNdEiOe7'
const MASKED_KEY = 'lol_k8••••••••••••••••••••••••••••••••'

export default function Account() {
  const [keyVisible, setKeyVisible]   = useState(false)
  const [copied, setCopied]           = useState(false)
  const [username, setUsername]       = useState('Waffle639')
  const [email, setEmail]             = useState('waffle@example.com')

  useEffect(() => {
    anime({ targets: '#s-account .panel', opacity:[0,1], translateY:[16,0], delay: anime.stagger(90), duration:420, easing:'easeOutExpo' })
    anime({ targets: '#s-account .fg',   opacity:[0,1], translateX:[-6,0],  delay: anime.stagger(45,{start:180}), duration:280, easing:'easeOutExpo' })
  }, [])

  const toggleKey = () => {
    setKeyVisible(v => !v)
    anime({ targets: '#api-key-val', opacity:[.4,1], duration:280, easing:'easeOutExpo' })
  }

  const copyKey = () => {
    navigator.clipboard?.writeText(REAL_KEY)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <AppLayout>
      <div id="s-account">
        <h1 className="sec-title">My Account</h1>
        <p className="sec-sub">Profile &nbsp;·&nbsp; API Key &nbsp;·&nbsp; Security</p>

        <div className={styles.twoCol}>
          <Panel accent="gold" className="panel">
            <PanelTitle>Profile</PanelTitle>
            <FormField label="Username" value={username} onChange={e => setUsername(e.target.value)} />
            <FormField label="Email"    value={email}    onChange={e => setEmail(e.target.value)}    />
            <Button size="sm">Save Changes</Button>
          </Panel>

          <Panel accent="teal" className="panel">
            <PanelTitle>Change Password</PanelTitle>
            <FormField label="Current Password" type="password" placeholder="••••••••" />
            <FormField label="New Password"     type="password" placeholder="••••••••" />
            <FormField label="Confirm"          type="password" placeholder="••••••••" />
            <Button variant="ghost" size="sm">Update</Button>
          </Panel>
        </div>

        {/* API Key */}
        <Panel accent="gold" className={`panel ${styles.keyPanel}`}>
          <PanelTitle>API Key</PanelTitle>
          <p className={styles.keyNote}>
            Include in <code className={styles.code}>X-API-Key</code> header for all prediction calls.
          </p>
          <div className={styles.keyBox}>
            <span id="api-key-val" className={styles.keyVal}>
              {keyVisible ? REAL_KEY : MASKED_KEY}
            </span>
            <button className={styles.keyBtn} onClick={toggleKey}>
              {keyVisible ? 'HIDE' : 'SHOW'}
            </button>
            <button className={styles.keyBtn} onClick={copyKey}>
              {copied ? 'COPIED' : 'COPY'}
            </button>
          </div>
          <div className={styles.keyActions}>
            <Button variant="ghost" size="sm">Regenerate Key</Button>
            <span className={styles.keyWarn}>Previous key will be invalidated</span>
          </div>
        </Panel>

        {/* Danger zone */}
        <Panel className="panel" style={{ borderColor: 'rgba(200,48,32,.3)' }}>
          <PanelTitle style={{ color: 'var(--red)' }}>Danger Zone</PanelTitle>
          <p className={styles.dangerText}>
            Permanently delete your account, all predictions, and remaining credits.
          </p>
          <Button variant="red" size="sm">Delete Account</Button>
        </Panel>
      </div>
    </AppLayout>
  )
}
