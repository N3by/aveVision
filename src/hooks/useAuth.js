import { useState, useEffect } from 'react'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from '../services/firebase'

export function useAuth() {
  const [user, setUser] = useState(undefined) // undefined = still loading

  useEffect(() => {
    return onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser ?? null) // null = definitely not logged in
    })
  }, [])

  return { user, loading: user === undefined }
}
