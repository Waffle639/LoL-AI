// ─────────────────────────────────────────────────────────────────
// CHAMPIONS
// Champion data for the Pre-Game picker
// bg: CSS gradient for the champion cell placeholder
// ─────────────────────────────────────────────────────────────────

export const CHAMPIONS = [
  { id: 'Aatrox',       bg: 'linear-gradient(135deg,#1a1225,#2a1535,#150a20)' },
  { id: 'Ahri',         bg: 'linear-gradient(135deg,#0a1a25,#152535,#0a1520)' },
  { id: 'Akali',        bg: 'linear-gradient(135deg,#251a0a,#352510,#201505)' },
  { id: 'Alistar',      bg: 'linear-gradient(135deg,#0a251a,#153525,#052015)' },
  { id: 'Amumu',        bg: 'linear-gradient(135deg,#251520,#35202a,#201018)' },
  { id: 'Anivia',       bg: 'linear-gradient(135deg,#15201a,#203025,#101a15)' },
  { id: 'Annie',        bg: 'linear-gradient(135deg,#201525,#302035,#18101e)' },
  { id: 'Aphelios',     bg: 'linear-gradient(135deg,#0f1f28,#1a2e38,#0a1820)' },
  { id: 'Ashe',         bg: 'linear-gradient(135deg,#28180f,#38221a,#20100a)', picked: true },
  { id: 'AurelionSol',  bg: 'linear-gradient(135deg,#1f280f,#2e380a,#181f08)' },
  { id: 'Azir',         bg: 'linear-gradient(135deg,#280f1f,#38102e,#200a18)', picked: true },
  { id: 'Bard',         bg: 'linear-gradient(135deg,#0f2828,#1a3838,#0a2020)' },
  { id: 'Blitzcrank',   bg: 'linear-gradient(135deg,#1a1225,#2a1535)' },
  { id: 'Brand',        bg: 'linear-gradient(135deg,#0a1a25,#152535)' },
  { id: 'Braum',        bg: 'linear-gradient(135deg,#0a251a,#153525)' },
  { id: 'Caitlyn',      bg: 'linear-gradient(135deg,#251520,#35202a)' },
  { id: 'Camille',      bg: 'linear-gradient(135deg,#15201a,#203025)' },
  { id: 'Cassiopeia',   bg: 'linear-gradient(135deg,#0f1f28,#1a2e38)' },
  { id: "Cho'Gath",     bg: 'linear-gradient(135deg,#28180f,#38221a)' },
  { id: 'Corki',        bg: 'linear-gradient(135deg,#1f280f,#2e380a)' },
  { id: 'Darius',       bg: 'linear-gradient(135deg,#251a0a,#352510)' },
  { id: 'Diana',        bg: 'linear-gradient(135deg,#280f1f,#38102e)' },
  { id: 'Dr. Mundo',    bg: 'linear-gradient(135deg,#0f2828,#1a3838)' },
  { id: 'Draven',       bg: 'linear-gradient(135deg,#201525,#302035)' },
]

// Positions for the champion select / pre-game picker
export const POSITIONS = ['TOP', 'JNG', 'MID', 'BOT', 'SUP']

// Mock team data for pre-game screen
export const TEAM_BLUE = [
  { player: 'BrokenBlade', champion: "K'Sante", position: 'TOP', picking: true },
  { player: 'Yike',        champion: 'Vi',       position: 'JNG' },
  { player: 'Caps',        champion: 'Azir',     position: 'MID' },
  { player: 'Hans Sama',   champion: 'Varus',    position: 'BOT' },
  { player: 'Mikyx',       champion: 'Zyra',     position: 'SUP' },
]

export const TEAM_RED = [
  { player: 'Myrwn',     champion: 'Gwen',         position: 'TOP' },
  { player: 'Elyoya',    champion: 'Viego',         position: 'JNG' },
  { player: 'Fresskowy', champion: 'Neeko',         position: 'MID' },
  { player: 'Supa',      champion: 'Ashe',          position: 'BOT' },
  { player: 'Alvaro',    champion: 'Renata Glasc',  position: 'SUP', picking: true },
]
