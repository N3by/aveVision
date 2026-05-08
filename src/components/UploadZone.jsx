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
            : 'border-forest/50 bg-white animate-border-pulse',
        ].join(' ')}
      >
        <input {...getInputProps()} />
        <div className="text-forest/60 w-16 h-16 mx-auto mb-4">
          <BlackbirdIcon />
        </div>
        <p className="text-primary font-semibold text-lg">
          Arrastra o selecciona una imagen de un ave
        </p>
        <p className="text-muted text-sm mt-1">
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
