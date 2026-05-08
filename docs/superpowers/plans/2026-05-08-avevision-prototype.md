# AveVision Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a visually polished React prototype for bird species identification with a natural green/coffee color scheme, animations, and a mock upload → classify → result flow.

**Architecture:** Single-page React app with a three-phase state machine (`idle → loading → result`). All classification is mocked with a `setTimeout` + hardcoded result object. Framer Motion handles entrance animations; Tailwind handles all styling via a custom earthy palette.

**Tech Stack:** React 18, Vite, Tailwind CSS v3, Framer Motion, react-dropzone

---

## File Map

| File | Responsibility |
|---|---|
| `src/main.jsx` | Entry point, mounts App |
| `src/App.jsx` | Root state machine (`idle \| loading \| result`) |
| `src/index.css` | Tailwind directives + custom keyframes |
| `tailwind.config.js` | Custom colors, keyframes, animations |
| `src/assets/BlackbirdIcon.jsx` | Reusable blackbird SVG component |
| `src/data/mockResult.js` | Hardcoded mock classification result |
| `src/components/Header.jsx` | Logo + title + badges |
| `src/components/UploadZone.jsx` | Drag-and-drop upload card + button |
| `src/components/LoadingView.jsx` | Flying bird animation + status text |
| `src/components/ResultCard.jsx` | Species name, confidence bar, description, fun facts |
| `src/components/Footer.jsx` | Institution credits |

---

## Task 1: Scaffold Project

**Files:**
- Create: `package.json`, `vite.config.js`, `index.html`, `tailwind.config.js`, `postcss.config.js`

- [ ] **Step 1: Scaffold Vite React app inside the project directory**

```bash
cd /Users/mymac/Desktop/Ing-sistemas/2026-1/REDES-NEURONALES/reconocimiento-aves
npm create vite@latest . -- --template react
```

When prompted "Current directory is not empty. Remove existing files and continue?" — choose **Yes** (only the `docs/` folder is there).

Expected output: `Done. Now run: npm install`

- [ ] **Step 2: Install base dependencies**

```bash
npm install
```

Expected: packages installed with no errors.

- [ ] **Step 3: Install Tailwind CSS**

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Expected: `tailwind.config.js` and `postcss.config.js` created.

- [ ] **Step 4: Install runtime dependencies**

```bash
npm install framer-motion react-dropzone
```

Expected: both packages added to `node_modules`.

- [ ] **Step 5: Verify dev server starts**

```bash
npm run dev
```

Expected: `VITE v*.*.* ready` at `http://localhost:5173`. Open in browser — default Vite React page visible. Stop with `Ctrl+C`.

- [ ] **Step 6: Commit scaffold**

```bash
git init
git add .
git commit -m "chore: scaffold Vite React project with Tailwind and Framer Motion"
```

---

## Task 2: Configure Tailwind & Global Styles

**Files:**
- Modify: `tailwind.config.js`
- Modify: `src/index.css`

- [ ] **Step 1: Replace `tailwind.config.js` with custom palette and animations**

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        cream: '#F7F3EC',
        forest: '#2D6A4F',
        coffee: '#6B4226',
        'text-primary': '#2C1A0E',
        'text-muted': '#8B6F52',
      },
      keyframes: {
        bob: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        fly: {
          '0%': { transform: 'translateX(-120px)', opacity: '0' },
          '10%': { opacity: '1' },
          '90%': { opacity: '1' },
          '100%': { transform: 'translateX(110vw)', opacity: '0' },
        },
      },
      animation: {
        bob: 'bob 3s ease-in-out infinite',
        fly: 'fly 2.5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 2: Replace `src/index.css` with Tailwind directives and border pulse keyframe**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@keyframes borderPulse {
  0%, 100% { border-color: rgba(45, 106, 79, 0.4); }
  50% { border-color: rgba(45, 106, 79, 0.9); }
}

.border-pulse {
  animation: borderPulse 2s ease-in-out infinite;
}
```

- [ ] **Step 3: Verify Tailwind works**

Temporarily edit `src/App.jsx` to:
```jsx
export default function App() {
  return <div className="min-h-screen bg-cream flex items-center justify-center">
    <h1 className="text-5xl font-bold text-forest">AveVision</h1>
  </div>
}
```

Run `npm run dev`. Expected: cream background, dark green "AveVision" heading. Stop server.

- [ ] **Step 4: Commit**

```bash
git add tailwind.config.js src/index.css
git commit -m "chore: configure Tailwind with earthy color palette and animations"
```

---

## Task 3: Blackbird SVG Asset & Mock Data

**Files:**
- Create: `src/assets/BlackbirdIcon.jsx`
- Create: `src/data/mockResult.js`

- [ ] **Step 1: Create `src/assets/BlackbirdIcon.jsx`**

```jsx
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
```

- [ ] **Step 2: Create `src/data/mockResult.js`**

```js
export const mockResult = {
  especie: 'Mirlo Común',
  nombre_cientifico: 'Turdus merula',
  confianza: 0.91,
  descripcion:
    'El mirlo común es un ave paseriforme de la familia Turdidae, conocida por su plumaje negro brillante en los machos y su melodioso canto. Es una de las aves más reconocibles de Europa y Asia, y su canto es considerado uno de los más bellos del reino animal.',
  datos_curiosos: [
    'El macho adulto tiene un pico y anillo orbital de color amarillo-naranja intenso.',
    'Es capaz de imitar los sonidos de otras aves e incluso sonidos del entorno artificial.',
    'Puede vivir hasta 5 años en estado salvaje y más de 20 años en cautividad.',
  ],
}
```

- [ ] **Step 3: Commit**

```bash
git add src/assets/BlackbirdIcon.jsx src/data/mockResult.js
git commit -m "feat: add blackbird SVG component and mock classification result"
```

---

## Task 4: App State Machine

**Files:**
- Modify: `src/App.jsx`
- Modify: `src/main.jsx`

- [ ] **Step 1: Update `src/main.jsx`**

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- [ ] **Step 2: Write `src/App.jsx` with state machine**

```jsx
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
```

Note: Create empty placeholder components so the app compiles. In each `src/components/*.jsx` file, export a default function that returns `null` for now (Header, UploadZone, LoadingView, ResultCard, Footer).

- [ ] **Step 3: Create placeholder components so the app compiles**

Create `src/components/Header.jsx`:
```jsx
export default function Header() { return null }
```

Create `src/components/UploadZone.jsx`:
```jsx
export default function UploadZone() { return null }
```

Create `src/components/LoadingView.jsx`:
```jsx
export default function LoadingView() { return null }
```

Create `src/components/ResultCard.jsx`:
```jsx
export default function ResultCard() { return null }
```

Create `src/components/Footer.jsx`:
```jsx
export default function Footer() { return null }
```

- [ ] **Step 4: Verify app compiles without errors**

```bash
npm run dev
```

Expected: blank cream page, no console errors. Stop server.

- [ ] **Step 5: Commit**

```bash
git add src/App.jsx src/main.jsx src/components/
git commit -m "feat: add App state machine and placeholder components"
```

---

## Task 5: Header Component

**Files:**
- Modify: `src/components/Header.jsx`

- [ ] **Step 1: Implement `src/components/Header.jsx`**

```jsx
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
      <p className="text-text-muted mt-2 text-sm max-w-md mx-auto leading-relaxed">
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
```

- [ ] **Step 2: Verify visually**

Run `npm run dev`. Expected: bobbing blackbird SVG above "AveVision" in forest green, muted subtitle, four coffee-brown pill badges.

- [ ] **Step 3: Commit**

```bash
git add src/components/Header.jsx
git commit -m "feat: add Header component with bobbing blackbird and badges"
```

---

## Task 6: UploadZone Component

**Files:**
- Modify: `src/components/UploadZone.jsx`

- [ ] **Step 1: Implement `src/components/UploadZone.jsx`**

```jsx
import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import BlackbirdIcon from '../assets/BlackbirdIcon'

export default function UploadZone({ onUpload }) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles[0]) onUpload(acceptedFiles[0])
    },
    [onUpload],
  )

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    noClick: true,
    accept: { 'image/jpeg': [], 'image/png': [], 'image/webp': [] },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
  })

  return (
    <div className="flex flex-col items-center gap-5">
      <div
        {...getRootProps()}
        className={[
          'w-full border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300',
          isDragActive
            ? 'border-forest bg-forest/5 shadow-[0_0_24px_rgba(45,106,79,0.25)]'
            : 'border-forest/50 bg-white border-pulse',
        ].join(' ')}
      >
        <input {...getInputProps()} />
        <div className="text-forest/60 w-16 h-16 mx-auto mb-4">
          <BlackbirdIcon />
        </div>
        <p className="text-text-primary font-semibold text-lg">
          Arrastra o selecciona una imagen de un ave
        </p>
        <p className="text-text-muted text-sm mt-1">
          JPG · PNG · WEBP — máx. 10 MB
        </p>
      </div>
      <button
        type="button"
        onClick={open}
        className="px-8 py-3 bg-forest text-white rounded-xl font-semibold text-sm
          hover:scale-105 hover:shadow-lg transition-all duration-200 active:scale-95"
      >
        Identificar Ave
      </button>
    </div>
  )
}
```

- [ ] **Step 2: Verify visually**

Run `npm run dev`. Expected:
- Dashed card with blackbird icon, slowly pulsing border
- Dragging an image over it: border glows green, light green tint appears
- "Identificar Ave" button: lifts slightly on hover

Note: clicking the button opens the OS file picker. Selecting an image should trigger the 2-second loading phase (LoadingView is still a placeholder — you'll see a blank white area briefly, then nothing more yet).

- [ ] **Step 3: Commit**

```bash
git add src/components/UploadZone.jsx
git commit -m "feat: add UploadZone with drag-and-drop and file picker"
```

---

## Task 7: Loading View Component

**Files:**
- Modify: `src/components/LoadingView.jsx`

- [ ] **Step 1: Implement `src/components/LoadingView.jsx`**

```jsx
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
        {[0, 0.15, 0.3].map((delay, i) => (
          <span
            key={i}
            className="w-2.5 h-2.5 bg-forest rounded-full animate-bounce"
            style={{ animationDelay: `${delay}s` }}
          />
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify visually**

Upload any image via the file picker. Expected:
- Blackbird icon flies left-to-right across the card area, looping every ~2.5s
- "Analizando imagen..." text below
- Three bouncing green dots staggered
- After 2 seconds, transitions to result (still placeholder — blank area)

- [ ] **Step 3: Commit**

```bash
git add src/components/LoadingView.jsx
git commit -m "feat: add LoadingView with flying bird animation"
```

---

## Task 8: Result Card Component

**Files:**
- Modify: `src/components/ResultCard.jsx`

- [ ] **Step 1: Implement `src/components/ResultCard.jsx`**

```jsx
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
        <p className="text-text-muted italic mt-1 text-sm">{result.nombre_cientifico}</p>
      </div>

      <div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-text-muted font-medium uppercase tracking-wider text-xs">
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

      <p className="text-text-primary leading-relaxed text-sm">{result.descripcion}</p>

      <div>
        <h3 className="text-coffee font-semibold mb-3 uppercase text-xs tracking-wider">
          Datos curiosos
        </h3>
        <ul className="flex flex-col gap-3">
          {result.datos_curiosos.map((fact, i) => (
            <li key={i} className="flex items-start gap-2 text-text-primary text-sm leading-relaxed">
              <FeatherIcon />
              <span>{fact}</span>
            </li>
          ))}
        </ul>
      </div>

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
```

- [ ] **Step 2: Verify visually**

Upload any image. Expected after 2s loading:
- Card slides up smoothly from below with fade-in
- Uploaded image shown in a rounded preview
- Species name "Mirlo Común" in forest green, italic scientific name below
- Confidence bar animates from 0% to 91% over 0.8s
- Description paragraph
- Three fun facts each with a small icon
- "Intentar con otra imagen" outlined button — fills green on hover; clicking resets to upload zone

- [ ] **Step 3: Commit**

```bash
git add src/components/ResultCard.jsx
git commit -m "feat: add ResultCard with animated confidence bar and Framer Motion entrance"
```

---

## Task 9: Footer Component

**Files:**
- Modify: `src/components/Footer.jsx`

- [ ] **Step 1: Implement `src/components/Footer.jsx`**

```jsx
export default function Footer() {
  return (
    <footer className="mt-12 pb-4 text-center text-text-muted text-sm">
      <span className="text-coffee font-semibold">AveVision</span>
      {' · '}Semillero de Investigación 2026{' · '}Ingeniería de Sistemas{' · '}
      <span className="text-coffee font-medium">Uniagustiniana</span>
    </footer>
  )
}
```

- [ ] **Step 2: Verify visually**

Run `npm run dev`. Expected: centered footer at the bottom with muted text and coffee-colored brand names.

- [ ] **Step 3: Commit**

```bash
git add src/components/Footer.jsx
git commit -m "feat: add Footer with institution credits"
```

---

## Task 10: Final Polish & Verification

**Files:**
- No new files — visual review and minor adjustments only

- [ ] **Step 1: Full flow walkthrough**

Run `npm run dev`. Test the complete happy path:
1. Cream background visible, bobbing blackbird, "AveVision" title, four badges ✓
2. Dashed upload card with pulsing border ✓
3. Drag an image onto the card — green glow appears ✓
4. Click "Identificar Ave" — OS file picker opens, select any bird photo ✓
5. Flying bird animation plays for ~2s ✓
6. Result card slides in: photo preview, species name, animated confidence bar, description, fun facts ✓
7. Click "Intentar con otra imagen" → resets to upload zone ✓
8. Footer visible throughout ✓

- [ ] **Step 2: Mobile check**

In Chrome DevTools, set viewport to 375px wide. Expected: all sections stack correctly, card doesn't overflow, text readable, button reachable.

- [ ] **Step 3: Delete Vite boilerplate files**

Remove files left over from the Vite template that are not part of the app:

```bash
rm -f src/App.css public/vite.svg src/assets/react.svg
```

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete AveVision visual prototype"
```

---

## Verification Checklist

| Check | Expected |
|---|---|
| `npm run dev` starts | Vite ready at localhost:5173 |
| Background color | Warm cream `#F7F3EC` |
| Header blackbird | Bobs up/down continuously |
| Badge style | Coffee-brown outlined pills |
| Upload card border | Pulses gently when idle |
| Drag over card | Green glow border |
| After upload | ~2s flying bird loading state |
| Result card entrance | Slides up + fades in |
| Confidence bar | Animates 0% → 91% over 0.8s |
| Reset button | Returns to upload zone |
| Mobile (375px) | No overflow, all readable |
| Language | All text in Spanish |
