import { motion } from 'framer-motion'
import styles from './RecipeGrid.module.css'

export default function RecipeGrid({ data, onSelect, onReset }) {
  const recipes = data?.recipes ?? []
  const ingredients = data?.detected_ingredients ?? []

  return (
    <div className={styles.wrapper}>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className={styles.header}
      >
        <h2 className={styles.title}>
          На фото нашлось — <em>{ingredients.length}</em>
        </h2>
        {ingredients.length > 0 && (
          <div className={styles.tags}>
            {ingredients.map((ing, i) => (
              <motion.span
                key={i}
                initial={{ opacity: 0, scale: 0.85, y: 8 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ delay: 0.15 + i * 0.04 }}
                className={styles.tag}
              >
                {ing.name}
              </motion.span>
            ))}
          </div>
        )}
        <button className={styles.reset} onClick={onReset}>
          ← другая фотография
        </button>
      </motion.div>

      {recipes.length === 0 ? (
        <div className={styles.empty}>
          К сожалению, рецептов не нашлось. Попробуй другое фото.
        </div>
      ) : (
        <div className={styles.grid}>
          {recipes.map((recipe, i) => (
            <RecipeCard
              key={recipe.id}
              recipe={recipe}
              index={i}
              onClick={() => onSelect(recipe)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function RecipeCard({ recipe, index, onClick }) {
  return (
    <motion.button
      className={styles.card}
      onClick={onClick}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 + index * 0.1, duration: 0.5 }}
      whileHover={{ y: -8 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className={styles.imageWrap}>
        {recipe.image ? (
          <img
            src={recipe.image}
            alt={recipe.title}
            className={styles.image}
            loading="lazy"
          />
        ) : (
          <div className={styles.imagePlaceholder}>
            <span>нет фото</span>
          </div>
        )}
        <div className={styles.imageOverlay} />
      </div>

      <div className={styles.cardBody}>
        <h3 className={styles.cardTitle}>{recipe.title}</h3>
        <div className={styles.cardMeta}>
          <span>{recipe.used_ingredients_count} есть</span>
          <span className={styles.dot}>·</span>
          <span>{recipe.missing_ingredients.length} нужно</span>
        </div>
        <div className={styles.cardArrow}>→</div>
      </div>
    </motion.button>
  )
}
