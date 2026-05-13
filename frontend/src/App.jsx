import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import DropZone from './components/DropZone.jsx'
import CookingLoader from './components/CookingLoader.jsx'
import RecipeGrid from './components/RecipeGrid.jsx'
import RecipeDetail from './components/RecipeDetail.jsx'
import { recognizeFood } from './api/client.js'
import styles from './App.module.css'

const STAGE = {
  UPLOAD: 'upload',
  LOADING: 'loading',
  RESULTS: 'results',
  DETAIL: 'detail',
}

export default function App() {
  const [stage, setStage] = useState(STAGE.UPLOAD)
  const [data, setData] = useState(null)
  const [selectedRecipe, setSelectedRecipe] = useState(null)
  const [error, setError] = useState(null)

  async function handleFile(file) {
    console.log('[App] handleFile called with', file?.name, file?.size, 'bytes')
    setError(null)
    setStage(STAGE.LOADING)
    try {
      const result = await recognizeFood(file)
      console.log('[App] recognizeFood resolved with:', result)
      setData(result)
      setStage(STAGE.RESULTS)
    } catch (err) {
      console.error('[App] recognizeFood failed:', err)
      setError(err.message || 'Что-то пошло не так')
      setStage(STAGE.UPLOAD)
    }
  }

  function handleSelectRecipe(recipe) {
    setSelectedRecipe(recipe)
    setStage(STAGE.DETAIL)
  }

  function handleBack() {
    setSelectedRecipe(null)
    setStage(STAGE.RESULTS)
  }

  function handleReset() {
    setData(null)
    setSelectedRecipe(null)
    setError(null)
    setStage(STAGE.UPLOAD)
  }

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <motion.button
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className={styles.brand}
          onClick={handleReset}
          type="button"
        >
          <img src="/logo.png" alt="" className={styles.brandLogo} />
          <span className={styles.brandText}>
            food<em>shot</em>
          </span>
        </motion.button>
      </header>

      <main className={styles.main}>
        <AnimatePresence mode="wait">
          {stage === STAGE.UPLOAD && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className={styles.stage}
            >
              <DropZone onFile={handleFile} error={error} />
            </motion.div>
          )}

          {stage === STAGE.LOADING && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className={styles.stage}
            >
              <CookingLoader />
            </motion.div>
          )}

          {stage === STAGE.RESULTS && data && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className={styles.stage}
            >
              <RecipeGrid
                data={data}
                onSelect={handleSelectRecipe}
                onReset={handleReset}
              />
            </motion.div>
          )}

          {stage === STAGE.DETAIL && selectedRecipe && (
            <motion.div
              key="detail"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className={styles.stage}
            >
              <RecipeDetail recipe={selectedRecipe} onBack={handleBack} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}
