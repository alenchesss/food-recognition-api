import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { DotLottieReact } from '@lottiefiles/dotlottie-react'
import animationData from '../assets/loader.json'
import styles from './CookingLoader.module.css'

const MESSAGES = [
  'Разглядываю, что у тебя там...',
  'Достаю поваренную книгу...',
  'Подбираю интересные сочетания...',
  'Почти готово, пробую соус...',
]

export default function CookingLoader() {
  const [messageIndex, setMessageIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((i) => (i + 1) % MESSAGES.length)
    }, 3500)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className={styles.wrapper}>
      <div className={styles.sceneWrap}>
        <DotLottieReact
          data={animationData}
          loop
          autoplay
          className={styles.lottie}
        />
      </div>

      <div className={styles.textBlock}>
        <motion.div
          key={messageIndex}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.4 }}
          className={styles.message}
        >
          {MESSAGES[messageIndex]}
        </motion.div>

        <div className={styles.dots}>
          {[0, 1, 2].map((i) => (
            <motion.span
              key={i}
              className={styles.dot}
              initial={{ opacity: 0.2, y: 0 }}
              animate={{ opacity: [0.2, 1, 0.2], y: [0, -3, 0] }}
              transition={{
                duration: 1.2,
                repeat: Infinity,
                delay: i * 0.18,
                ease: 'easeInOut',
              }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
