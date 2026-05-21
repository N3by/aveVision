import { useState } from 'react'
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
} from 'firebase/auth'
import { auth, googleProvider } from '../services/firebase'
import { syncUser } from '../services/api'
import BlackbirdIcon from '../assets/BlackbirdIcon'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleEmailAuth(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      if (isRegister) {
        await createUserWithEmailAndPassword(auth, email, password)
      } else {
        await signInWithEmailAndPassword(auth, email, password)
      }
      await syncUser()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleGoogle() {
    setError(null)
    setLoading(true)
    try {
      await signInWithPopup(auth, googleProvider)
      await syncUser()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-cream flex flex-col items-center justify-center px-4">
      <div className="animate-bob inline-block text-forest mb-4">
        <BlackbirdIcon className="w-16 h-16" />
      </div>
      <h1 className="text-4xl font-bold text-forest mb-1">AveVision</h1>
      <p className="text-muted text-sm mb-8">Identificación Automática de Aves</p>

      <div className="bg-white rounded-2xl shadow-md p-8 w-full max-w-sm flex flex-col gap-4">
        <form onSubmit={handleEmailAuth} className="flex flex-col gap-3">
          <input
            type="email"
            placeholder="Correo electrónico"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="border border-gray-200 rounded-xl px-4 py-2.5 text-sm text-primary focus:outline-none focus:border-forest"
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="border border-gray-200 rounded-xl px-4 py-2.5 text-sm text-primary focus:outline-none focus:border-forest"
          />
          {error && <p className="text-red-500 text-xs leading-snug">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="bg-forest text-white rounded-xl py-2.5 font-semibold text-sm hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {loading ? 'Cargando...' : isRegister ? 'Registrarse' : 'Iniciar sesión'}
          </button>
        </form>

        <button
          type="button"
          onClick={() => setIsRegister(!isRegister)}
          className="text-muted text-xs text-center hover:text-forest transition-colors"
        >
          {isRegister ? '¿Ya tienes cuenta? Inicia sesión' : '¿No tienes cuenta? Regístrate'}
        </button>

        <div className="flex items-center gap-2">
          <div className="flex-1 h-px bg-gray-100" />
          <span className="text-muted text-xs">o</span>
          <div className="flex-1 h-px bg-gray-100" />
        </div>

        <button
          type="button"
          onClick={handleGoogle}
          disabled={loading}
          className="border-2 border-coffee text-coffee rounded-xl py-2.5 font-semibold text-sm hover:bg-coffee/5 transition-colors disabled:opacity-50"
        >
          Continuar con Google
        </button>
      </div>
    </div>
  )
}
