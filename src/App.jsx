import { useState, useRef } from 'react'
import { signOut } from 'firebase/auth'
import { auth } from './services/firebase'
import { useAuth } from './hooks/useAuth'
import { classify } from './services/api'
import Header from './components/Header'
import UploadZone from './components/UploadZone'
import LoadingView from './components/LoadingView'
import ResultCard from './components/ResultCard'
import Footer from './components/Footer'
import LoginPage from './pages/LoginPage'
import BlackbirdIcon from './assets/BlackbirdIcon'

export default function App() {
  const { user, loading } = useAuth()
  const [phase, setPhase] = useState('idle')
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const timerRef = useRef(null)

  async function handleUpload(file) {
    setPreview(URL.createObjectURL(file))
    setPhase('loading')
    setError(null)
    try {
      const data = await classify(file)
      setResult(data)
      setPhase('result')
    } catch {
      setError('Error al clasificar la imagen. Intenta de nuevo.')
      if (preview) URL.revokeObjectURL(preview)
      setPreview(null)
      setPhase('idle')
    }
  }

  function handleReset() {
    clearTimeout(timerRef.current)
    if (preview) URL.revokeObjectURL(preview)
    setPreview(null)
    setResult(null)
    setError(null)
    setPhase('idle')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-cream flex items-center justify-center">
        <div className="animate-bob text-forest">
          <BlackbirdIcon className="w-12 h-12" />
        </div>
      </div>
    )
  }

  if (!user) return <LoginPage />

  return (
    <div className="min-h-screen bg-cream flex flex-col items-center px-4 py-8">
      <Header onSignOut={() => signOut(auth)} />
      <main className="w-full max-w-2xl mt-8 flex-1">
        {error && (
          <p className="text-red-500 text-sm text-center mb-4">{error}</p>
        )}
        {phase === 'idle' && <UploadZone onUpload={handleUpload} />}
        {phase === 'loading' && <LoadingView />}
        {phase === 'result' && result && (
          <ResultCard result={result} preview={preview} onReset={handleReset} />
        )}
      </main>
      <Footer />
    </div>
  )
}
