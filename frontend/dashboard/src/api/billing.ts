import client from './client'

export async function getCredits() {
  const { data } = await client.get('/billing/credits')
  return data
}

export async function getCheckoutInfo() {
  const { data } = await client.get('/billing/checkout')
  return data
}
