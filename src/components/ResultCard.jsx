import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

function FeatherIcon() {
  return (
    <svg
      className="w-4 h-4 shrink-0 mt-0.5 text-coffee"
      fill="currentColor"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M21 3L3 10.53v.98l6.84 2.65L12.48 21h.98L21 3z" />
    </svg>
  )
}

export default function ResultCard({ result, preview, onReset }) {
  const [barWidth, setBarWidth] = useState(0)

  useEffect(() => {
    setBarWidth(0)
    const timer = setTimeout(() => setBarWidth(result.confianza * 100), 300)
    return () => clearTimeout(timer)
  }, [result.confianza])

  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="bg-white rounded-2xl shadow-md p-8 flex flex-col gap-6"
    >
      {preview && (
        <img
          src={preview}
          alt="Ave analizada"
          className="w-full max-h-64 object-cover rounded-xl"
        />
      )}

      <div>
        <h2 className="text-3xl font-bold text-forest">{result.especie}</h2>
        <p className="text-muted italic mt-1 text-sm">{result.nombre_cientifico}</p>
      </div>

      <div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-muted font-medium uppercase tracking-wider text-xs">
            Confianza
          </span>
          <span className="text-forest font-bold">
            {Math.round(result.confianza * 100)}%
          </span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
          <div
            className="h-3 bg-forest rounded-full"
            style={{
              width: `${barWidth}%`,
              transition: 'width 0.8s ease-out',
            }}
          />
        </div>
      </div>

      <p className="text-primary leading-relaxed text-sm">{result.descripcion}</p>

      <div>
        <h3 className="text-coffee font-semibold mb-3 uppercase text-xs tracking-wider">
          Datos curiosos
        </h3>
        <ul className="flex flex-col gap-3">
          {result.datos_curiosos.map((fact) => (
            <li key={fact.slice(0, 20)} className="flex items-start gap-2 text-primary text-sm leading-relaxed">
              <FeatherIcon />
              <span>{fact}</span>
            </li>
          ))}
        </ul>
      </div>

      {result.metrics && (
        <div>
          <h3 className="text-coffee font-semibold mb-3 uppercase text-xs tracking-wider">
            Métricas de inferencia
          </h3>
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-gray-50 rounded-xl p-3 flex flex-col items-center gap-1">
              <span className="text-lg font-bold text-forest">{result.metrics.latency_ms}</span>
              <span className="text-xs text-muted uppercase tracking-wider">ms</span>
              <span className="text-xs text-muted">Latencia</span>
            </div>
            <div className="bg-gray-50 rounded-xl p-3 flex flex-col items-center gap-1">
              <span className="text-lg font-bold text-forest">{result.metrics.ram_mb.toFixed(1)}</span>
              <span className="text-xs text-muted uppercase tracking-wider">MB</span>
              <span className="text-xs text-muted">RAM</span>
            </div>
            <div className="bg-gray-50 rounded-xl p-3 flex flex-col items-center gap-1">
              <span className="text-lg font-bold text-forest">{result.metrics.cpu_percent.toFixed(1)}</span>
              <span className="text-xs text-muted uppercase tracking-wider">%</span>
              <span className="text-xs text-muted">CPU</span>
            </div>
          </div>
        </div>
      )}

      <button
        type="button"
        onClick={onReset}
        className="self-start px-6 py-2 border-2 border-forest text-forest rounded-xl font-semibold text-sm
          hover:bg-forest hover:text-white transition-all duration-200"
      >
        Intentar con otra imagen
      </button>
    </motion.div>
  )
}
