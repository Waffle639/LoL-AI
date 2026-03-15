import client from './client'

export async function predict(payload: Record<string, unknown>) {
  const { data } = await client.post('/predict', payload)
  return data
}

export async function predictPregame(payload: Record<string, unknown>) {
  const { data } = await client.post('/predict/pregame', payload)
  return data
}
