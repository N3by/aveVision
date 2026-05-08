import { useState } from 'react'
import Header from './components/Header'
import UploadZone from './components/UploadZone'
import LoadingView from './components/LoadingView'
import ResultCard from './components/ResultCard'
import Footer from './components/Footer'
import { mockResult } from './data/mockResult'

export default function App() {
  const [phase, setPhase] = useState('idle') // 'idle' | 'loading' | 'result'
  const [preview, setPreview] = useState(null)

  function handleUpload(file) {
    setPreview(URL.createObjectURL(file))
    setPhase('loading')
    setTimeout(() => setPhase('result'), 2000)
  }

  function handleReset() {
    if (preview) URL.revokeObjectURL(preview)
    setPreview(null)
    setPhase('idle')
  }

  return (
    <div className="min-h-screen bg-cream flex flex-col items-center px-4 py-8">
      <Header />
      <main className="w-full max-w-2xl mt-8 flex-1">
        {phase === 'idle' && <UploadZone onUpload={handleUpload} />}
        {phase === 'loading' && <LoadingView />}
        {phase === 'result' && (
          <ResultCard result={mockResult} preview={preview} onReset={handleReset} />
        )}
      </main>
      <Footer />
    </div>
  )
}
