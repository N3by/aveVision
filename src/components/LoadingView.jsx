import BlackbirdIcon from '../assets/BlackbirdIcon'

export default function LoadingView() {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-8">
      <div className="relative w-full h-16 overflow-hidden">
        {/* Use marginTop instead of translateY to avoid conflicting with the fly animation's translateX */}
        <div className="animate-fly absolute text-forest" style={{ top: '50%', marginTop: '-28px' }}>
          <BlackbirdIcon className="w-14 h-14 -rotate-12" />
        </div>
      </div>
      <p className="text-forest font-semibold text-lg tracking-wide">
        Analizando imagen...
      </p>
      <div className="flex gap-2">
        {[0, 0.15, 0.3].map((delay) => (
          <span
            key={delay}
            className="w-2.5 h-2.5 bg-forest rounded-full animate-bounce"
            style={{ animationDelay: `${delay}s` }}
          />
        ))}
      </div>
    </div>
  )
}
