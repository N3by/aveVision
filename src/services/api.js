import { auth } from './firebase'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function getToken() {
  const user = auth.currentUser
  if (!user) throw new Error('No autenticado')
  return user.getIdToken()
}

export async function syncUser() {
  const user = auth.currentUser
  const token = await getToken()
  const res = await fetch(`${API_URL}/auth/sync`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      firebase_uid: user.uid,
      email: user.email,
      display_name: user.displayName ?? null,
    }),
  })
  if (!res.ok) throw new Error('Error al sincronizar usuario')
  return res.json()
}

export async function classify(file) {
  const token = await getToken()
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_URL}/classify`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  })
  if (!res.ok) throw new Error('Error al clasificar la imagen')
  return res.json()
}
