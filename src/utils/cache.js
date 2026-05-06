const store = new Map()

function cacheKey(config) {
  const { method, url, params } = config
  return `${method || 'get'}:${url}:${JSON.stringify(params || {})}`
}

export function getCache(config) {
  const entry = store.get(cacheKey(config))
  if (!entry) return null
  if (Date.now() > entry.expiresAt) {
    store.delete(cacheKey(config))
    return null
  }
  return entry.data
}

export function setCache(config, data, ttl = 30000) {
  store.set(cacheKey(config), {
    data,
    expiresAt: Date.now() + ttl,
  })
}

export function clearCache(pattern = '') {
  if (!pattern) {
    store.clear()
    return
  }
  for (const key of store.keys()) {
    if (key.includes(pattern)) {
      store.delete(key)
    }
  }
}
