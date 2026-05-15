import { useRef, useState } from 'react'
import { motion } from 'framer-motion'
import styles from './DropZone.module.css'

const MAX_SIZE_MB = 10
const ALLOWED = ['image/jpeg', 'image/png', 'image/webp']
const ALLOWED_EXT = '.jpg, .jpeg, .png, .webp'

export default function DropZone({ onFile, error }) {
  const inputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)
  const [localError, setLocalError] = useState(null)

  function validate(file) {
    if (!ALLOWED.includes(file.type)) {
      return `Можно только ${ALLOWED_EXT}`
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `Файл больше ${MAX_SIZE_MB} МБ`
    }
    return null
  }

  function handleFile(file) {
    const err = validate(file)
    if (err) {
      setLocalError(err)
      return
    }
    setLocalError(null)
    onFile(file)
  }

  function onDrop(e) {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }

  function onDragOver(e) {
    e.preventDefault()
    setIsDragging(true)
  }

  function onDragLeave(e) {
    e.preventDefault()
    setIsDragging(false)
  }

  function onPick(e) {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  const displayError = localError || error

  return (
    <div className={styles.wrapper}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.6 }}
        className={styles.intro}
      >
        <h1 className={styles.title}>
          Сфотографируй <em>продукты</em> —
          <br />
          получи рецепт.
        </h1>
        <p className={styles.subtitle}>
          ИИ распознает ингредиенты на фото и подберёт три рецепта,
          которые можно из них приготовить.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.25, duration: 0.5 }}
        className={`${styles.zone} ${isDragging ? styles.dragging : ''}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click()
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ALLOWED.join(',')}
          onChange={onPick}
          className={styles.input}
        />

        <div className={styles.zoneInner}>
          <motion.svg
            width="56"
            height="56"
            viewBox="0 0 56 56"
            fill="none"
            animate={
              isDragging
                ? { y: -6, scale: 1.1 }
                : { y: 0, scale: 1 }
            }
            transition={{ type: 'spring', stiffness: 300, damping: 18 }}
          >
            <rect
              x="6"
              y="14"
              width="44"
              height="34"
              rx="6"
              stroke="currentColor"
              strokeWidth="1.5"
              fill="none"
              opacity="0.4"
            />
            <path
              d="M14 38l8-8 6 6 10-10 8 8"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              opacity="0.5"
            />
            <circle cx="20" cy="22" r="3" fill="currentColor" opacity="0.5" />
            <motion.path
              d="M28 6v18M22 12l6-6 6 6"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              animate={
                isDragging
                  ? { y: -3, opacity: 1 }
                  : { y: 0, opacity: 0.85 }
              }
              transition={{ duration: 0.3 }}
            />
          </motion.svg>

          <div className={styles.text}>
            <span className={styles.headline}>
              {isDragging ? 'Отпускай!' : 'Перетащи фото или нажми'}
            </span>
            <span className={styles.hint}>
              JPEG, PNG или WebP · до {MAX_SIZE_MB} МБ
            </span>
          </div>
        </div>

        <div className={styles.corner} data-pos="tl" />
        <div className={styles.corner} data-pos="tr" />
        <div className={styles.corner} data-pos="bl" />
        <div className={styles.corner} data-pos="br" />
      </motion.div>

      {displayError && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className={styles.error}
        >
          {displayError}
        </motion.div>
      )}
    </div>
  )
}
