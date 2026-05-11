import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import anime from 'animejs'
import AppLayout from '@/components/layout/AppLayout'
import Panel, { PanelTitle } from '@/components/ui/Panel'
import FormField from '@/components/ui/FormField'
import Button from '@/components/ui/Button'
import { useApp } from '@/context/AppContext'
import { createApiKey, regenerateApiKey } from '@/api/auth'
import { ROUTES } from '@/constants/navigation'
import styles from './Account.module.css'

// ─────────────────────────────────────────────────────────────────
// Account
// Profile · API Key (hidden by default) · Danger zone
// ─────────────────────────────────────────────────────────────────

export default function Account() {
  const navigate = useNavigate()
  const { user, apiKeyPrefix, accessToken, updateApiKeyPrefix, logout } = useApp()
  const [username, setUsername]       = useState(user.name)
  const [email, setEmail]             = useState(user.email)
  const [keyModalOpen, setKeyModalOpen] = useState(false)
  const [keyModalValue, setKeyModalValue] = useState('')
  const [keyModalCopied, setKeyModalCopied] = useState(false)
  const [keyLoading, setKeyLoading] = useState(false)
  const [keyError, setKeyError] = useState('')

  useEffect(() => {
    anime({ targets: '#s-account .panel', opacity:[0,1], translateY:[16,0], delay: anime.stagger(90), duration:420, easing:'easeOutExpo' })
    anime({ targets: '#s-account .fg',   opacity:[0,1], translateX:[-6,0],  delay: anime.stagger(45,{start:180}), duration:280, easing:'easeOutExpo' })
  }, [])

  const openKeyModal = rawKey => {
    setKeyModalValue(rawKey)
    setKeyModalCopied(false)
    setKeyModalOpen(true)
    anime({ targets: '#api-key-modal', opacity:[0,1], translateY:[10,0], duration:260, easing:'easeOutExpo' })
  }

  const closeKeyModal = () => {
    setKeyModalOpen(false)
    setKeyModalValue('')
    setKeyModalCopied(false)
  }

  const copyModalKey = () => {
    if (!keyModalValue) return
    navigator.clipboard?.writeText(keyModalValue)
    setKeyModalCopied(true)
    setTimeout(() => setKeyModalCopied(false), 1500)
  }

  const handleCreateKey = async () => {
    if (!accessToken) return
    setKeyLoading(true)
    setKeyError('')
    try {
      const payload = await createApiKey(accessToken)
      updateApiKeyPrefix(payload.api_key_prefix)
      openKeyModal(payload.api_key)
    } catch (err) {
      setKeyError(err.message || 'No se pudo crear la API key')
    } finally {
      setKeyLoading(false)
    }
  }

  const handleRegenerateKey = async () => {
    if (!accessToken) return
    setKeyLoading(true)
    setKeyError('')
    try {
      const payload = await regenerateApiKey(accessToken)
      updateApiKeyPrefix(payload.api_key_prefix)
      openKeyModal(payload.api_key)
    } catch (err) {
      setKeyError(err.message || 'No se pudo regenerar la API key')
    } finally {
      setKeyLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate(ROUTES.LOGIN)
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
            Usa el header <code className={styles.code}>X-API-Key</code> para llamadas de prediccion.
            La key completa solo se muestra una vez al crearla o regenerarla.
          </p>
          <div className={styles.keyBox}>
            <span id="api-key-val" className={styles.keyVal}>
              {apiKeyPrefix ? `${apiKeyPrefix}....` : 'Sin API key activa'}
            </span>
          </div>
          {keyError ? <div className={styles.keyError}>{keyError}</div> : null}
          <div className={styles.keyActions}>
            {apiKeyPrefix ? (
              <Button variant="ghost" size="sm" onClick={handleRegenerateKey} disabled={keyLoading}>
                {keyLoading ? 'Regenerating...' : 'Regenerate Key'}
              </Button>
            ) : (
              <Button variant="ghost" size="sm" onClick={handleCreateKey} disabled={keyLoading}>
                {keyLoading ? 'Creating...' : 'Create Key'}
              </Button>
            )}
            <span className={styles.keyWarn}>
              {apiKeyPrefix ? 'Se invalida la key anterior' : 'Solo se muestra una vez'}
            </span>
          </div>
        </Panel>

        {/* Danger zone */}
        <Panel className="panel" style={{ borderColor: 'rgba(200,48,32,.3)' }}>
          <PanelTitle style={{ color: 'var(--red)' }}>Danger Zone</PanelTitle>
          <p className={styles.dangerText}>
            Cerrar sesion en este navegador y eliminar la API key almacenada localmente.
          </p>
          <Button variant="red" size="sm" onClick={handleLogout}>Logout</Button>
        </Panel>
      </div>

      {keyModalOpen ? (
        <div className={styles.keyModalOverlay} onClick={closeKeyModal}>
          <div
            className={styles.keyModal}
            id="api-key-modal"
            onClick={e => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <div className={styles.keyModalHeader}>
              <div className={styles.keyModalTitle}>Nueva API key</div>
              <button className={styles.keyModalClose} onClick={closeKeyModal} aria-label="Cerrar">
                X
              </button>
            </div>
            <p className={styles.keyModalNote}>
              Copiala ahora. No podras recuperarla luego. Guardala en un lugar seguro.
            </p>
            <div className={styles.keyModalBox}>
              <span className={styles.keyModalValue}>{keyModalValue}</span>
              <button className={styles.keyModalCopy} onClick={copyModalKey}>
                {keyModalCopied ? 'COPIED' : 'COPY'}
              </button>
            </div>
            <div className={styles.keyModalActions}>
              <Button size="sm" onClick={closeKeyModal}>Ya la guarde</Button>
            </div>
          </div>
        </div>
      ) : null}
    </AppLayout>
  )
}
