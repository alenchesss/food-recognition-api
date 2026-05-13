import { motion } from 'framer-motion'
import styles from './RecipeDetail.module.css'

export default function RecipeDetail({ recipe, onBack }) {
  return (
    <div className={styles.wrapper}>
      <button className={styles.back} onClick={onBack}>
        ← к вариантам
      </button>

      <motion.div
        className={styles.hero}
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        {recipe.image && (
          <img
            src={recipe.image}
            alt={recipe.title}
            className={styles.heroImage}
          />
        )}
        <div className={styles.heroOverlay} />
        <div className={styles.heroContent}>
          <motion.h1
            className={styles.title}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            {recipe.title}
          </motion.h1>
        </div>
      </motion.div>

      <div className={styles.body}>
        {recipe.missing_ingredients.length > 0 && (
          <motion.section
            className={styles.section}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h2 className={styles.sectionTitle}>Что докупить</h2>
            <ul className={styles.ingredients}>
              {recipe.missing_ingredients.map((ing, i) => (
                <motion.li
                  key={i}
                  className={styles.ingredient}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + i * 0.05 }}
                >
                  <span className={styles.ingredientName}>{ing.name}</span>
                  <span className={styles.ingredientAmount}>
                    {formatAmount(ing.amount)} {ing.unit}
                  </span>
                </motion.li>
              ))}
            </ul>
          </motion.section>
        )}

        {recipe.instructions.length > 0 && (
          <motion.section
            className={styles.section}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h2 className={styles.sectionTitle}>Как готовить</h2>
            <ol className={styles.steps}>
              {recipe.instructions.map((step, i) => (
                <motion.li
                  key={step.number}
                  className={styles.step}
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 + i * 0.08 }}
                >
                  <span className={styles.stepNumber}>{step.number}</span>
                  <span className={styles.stepText}>{step.description}</span>
                </motion.li>
              ))}
            </ol>
          </motion.section>
        )}
      </div>
    </div>
  )
}

function formatAmount(amount) {
  if (Number.isInteger(amount)) return String(amount)
  return amount.toFixed(1).replace(/\.0$/, '')
}
