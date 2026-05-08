export default function BlackbirdIcon({ className = 'w-full h-full' }) {
  return (
    <svg
      className={className}
      viewBox="0 0 100 80"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Body */}
      <ellipse cx="44" cy="50" rx="22" ry="13" />
      {/* Tail */}
      <path d="M24,50 L4,42 L10,50 L4,58 Z" />
      {/* Head */}
      <circle cx="64" cy="38" r="12" />
      {/* Beak */}
      <path d="M75,36 L88,33 L74,42 Z" fill="#D4A853" />
      {/* Eye white */}
      <circle cx="67" cy="34" r="3" fill="white" />
      {/* Eye pupil */}
      <circle cx="67.5" cy="34" r="1.5" fill="#1a0a00" />
      {/* Wing shading */}
      <path d="M42,43 Q33,27 19,30 Q33,37 40,49 Z" opacity="0.2" />
      {/* Legs */}
      <line x1="40" y1="62" x2="35" y2="73" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="50" y1="62" x2="55" y2="73" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
      {/* Feet */}
      <path d="M31,73 L35,73 M35,73 L38,76 M35,73 L32,76" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" />
      <path d="M51,73 L55,73 M55,73 L58,76 M55,73 L52,76" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" />
    </svg>
  )
}
