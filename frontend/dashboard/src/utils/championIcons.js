const DDRAGON_VERSION = '15.5.1'

const CHAMPION_KEY_MAP = {
  "Kha'Zix": 'Khazix',
  "Kai'Sa": 'Kaisa',
  "Cho'Gath": 'Chogath',
  "Bel'Veth": 'Belveth',
  "Kog'Maw": 'KogMaw',
  "Rek'Sai": 'RekSai',
  "Vel'Koz": 'Velkoz',
  Wukong: 'MonkeyKing',
  'Nunu & Willump': 'Nunu',
  LeBlanc: 'Leblanc',
  'Lee Sin': 'LeeSin',
}

export function getChampionIconUrl(championName) {
  if (!championName) return ''
  const mapped = CHAMPION_KEY_MAP[championName]
  const normalized = (mapped || championName).replace(/[^a-zA-Z]/g, '')
  return `https://ddragon.leagueoflegends.com/cdn/${DDRAGON_VERSION}/img/champion/${normalized}.png`
}
