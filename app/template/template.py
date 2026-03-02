"""
HTML templates profesionales para el billing de LoL AI API.
"""

# Official Riot Games / LoL logo from their CDN
LOGO_URL = "https://raw.githubusercontent.com/nicehash/NiceHashQuickMiner/master/LoL_logo.png"
# Fallback: inline SVG crest-style LoL logo embedded directly in HTML


def _html_success(api_key: str, credits: int) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Access Granted — LoL AI API</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --gold:        #C8A96E;
            --gold-bright: #F0D898;
            --gold-dim:    #7A5C2E;
            --blue:        #0AC8B9;
            --blue-dim:    #0A3D3A;
            --dark:        #03070F;
            --surface:     #080E1A;
            --surface-2:   #0D1525;
            --border:      #1A2640;
            --border-gold: rgba(200, 169, 110, 0.25);
            --text:        #8BA3BF;
            --text-bright: #C5D4E8;
            --success:     #0ABFA3;
            --radius:      2px;
        }}

        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        html {{ -webkit-font-smoothing: antialiased; }}

        body {{
            font-family: 'Inter', sans-serif;
            background: var(--dark);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 32px 16px;
        }}

        /* Ambient background */
        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            background:
                radial-gradient(ellipse 70% 50% at 50% -5%, rgba(10, 200, 185, 0.06) 0%, transparent 65%),
                radial-gradient(ellipse 50% 35% at 85% 85%, rgba(200, 169, 110, 0.04) 0%, transparent 55%);
            pointer-events: none;
            z-index: 0;
        }}

        /* Subtle grid */
        body::after {{
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(rgba(10, 200, 185, 0.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(10, 200, 185, 0.025) 1px, transparent 1px);
            background-size: 48px 48px;
            pointer-events: none;
            z-index: 0;
        }}

        .page {{
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 520px;
            animation: rise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
        }}

        @keyframes rise {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        /* ─── Logo / Header ─────────────────────────── */
        .brand {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 14px;
            margin-bottom: 28px;
        }}

        /* Inline SVG crest — official LoL style */
        .brand-crest {{
            width: 64px;
            height: 64px;
        }}

        .brand-name {{
            font-family: 'Cinzel', serif;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 4px;
            color: var(--gold);
            text-transform: uppercase;
        }}

        /* ─── Card ──────────────────────────────────── */
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow:
                0 0 0 1px rgba(10, 200, 185, 0.04),
                0 32px 80px rgba(0, 0, 0, 0.65),
                inset 0 1px 0 rgba(255, 255, 255, 0.025);
            position: relative;
        }}

        /* Gold top bar */
        .card-bar {{
            height: 2px;
            background: linear-gradient(90deg,
                transparent 0%,
                var(--gold-dim) 20%,
                var(--gold-bright) 50%,
                var(--gold-dim) 80%,
                transparent 100%
            );
        }}

        /* Corner accents */
        .card::before, .card::after,
        .card-inner::before, .card-inner::after {{
            content: '';
            position: absolute;
            width: 10px;
            height: 10px;
            border-color: var(--gold-dim);
            border-style: solid;
            opacity: 0.6;
        }}
        .card::before  {{ top: 0;  left: 0;  border-width: 1px 0 0 1px; }}
        .card::after   {{ top: 0;  right: 0; border-width: 1px 1px 0 0; }}
        .card-inner::before {{ bottom: 0; left: 0;  border-width: 0 0 1px 1px; }}
        .card-inner::after  {{ bottom: 0; right: 0; border-width: 0 1px 1px 0; }}

        .card-body {{
            padding: 36px 40px 40px;
        }}

        /* ─── Status ────────────────────────────────── */
        .status {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(10, 191, 163, 0.06);
            border: 1px solid rgba(10, 191, 163, 0.18);
            border-radius: 100px;
            padding: 5px 12px 5px 8px;
            margin-bottom: 24px;
        }}

        .status-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--success);
            box-shadow: 0 0 6px var(--success);
            animation: breathe 2.4s ease-in-out infinite;
        }}

        @keyframes breathe {{
            0%, 100% {{ opacity: 1;   box-shadow: 0 0 6px var(--success); }}
            50%       {{ opacity: 0.5; box-shadow: 0 0 12px var(--success); }}
        }}

        .status-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 500;
            color: var(--success);
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }}

        /* ─── Title ─────────────────────────────────── */
        h1 {{
            font-family: 'Cinzel', serif;
            font-size: 26px;
            font-weight: 600;
            color: var(--gold-bright);
            line-height: 1.25;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }}

        .subtitle {{
            font-size: 13.5px;
            color: var(--text);
            line-height: 1.65;
            margin-bottom: 32px;
        }}

        /* ─── Credits ───────────────────────────────── */
        .credits {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(200, 169, 110, 0.05);
            border: 1px solid var(--border-gold);
            border-radius: var(--radius);
            padding: 16px 20px;
            margin-bottom: 28px;
        }}

        .credits-left {{
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}

        .credits-eyebrow {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 500;
            color: var(--gold);
            letter-spacing: 2px;
            text-transform: uppercase;
        }}

        .credits-value {{
            font-family: 'Cinzel', serif;
            font-size: 22px;
            font-weight: 600;
            color: var(--gold-bright);
            letter-spacing: 0.5px;
        }}

        .credits-badge {{
            background: rgba(200, 169, 110, 0.1);
            border: 1px solid var(--border-gold);
            border-radius: var(--radius);
            padding: 4px 10px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: var(--gold);
            letter-spacing: 1px;
            text-transform: uppercase;
        }}

        /* ─── API Key ───────────────────────────────── */
        .field {{
            margin-bottom: 12px;
        }}

        .field-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 500;
            color: var(--blue);
            letter-spacing: 2.5px;
            text-transform: uppercase;
            margin-bottom: 8px;
            display: block;
        }}

        .key-box {{
            background: #020710;
            border: 1px solid rgba(10, 200, 185, 0.12);
            border-radius: var(--radius);
            padding: 16px 18px;
            position: relative;
            overflow: hidden;
        }}

        .key-box::after {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(10, 200, 185, 0.25), transparent);
        }}

        .key-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12.5px;
            font-weight: 400;
            color: #D6EAF8;
            word-break: break-all;
            line-height: 1.7;
            letter-spacing: 0.3px;
            user-select: all;
        }}

        /* ─── Copy Button ───────────────────────────── */
        .copy-btn {{
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            background: transparent;
            border: 1px solid rgba(10, 200, 185, 0.28);
            border-radius: var(--radius);
            padding: 14px 20px;
            color: var(--blue);
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            cursor: pointer;
            margin-top: 20px;
            margin-bottom: 20px;
            transition: all 0.18s ease;
            position: relative;
            overflow: hidden;
        }}

        .copy-btn svg {{
            width: 14px;
            height: 14px;
            flex-shrink: 0;
            transition: all 0.18s ease;
        }}

        .copy-btn::before {{
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(10, 200, 185, 0.06) 0%, transparent 60%);
            opacity: 0;
            transition: opacity 0.18s ease;
        }}

        .copy-btn:hover {{
            border-color: var(--blue);
            color: #ffffff;
            box-shadow: 0 0 24px rgba(10, 200, 185, 0.12), inset 0 0 24px rgba(10, 200, 185, 0.03);
        }}

        .copy-btn:hover::before {{ opacity: 1; }}
        .copy-btn:hover svg {{ stroke: #ffffff; }}

        .copy-btn:active {{
            transform: scale(0.99);
        }}

        .copy-btn.success {{
            border-color: rgba(10, 191, 163, 0.5);
            color: var(--success);
            pointer-events: none;
        }}

        .copy-btn.success svg {{ stroke: var(--success); }}

        /* ─── Warning ───────────────────────────────── */
        .notice {{
            display: flex;
            gap: 14px;
            align-items: flex-start;
            background: rgba(200, 169, 110, 0.04);
            border: 1px solid var(--border-gold);
            border-left: 2px solid var(--gold-dim);
            border-radius: 0 var(--radius) var(--radius) 0;
            padding: 14px 16px;
            margin-bottom: 32px;
        }}

        .notice-icon {{
            flex-shrink: 0;
            margin-top: 1px;
            opacity: 0.75;
        }}

        .notice-icon svg {{
            width: 14px;
            height: 14px;
            stroke: var(--gold);
        }}

        .notice-text {{
            font-size: 12.5px;
            color: #B08D57;
            line-height: 1.6;
        }}

        .notice-text strong {{
            color: var(--gold);
            font-weight: 600;
        }}

        /* ─── Divider ───────────────────────────────── */
        .divider {{
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--border), transparent);
            margin-bottom: 24px;
        }}

        /* ─── Footer Links ──────────────────────────── */
        .links {{
            display: flex;
            gap: 24px;
            justify-content: center;
        }}

        .link {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 500;
            color: var(--text);
            text-decoration: none;
            letter-spacing: 0.3px;
            transition: color 0.15s;
        }}

        .link svg {{
            width: 12px;
            height: 12px;
            opacity: 0.5;
            transition: opacity 0.15s;
        }}

        .link:hover {{
            color: var(--blue);
        }}

        .link:hover svg {{
            opacity: 1;
            stroke: var(--blue);
        }}
    </style>
</head>
<body>
    <div class="page">

        <!-- Brand -->
        <div class="brand">
            <!-- Inline LoL-style crest SVG -->
            <svg class="brand-crest" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                <!-- Shield base -->
                <path d="M32 4 L56 14 L56 36 C56 50 44 60 32 62 C20 60 8 50 8 36 L8 14 Z"
                      fill="#0D1525" stroke="#C8A96E" stroke-width="1.5"/>
                <!-- Inner shield -->
                <path d="M32 10 L50 18 L50 36 C50 47 42 55 32 57 C22 55 14 47 14 36 L14 18 Z"
                      fill="none" stroke="#7A5C2E" stroke-width="0.75"/>
                <!-- Center ornament — crossed swords -->
                <line x1="24" y1="40" x2="40" y2="24" stroke="#C8A96E" stroke-width="1.5" stroke-linecap="round"/>
                <line x1="40" y1="40" x2="24" y2="24" stroke="#C8A96E" stroke-width="1.5" stroke-linecap="round"/>
                <!-- Sword hilts -->
                <line x1="22" y1="22" x2="26" y2="22" stroke="#F0D898" stroke-width="1.2" stroke-linecap="round"/>
                <line x1="38" y1="22" x2="42" y2="22" stroke="#F0D898" stroke-width="1.2" stroke-linecap="round"/>
                <line x1="22" y1="42" x2="26" y2="42" stroke="#F0D898" stroke-width="1.2" stroke-linecap="round"/>
                <line x1="38" y1="42" x2="42" y2="42" stroke="#F0D898" stroke-width="1.2" stroke-linecap="round"/>
                <!-- Shield top gem -->
                <polygon points="32,13 34,17 32,19 30,17" fill="#C8A96E" opacity="0.8"/>
            </svg>
            <span class="brand-name">LoL AI API</span>
        </div>

        <!-- Card -->
        <div class="card">
            <div class="card-bar"></div>
            <div class="card-inner">
                <div class="card-body">

                    <div class="status">
                        <div class="status-dot"></div>
                        <span class="status-label">Account Active</span>
                    </div>

                    <h1>Your API Key<br>is Ready</h1>
                    <p class="subtitle">
                        Your account has been provisioned successfully. Save your key in a secure location — it will not be shown again after you close this page.
                    </p>

                    <!-- Credits -->
                    <div class="credits">
                        <div class="credits-left">
                            <span class="credits-eyebrow">Predictions Available</span>
                            <span class="credits-value">{credits}</span>
                        </div>
                        <span class="credits-badge">Requests</span>
                    </div>

                    <!-- API Key -->
                    <div class="field">
                        <span class="field-label">API Key</span>
                        <div class="key-box">
                            <div class="key-value" id="apikey">{api_key}</div>
                        </div>
                    </div>

                    <!-- Copy Button -->
                    <button class="copy-btn" id="copyBtn" onclick="copyKey()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" id="copyIcon">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                        <span id="copyLabel">Copy API Key</span>
                    </button>

                    <!-- Notice -->
                    <div class="notice">
                        <div class="notice-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                                <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                            </svg>
                        </div>
                        <p class="notice-text">
                            <strong>Keep this key private.</strong> It grants full API access to your account. Do not commit it to public repositories or share it in unsecured channels.
                        </p>
                    </div>

                    <div class="divider"></div>

                    <div class="links">
                        <a href="/docs" class="link">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                                <polyline points="14 2 14 8 20 8"/>
                            </svg>
                            API Documentation
                        </a>
                        <a href="/billing/credits" class="link">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="2" y="5" width="20" height="14" rx="2"/>
                                <line x1="2" y1="10" x2="22" y2="10"/>
                            </svg>
                            Check Credits
                        </a>
                    </div>

                </div>
            </div>
        </div>

    </div>

    <script>
        function copyKey() {{
            const key   = document.getElementById('apikey').textContent.trim();
            const btn   = document.getElementById('copyBtn');
            const label = document.getElementById('copyLabel');
            const icon  = document.getElementById('copyIcon');

            navigator.clipboard.writeText(key).then(() => {{
                // Swap to check icon
                icon.innerHTML = '<polyline points="20 6 9 17 4 12"/>';
                label.textContent = 'Copied to Clipboard';
                btn.classList.add('success');

                setTimeout(() => {{
                    icon.innerHTML = '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>';
                    label.textContent = 'Copy API Key';
                    btn.classList.remove('success');
                }}, 2800);
            }}).catch(() => {{
                // Fallback for older browsers
                const range = document.createRange();
                range.selectNode(document.getElementById('apikey'));
                window.getSelection().removeAllRanges();
                window.getSelection().addRange(range);
                document.execCommand('copy');
                window.getSelection().removeAllRanges();
                label.textContent = 'Copied';
                setTimeout(() => {{ label.textContent = 'Copy API Key'; }}, 2000);
            }});
        }}
    </script>
</body>
</html>"""


def _html_error(message: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error — LoL AI API</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --gold:        #C8A96E;
            --gold-bright: #F0D898;
            --gold-dim:    #7A5C2E;
            --red:         #C84040;
            --red-dim:     #7A2020;
            --dark:        #03070F;
            --surface:     #080E1A;
            --surface-2:   #0D1525;
            --border:      #1A2640;
            --border-red:  rgba(200, 64, 64, 0.25);
            --text:        #8BA3BF;
            --text-bright: #C5D4E8;
            --radius:      2px;
        }}

        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html {{ -webkit-font-smoothing: antialiased; }}

        body {{
            font-family: 'Inter', sans-serif;
            background: var(--dark);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 32px 16px;
        }}

        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            background:
                radial-gradient(ellipse 70% 50% at 50% -5%, rgba(200, 64, 64, 0.06) 0%, transparent 65%),
                radial-gradient(ellipse 50% 35% at 85% 85%, rgba(200, 169, 110, 0.03) 0%, transparent 55%);
            pointer-events: none;
            z-index: 0;
        }}

        body::after {{
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(rgba(200, 64, 64, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(200, 64, 64, 0.02) 1px, transparent 1px);
            background-size: 48px 48px;
            pointer-events: none;
            z-index: 0;
        }}

        .page {{
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 520px;
            animation: rise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
        }}

        @keyframes rise {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        .brand {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 14px;
            margin-bottom: 28px;
        }}

        .brand-crest {{ width: 64px; height: 64px; }}

        .brand-name {{
            font-family: 'Cinzel', serif;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 4px;
            color: var(--gold);
            text-transform: uppercase;
        }}

        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow:
                0 0 0 1px rgba(200, 64, 64, 0.04),
                0 32px 80px rgba(0, 0, 0, 0.65),
                inset 0 1px 0 rgba(255, 255, 255, 0.025);
            position: relative;
        }}

        .card-bar {{
            height: 2px;
            background: linear-gradient(90deg,
                transparent 0%,
                var(--red-dim) 20%,
                #E86060 50%,
                var(--red-dim) 80%,
                transparent 100%
            );
        }}

        .card::before, .card::after,
        .card-inner::before, .card-inner::after {{
            content: '';
            position: absolute;
            width: 10px;
            height: 10px;
            border-color: var(--red-dim);
            border-style: solid;
            opacity: 0.6;
            pointer-events: none;
        }}
        .card::before  {{ top: 0;  left: 0;  border-width: 1px 0 0 1px; }}
        .card::after   {{ top: 0;  right: 0; border-width: 1px 1px 0 0; }}
        .card-inner::before {{ bottom: 0; left: 0;  border-width: 0 0 1px 1px; }}
        .card-inner::after  {{ bottom: 0; right: 0; border-width: 0 1px 1px 0; }}

        .card-body {{ padding: 36px 40px 40px; text-align: center; }}

        .error-tag {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 500;
            color: var(--red);
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-bottom: 16px;
        }}

        h1 {{
            font-family: 'Cinzel', serif;
            font-size: 26px;
            font-weight: 600;
            color: var(--text-bright);
            line-height: 1.25;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }}

        p {{
            font-size: 13.5px;
            color: var(--text);
            line-height: 1.65;
            margin-bottom: 32px;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 14px 28px;
            border: 1px solid rgba(200, 64, 64, 0.3);
            border-radius: var(--radius);
            color: var(--red);
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-decoration: none;
            text-transform: uppercase;
            transition: all 0.18s;
        }}

        .btn:hover {{
            background: rgba(200, 64, 64, 0.06);
            border-color: var(--red);
            color: #E86060;
            box-shadow: 0 0 24px rgba(200, 64, 64, 0.1);
        }}
    </style>
</head>
<body>
    <div class="page">

        <div class="brand">
            <svg class="brand-crest" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M32 4 L56 14 L56 36 C56 50 44 60 32 62 C20 60 8 50 8 36 L8 14 Z"
                      fill="#0D1525" stroke="#7A2020" stroke-width="1.5"/>
                <path d="M32 10 L50 18 L50 36 C50 47 42 55 32 57 C22 55 14 47 14 36 L14 18 Z"
                      fill="none" stroke="#4A1515" stroke-width="0.75"/>
                <line x1="24" y1="40" x2="40" y2="24" stroke="#C84040" stroke-width="1.5" stroke-linecap="round"/>
                <line x1="40" y1="40" x2="24" y2="24" stroke="#C84040" stroke-width="1.5" stroke-linecap="round"/>
                <line x1="22" y1="22" x2="26" y2="22" stroke="#E86060" stroke-width="1.2" stroke-linecap="round"/>
                <line x1="38" y1="22" x2="42" y2="22" stroke="#E86060" stroke-width="1.2" stroke-linecap="round"/>
                <line x1="22" y1="42" x2="26" y2="42" stroke="#E86060" stroke-width="1.2" stroke-linecap="round"/>
                <line x1="38" y1="42" x2="42" y2="42" stroke="#E86060" stroke-width="1.2" stroke-linecap="round"/>
                <polygon points="32,13 34,17 32,19 30,17" fill="#C84040" opacity="0.8"/>
            </svg>
            <span class="brand-name">LoL AI API</span>
        </div>

        <div class="card">
            <div class="card-bar"></div>
            <div class="card-inner">
                <div class="card-body">
                    <div class="error-tag">System Error</div>
                    <h1>Something Went Wrong</h1>
                    <p>{message}</p>
                    <a href="/billing/checkout" class="btn">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.61"/></svg>
                        Try Again
                    </a>
                </div>
            </div>
        </div>

    </div>
</body>
</html>"""


def _html_cancel() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cancelled — LoL AI API</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --gold:        #C8A96E;
            --gold-bright: #F0D898;
            --gold-dim:    #7A5C2E;
            --dark:        #03070F;
            --surface:     #080E1A;
            --border:      #1A2640;
            --border-gold: rgba(200, 169, 110, 0.25);
            --text:        #8BA3BF;
            --text-bright: #C5D4E8;
            --radius:      2px;
        }}

        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html {{ -webkit-font-smoothing: antialiased; }}

        body {{
            font-family: 'Inter', sans-serif;
            background: var(--dark);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 32px 16px;
        }}

        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            background:
                radial-gradient(ellipse 70% 50% at 50% -5%, rgba(200, 169, 110, 0.05) 0%, transparent 65%),
                radial-gradient(ellipse 50% 35% at 85% 85%, rgba(200, 169, 110, 0.03) 0%, transparent 55%);
            pointer-events: none;
            z-index: 0;
        }}

        body::after {{
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(rgba(200, 169, 110, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(200, 169, 110, 0.02) 1px, transparent 1px);
            background-size: 48px 48px;
            pointer-events: none;
            z-index: 0;
        }}

        .page {{
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 520px;
            animation: rise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
        }}

        @keyframes rise {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        .brand {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 14px;
            margin-bottom: 28px;
        }}

        .brand-crest {{ width: 64px; height: 64px; opacity: 0.6; }}

        .brand-name {{
            font-family: 'Cinzel', serif;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 4px;
            color: var(--gold);
            text-transform: uppercase;
        }}

        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow:
                0 0 0 1px rgba(200, 169, 110, 0.04),
                0 32px 80px rgba(0, 0, 0, 0.65),
                inset 0 1px 0 rgba(255, 255, 255, 0.025);
            position: relative;
        }}

        .card-bar {{
            height: 2px;
            background: linear-gradient(90deg,
                transparent 0%,
                var(--gold-dim) 20%,
                var(--gold-bright) 50%,
                var(--gold-dim) 80%,
                transparent 100%
            );
            opacity: 0.5;
        }}

        .card::before, .card::after,
        .card-inner::before, .card-inner::after {{
            content: '';
            position: absolute;
            width: 10px;
            height: 10px;
            border-color: var(--gold-dim);
            border-style: solid;
            opacity: 0.4;
            pointer-events: none;
        }}
        .card::before  {{ top: 0;  left: 0;  border-width: 1px 0 0 1px; }}
        .card::after   {{ top: 0;  right: 0; border-width: 1px 1px 0 0; }}
        .card-inner::before {{ bottom: 0; left: 0;  border-width: 0 0 1px 1px; }}
        .card-inner::after  {{ bottom: 0; right: 0; border-width: 0 1px 1px 0; }}

        .card-body {{ padding: 36px 40px 40px; text-align: center; }}

        .tag {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 500;
            color: var(--gold);
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-bottom: 16px;
        }}

        h1 {{
            font-family: 'Cinzel', serif;
            font-size: 26px;
            font-weight: 600;
            color: var(--gold-bright);
            line-height: 1.25;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
            opacity: 0.75;
        }}

        p {{
            font-size: 13.5px;
            color: var(--text);
            line-height: 1.65;
            margin-bottom: 32px;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 14px 28px;
            border: 1px solid var(--border-gold);
            border-radius: var(--radius);
            color: var(--gold);
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-decoration: none;
            text-transform: uppercase;
            transition: all 0.18s;
        }}

        .btn:hover {{
            background: rgba(200, 169, 110, 0.06);
            border-color: var(--gold);
            color: var(--gold-bright);
            box-shadow: 0 0 24px rgba(200, 169, 110, 0.08);
        }}
    </style>
</head>
<body>
    <div class="page">

        <div class="brand">
            <svg class="brand-crest" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M32 4 L56 14 L56 36 C56 50 44 60 32 62 C20 60 8 50 8 36 L8 14 Z"
                      fill="#0D1525" stroke="#C8A96E" stroke-width="1.5"/>
                <path d="M32 10 L50 18 L50 36 C50 47 42 55 32 57 C22 55 14 47 14 36 L14 18 Z"
                      fill="none" stroke="#7A5C2E" stroke-width="0.75"/>
                <line x1="24" y1="40" x2="40" y2="24" stroke="#C8A96E" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
                <line x1="40" y1="40" x2="24" y2="24" stroke="#C8A96E" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
                <line x1="22" y1="22" x2="26" y2="22" stroke="#F0D898" stroke-width="1.2" stroke-linecap="round" opacity="0.4"/>
                <line x1="38" y1="22" x2="42" y2="22" stroke="#F0D898" stroke-width="1.2" stroke-linecap="round" opacity="0.4"/>
                <line x1="22" y1="42" x2="26" y2="42" stroke="#F0D898" stroke-width="1.2" stroke-linecap="round" opacity="0.4"/>
                <line x1="38" y1="42" x2="42" y2="42" stroke="#F0D898" stroke-width="1.2" stroke-linecap="round" opacity="0.4"/>
                <polygon points="32,13 34,17 32,19 30,17" fill="#C8A96E" opacity="0.4"/>
            </svg>
            <span class="brand-name">LoL AI API</span>
        </div>

        <div class="card">
            <div class="card-bar"></div>
            <div class="card-inner">
                <div class="card-body">
                    <div class="tag">Payment Cancelled</div>
                    <h1>No Charges Made</h1>
                    <p>Your checkout session was cancelled. No payment has been processed. You can return and complete your purchase at any time.</p>
                    <a href="/billing/register" class="btn">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
                        Return to Checkout
                    </a>
                </div>
            </div>
        </div>

    </div>
</body>
</html>"""


# ==================== REGISTRO ====================

def html_register(error: str = None) -> str:
    error_html = f'<div class="form-error">{error}</div>' if error else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Account — LoL AI API</title>
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {{--gold:#C89B3C;--gold-light:#F0E6B2;--blue:#0BC4E3;--dark:#010A13;--panel:#0A1628;--border:#1E2D3D;--text:#A0B4CC;}}
        *{{box-sizing:border-box;margin:0;padding:0;}}
        body{{font-family:'Exo 2',sans-serif;background:var(--dark);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;}}
        body::before{{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 80% 50% at 50% -10%,rgba(12,196,227,0.07) 0%,transparent 60%);pointer-events:none;z-index:0;}}
        body::after{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(11,196,227,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(11,196,227,0.02) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0;}}
        .container{{position:relative;z-index:1;width:100%;max-width:520px;animation:fadeUp 0.5s ease both;}}
        @keyframes fadeUp{{from{{opacity:0;transform:translateY(20px);}}to{{opacity:1;transform:translateY(0);}}}}
        .header{{text-align:center;margin-bottom:28px;}}
        .logo{{width:100px;margin-bottom:12px;filter:drop-shadow(0 0 16px rgba(11,196,227,0.3));}}
        .header-tag{{font-family:'Share Tech Mono',monospace;font-size:11px;color:var(--blue);letter-spacing:3px;text-transform:uppercase;}}
        .card-wrap{{position:relative;}}
        .corner{{position:absolute;width:12px;height:12px;border-color:var(--gold);border-style:solid;opacity:0.4;}}
        .corner-tl{{top:-1px;left:-1px;border-width:2px 0 0 2px;}}
        .corner-tr{{top:-1px;right:-1px;border-width:2px 2px 0 0;}}
        .corner-bl{{bottom:-1px;left:-1px;border-width:0 0 2px 2px;}}
        .corner-br{{bottom:-1px;right:-1px;border-width:0 2px 2px 0;}}
        .card{{background:var(--panel);border:1px solid var(--border);border-radius:4px;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,0.6);}}
        .card-accent{{height:3px;background:linear-gradient(90deg,transparent,var(--gold),var(--gold-light),var(--gold),transparent);}}
        .card-body{{padding:36px 40px;}}
        h1{{font-family:'Rajdhani',sans-serif;font-size:26px;font-weight:700;color:#E8D5A3;margin-bottom:4px;letter-spacing:1px;}}
        .subtitle{{font-size:13px;color:var(--text);margin-bottom:28px;}}
        .form-group{{margin-bottom:18px;}}
        label{{font-family:'Share Tech Mono',monospace;font-size:10px;color:var(--blue);letter-spacing:2px;text-transform:uppercase;display:block;margin-bottom:6px;}}
        input[type=text],input[type=email],input[type=password]{{width:100%;background:#040D18;border:1px solid rgba(11,196,227,0.15);border-radius:4px;padding:12px 14px;color:#E8F4FD;font-family:'Exo 2',sans-serif;font-size:14px;outline:none;transition:border-color 0.2s;}}
        input:focus{{border-color:rgba(11,196,227,0.5);}}
        .plan-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:24px;}}
        .plan-card{{position:relative;cursor:pointer;}}
        .plan-card input[type=radio]{{position:absolute;opacity:0;width:0;height:0;}}
        .plan-label{{display:block;background:#040D18;border:1px solid var(--border);border-radius:4px;padding:16px;transition:all 0.2s;cursor:pointer;}}
        .plan-card input:checked+.plan-label{{border-color:var(--gold);background:rgba(200,155,60,0.06);}}
        .plan-name{{font-family:'Rajdhani',sans-serif;font-size:16px;font-weight:700;color:var(--gold-light);margin-bottom:4px;}}
        .plan-desc{{font-size:12px;color:var(--text);margin-bottom:8px;}}
        .plan-badge{{font-family:'Share Tech Mono',monospace;font-size:10px;color:var(--blue);letter-spacing:1px;}}
        .submit-btn{{width:100%;background:transparent;border:1px solid rgba(200,155,60,0.4);border-radius:4px;padding:14px;color:var(--gold-light);font-family:'Rajdhani',sans-serif;font-size:16px;font-weight:600;letter-spacing:2px;text-transform:uppercase;cursor:pointer;margin-bottom:16px;transition:all 0.2s;}}
        .submit-btn:hover{{background:rgba(200,155,60,0.08);border-color:var(--gold);}}
        .form-error{{background:rgba(232,64,87,0.08);border:1px solid rgba(232,64,87,0.3);border-left:3px solid #E84057;border-radius:0 4px 4px 0;padding:12px 16px;font-size:13px;color:#E84057;margin-bottom:20px;}}
        .login-link{{text-align:center;font-size:13px;color:var(--text);}}
        .login-link a{{color:var(--blue);text-decoration:none;}}
        .login-link a:hover{{text-decoration:underline;}}
        .section-label{{font-family:'Share Tech Mono',monospace;font-size:10px;color:var(--gold);letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;}}
        .divider{{height:1px;background:linear-gradient(90deg,transparent,var(--border),transparent);margin:20px 0;}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{LOGO_URL}" alt="LoL AI API" class="logo">
            <div class="header-tag">New Account Registration</div>
        </div>
        <div class="card-wrap">
            <div class="corner corner-tl"></div><div class="corner corner-tr"></div>
            <div class="corner corner-bl"></div><div class="corner corner-br"></div>
            <div class="card">
                <div class="card-accent"></div>
                <div class="card-body">
                    <h1>Create Account</h1>
                    <p class="subtitle">Register to get your API Key and start making predictions.</p>
                    {error_html}
                    <form method="POST" action="/billing/register" autocomplete="off">
                        <div class="form-group">
                            <label for="username">Username</label>
                            <input type="text" id="username" name="username" placeholder="summoner_name" required minlength="3">
                        </div>
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" name="email" placeholder="you@example.com" required>
                        </div>
                        <div class="form-group">
                            <label for="password">Password</label>
                            <input type="password" id="password" name="password" placeholder="Min. 8 characters" required minlength="8">
                        </div>
                        <div class="divider"></div>
                        <div class="section-label">Choose your plan</div>
                        <div class="plan-grid">
                            <div class="plan-card">
                                <input type="radio" name="plan" id="plan_starter" value="starter" checked>
                                <label class="plan-label" for="plan_starter">
                                    <div class="plan-name">Starter</div>
                                    <div class="plan-desc">20 predictions</div>
                                    <div class="plan-badge">One-time payment</div>
                                </label>
                            </div>
                            <div class="plan-card">
                                <input type="radio" name="plan" id="plan_monthly" value="monthly">
                                <label class="plan-label" for="plan_monthly">
                                    <div class="plan-name">Monthly Pro</div>
                                    <div class="plan-desc">50 predictions/mo</div>
                                    <div class="plan-badge">Subscription</div>
                                </label>
                            </div>
                        </div>
                        <button type="submit" class="submit-btn">Continue to Payment →</button>
                    </form>
                    <p class="login-link">Already have an account? <a href="/account/login">Sign in →</a></p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""


# ==================== LOGIN ====================

def html_login(error: str = None) -> str:
    error_html = f'<div class="form-error">{error}</div>' if error else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In — LoL AI API</title>
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root{{--gold:#C89B3C;--gold-light:#F0E6B2;--blue:#0BC4E3;--dark:#010A13;--panel:#0A1628;--border:#1E2D3D;--text:#A0B4CC;}}
        *{{box-sizing:border-box;margin:0;padding:0;}}
        body{{font-family:'Exo 2',sans-serif;background:var(--dark);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;}}
        body::before{{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 80% 50% at 50% -10%,rgba(12,196,227,0.07) 0%,transparent 60%);pointer-events:none;z-index:0;}}
        body::after{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(11,196,227,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(11,196,227,0.02) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0;}}
        .container{{position:relative;z-index:1;width:100%;max-width:420px;animation:fadeUp 0.5s ease both;}}
        @keyframes fadeUp{{from{{opacity:0;transform:translateY(20px);}}to{{opacity:1;transform:translateY(0);}}}}
        .header{{text-align:center;margin-bottom:28px;}}
        .logo{{width:100px;margin-bottom:12px;filter:drop-shadow(0 0 16px rgba(11,196,227,0.3));}}
        .header-tag{{font-family:'Share Tech Mono',monospace;font-size:11px;color:var(--blue);letter-spacing:3px;text-transform:uppercase;}}
        .card-wrap{{position:relative;}}
        .corner{{position:absolute;width:12px;height:12px;border-color:var(--gold);border-style:solid;opacity:0.4;}}
        .corner-tl{{top:-1px;left:-1px;border-width:2px 0 0 2px;}}
        .corner-tr{{top:-1px;right:-1px;border-width:2px 2px 0 0;}}
        .corner-bl{{bottom:-1px;left:-1px;border-width:0 0 2px 2px;}}
        .corner-br{{bottom:-1px;right:-1px;border-width:0 2px 2px 0;}}
        .card{{background:var(--panel);border:1px solid var(--border);border-radius:4px;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,0.6);}}
        .card-accent{{height:3px;background:linear-gradient(90deg,transparent,var(--gold),var(--gold-light),var(--gold),transparent);}}
        .card-body{{padding:36px 40px;}}
        h1{{font-family:'Rajdhani',sans-serif;font-size:26px;font-weight:700;color:#E8D5A3;margin-bottom:4px;}}
        .subtitle{{font-size:13px;color:var(--text);margin-bottom:28px;}}
        .form-group{{margin-bottom:18px;}}
        label{{font-family:'Share Tech Mono',monospace;font-size:10px;color:var(--blue);letter-spacing:2px;text-transform:uppercase;display:block;margin-bottom:6px;}}
        input{{width:100%;background:#040D18;border:1px solid rgba(11,196,227,0.15);border-radius:4px;padding:12px 14px;color:#E8F4FD;font-family:'Exo 2',sans-serif;font-size:14px;outline:none;transition:border-color 0.2s;}}
        input:focus{{border-color:rgba(11,196,227,0.5);}}
        .submit-btn{{width:100%;background:transparent;border:1px solid rgba(200,155,60,0.4);border-radius:4px;padding:14px;color:var(--gold-light);font-family:'Rajdhani',sans-serif;font-size:16px;font-weight:600;letter-spacing:2px;text-transform:uppercase;cursor:pointer;margin-bottom:16px;transition:all 0.2s;}}
        .submit-btn:hover{{background:rgba(200,155,60,0.08);border-color:var(--gold);}}
        .form-error{{background:rgba(232,64,87,0.08);border:1px solid rgba(232,64,87,0.3);border-left:3px solid #E84057;border-radius:0 4px 4px 0;padding:12px 16px;font-size:13px;color:#E84057;margin-bottom:20px;}}
        .register-link{{text-align:center;font-size:13px;color:var(--text);}}
        .register-link a{{color:var(--blue);text-decoration:none;}}
        .register-link a:hover{{text-decoration:underline;}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{LOGO_URL}" alt="LoL AI API" class="logo">
            <div class="header-tag">Account Access</div>
        </div>
        <div class="card-wrap">
            <div class="corner corner-tl"></div><div class="corner corner-tr"></div>
            <div class="corner corner-bl"></div><div class="corner corner-br"></div>
            <div class="card">
                <div class="card-accent"></div>
                <div class="card-body">
                    <h1>Sign In</h1>
                    <p class="subtitle">Access your account to check credits and manage your API Key.</p>
                    {error_html}
                    <form method="POST" action="/account/login">
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" name="email" placeholder="you@example.com" required>
                        </div>
                        <div class="form-group">
                            <label for="password">Password</label>
                            <input type="password" id="password" name="password" placeholder="Your password" required>
                        </div>
                        <button type="submit" class="submit-btn">Sign In →</button>
                    </form>
                    <p class="register-link">Don't have an account? <a href="/billing/register">Register →</a></p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""


# ==================== DASHBOARD ====================

def html_dashboard(
    username: str,
    email: str,
    plan: str,
    credits: int,
    key_prefix: str = None,
    raw_key: str = None,
) -> str:
    plan_label       = "Monthly Pro" if plan == "monthly" else "Starter Pack"
    plan_badge_color = "#0BC4E3" if plan == "monthly" else "#C89B3C"

    if raw_key:
        key_display = f'<div class="key-value" id="apikey">{raw_key}</div>'
        key_note    = '<span style="color:#1de9b6;font-size:12px;">⚡ Key visible — save it now</span>'
        copy_btn    = '<button class="copy-btn" onclick="copyKey()">Copy API Key</button>'
    elif key_prefix:
        key_display = f'<div class="key-value">{key_prefix}••••••••••••••••••••••••••••••</div>'
        key_note    = '<span style="color:#6b7280;font-size:12px;">Key shown once after registration</span>'
        copy_btn    = ""
    else:
        key_display = '<div class="key-value" style="color:#6b7280">No API key found</div>'
        key_note    = ""
        copy_btn    = ""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard — LoL AI API</title>
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root{{--gold:#C89B3C;--gold-light:#F0E6B2;--blue:#0BC4E3;--dark:#010A13;--panel:#0A1628;--border:#1E2D3D;--text:#A0B4CC;}}
        *{{box-sizing:border-box;margin:0;padding:0;}}
        body{{font-family:'Exo 2',sans-serif;background:var(--dark);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;}}
        body::before{{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 80% 50% at 50% -10%,rgba(12,196,227,0.07) 0%,transparent 60%);pointer-events:none;z-index:0;}}
        body::after{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(11,196,227,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(11,196,227,0.02) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0;}}
        .container{{position:relative;z-index:1;width:100%;max-width:560px;animation:fadeUp 0.5s ease both;}}
        @keyframes fadeUp{{from{{opacity:0;transform:translateY(20px);}}to{{opacity:1;transform:translateY(0);}}}}
        .header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:28px;}}
        .logo{{width:80px;filter:drop-shadow(0 0 12px rgba(11,196,227,0.3));}}
        .logout-btn{{font-family:'Share Tech Mono',monospace;font-size:11px;color:var(--text);text-decoration:none;letter-spacing:2px;border:1px solid var(--border);padding:8px 14px;border-radius:4px;transition:all 0.2s;}}
        .logout-btn:hover{{color:var(--blue);border-color:rgba(11,196,227,0.3);}}
        .card-wrap{{position:relative;}}
        .corner{{position:absolute;width:12px;height:12px;border-color:var(--gold);border-style:solid;opacity:0.4;}}
        .corner-tl{{top:-1px;left:-1px;border-width:2px 0 0 2px;}}
        .corner-tr{{top:-1px;right:-1px;border-width:2px 2px 0 0;}}
        .corner-bl{{bottom:-1px;left:-1px;border-width:0 0 2px 2px;}}
        .corner-br{{bottom:-1px;right:-1px;border-width:0 2px 2px 0;}}
        .card{{background:var(--panel);border:1px solid var(--border);border-radius:4px;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,0.6);}}
        .card-accent{{height:3px;background:linear-gradient(90deg,transparent,var(--gold),var(--gold-light),var(--gold),transparent);}}
        .card-body{{padding:36px 40px;}}
        .user-row{{display:flex;align-items:center;gap:14px;margin-bottom:28px;padding-bottom:24px;border-bottom:1px solid var(--border);}}
        .avatar{{width:44px;height:44px;border-radius:50%;background:rgba(11,196,227,0.1);border:1px solid rgba(11,196,227,0.2);display:flex;align-items:center;justify-content:center;font-family:'Rajdhani',sans-serif;font-size:18px;font-weight:700;color:var(--blue);flex-shrink:0;}}
        .user-info h2{{font-family:'Rajdhani',sans-serif;font-size:20px;font-weight:700;color:#E8D5A3;}}
        .user-info p{{font-size:13px;color:var(--text);}}
        .plan-tag{{display:inline-block;font-family:'Share Tech Mono',monospace;font-size:10px;letter-spacing:2px;padding:3px 10px;border-radius:2px;border:1px solid;margin-top:4px;}}
        .stats-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:24px;}}
        .stat-card{{background:#040D18;border:1px solid var(--border);border-radius:4px;padding:16px;}}
        .stat-label{{font-family:'Share Tech Mono',monospace;font-size:10px;color:var(--text);letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;}}
        .stat-value{{font-family:'Rajdhani',sans-serif;font-size:28px;font-weight:700;color:var(--gold-light);}}
        .stat-sub{{font-size:12px;color:var(--text);margin-top:2px;}}
        .section-label{{font-family:'Share Tech Mono',monospace;font-size:10px;color:var(--blue);letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;}}
        .key-box{{background:#040D18;border:1px solid rgba(11,196,227,0.15);border-radius:4px;padding:16px 18px;margin-bottom:8px;position:relative;}}
        .key-box::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(11,196,227,0.3),transparent);}}
        .key-value{{font-family:'Share Tech Mono',monospace;font-size:13px;color:#E8F4FD;word-break:break-all;line-height:1.6;letter-spacing:0.5px;}}
        .key-footer{{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;}}
        .copy-btn{{background:transparent;border:1px solid rgba(11,196,227,0.3);border-radius:4px;padding:10px 20px;color:var(--blue);font-family:'Rajdhani',sans-serif;font-size:14px;font-weight:600;letter-spacing:2px;text-transform:uppercase;cursor:pointer;width:100%;margin-bottom:20px;transition:all 0.2s;}}
        .copy-btn:hover{{border-color:var(--blue);color:#fff;}}
        .copy-btn.copied{{border-color:#1de9b6;color:#1de9b6;}}
        .divider{{height:1px;background:linear-gradient(90deg,transparent,var(--border),transparent);margin:20px 0;}}
        .footer-links{{display:flex;gap:16px;justify-content:center;}}
        .footer-link{{font-family:'Share Tech Mono',monospace;font-size:12px;color:var(--text);text-decoration:none;letter-spacing:1px;transition:color 0.2s;}}
        .footer-link:hover{{color:var(--blue);}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{LOGO_URL}" alt="LoL AI API" class="logo">
            <a href="/account/logout" class="logout-btn">← Sign Out</a>
        </div>
        <div class="card-wrap">
            <div class="corner corner-tl"></div><div class="corner corner-tr"></div>
            <div class="corner corner-bl"></div><div class="corner corner-br"></div>
            <div class="card">
                <div class="card-accent"></div>
                <div class="card-body">
                    <div class="user-row">
                        <div class="avatar">{username[0].upper()}</div>
                        <div class="user-info">
                            <h2>{username}</h2>
                            <p>{email}</p>
                            <span class="plan-tag" style="color:{plan_badge_color};border-color:{plan_badge_color}40">{plan_label}</span>
                        </div>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-label">Credits Left</div>
                            <div class="stat-value">{credits}</div>
                            <div class="stat-sub">predictions available</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Plan</div>
                            <div class="stat-value" style="font-size:18px;padding-top:5px">{plan_label}</div>
                            <div class="stat-sub">{"renews monthly" if plan == "monthly" else "one-time purchase"}</div>
                        </div>
                    </div>
                    <div class="section-label">API Key</div>
                    <div class="key-box">{key_display}</div>
                    <div class="key-footer">{key_note}</div>
                    {copy_btn}
                    <div class="divider"></div>
                    <div class="footer-links">
                        <a href="/docs" class="footer-link">API Docs</a>
                        <a href="/billing/register" class="footer-link">New plan</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        function copyKey() {{
            const key = document.getElementById('apikey')?.textContent;
            if (!key) return;
            navigator.clipboard.writeText(key).then(() => {{
                const btn = document.querySelector('.copy-btn');
                btn.textContent = '✓  Copied';
                btn.classList.add('copied');
                setTimeout(() => {{ btn.textContent = 'Copy API Key'; btn.classList.remove('copied'); }}, 2500);
            }});
        }}
    </script>
</body>
</html>"""