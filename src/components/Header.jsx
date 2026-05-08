import BlackbirdIcon from '../assets/BlackbirdIcon'

const BADGES = ['CNN', 'CLASIFICACIÓN', 'DEEP LEARNING', 'UNIAGUSTINIANA']

export default function Header() {
  return (
    <header className="text-center w-full max-w-2xl">
      <div className="animate-bob inline-block text-forest">
        <BlackbirdIcon className="w-16 h-16 mx-auto" />
      </div>
      <h1 className="text-5xl font-bold text-forest mt-3 tracking-tight">
        AveVision
      </h1>
      <p className="text-muted mt-2 text-sm max-w-md mx-auto leading-relaxed">
        Identificación Automática de Aves mediante Aprendizaje Profundo
      </p>
      <div className="flex flex-wrap justify-center gap-2 mt-4">
        {BADGES.map((badge) => (
          <span
            key={badge}
            className="px-3 py-1 text-xs font-semibold border border-coffee text-coffee rounded-full"
          >
            {badge}
          </span>
        ))}
      </div>
    </header>
  )
}
