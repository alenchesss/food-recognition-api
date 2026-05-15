import { getMockResponse } from './mock.js'

const API_BASE = import.meta.env.VITE_API_BASE || ''
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

export async function recognizeFood(file) {
  if (USE_MOCK) {
    console.log('[client] MOCK MODE — returning fake data')
    return getMockResponse()
  }

  const formData = new FormData()
  formData.append('image', file)

  const url = `${API_BASE}/api/v1/recognize`
  console.log('[client] POST', url)

  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  })

  console.log('[client] response.status:', response.status)

  const rawText = await response.text()

  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const data = JSON.parse(rawText)
      if (data?.detail) detail = data.detail
    } catch {
      /* пустой/невалидный JSON — оставим дефолтный текст */
    }
    throw new Error(detail)
  }

  try {
    return JSON.parse(rawText)
  } catch (err) {
    console.error('[client] cannot parse response as JSON:', err)
    throw new Error('Сервер вернул не-JSON')
  }
}
