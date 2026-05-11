import { ref, computed } from 'vue'

const mobileQuery = window.matchMedia('(max-width: 767px)')
const tabletQuery = window.matchMedia('(min-width: 768px) and (max-width: 1024px)')

const isMobile = ref(mobileQuery.matches)
const isTablet = ref(tabletQuery.matches)
const isDesktop = computed(() => !isMobile.value && !isTablet.value)
const screenSize = computed(() => {
  if (isMobile.value) return 'mobile'
  if (isTablet.value) return 'tablet'
  return 'desktop'
})

mobileQuery.addEventListener('change', (e) => { isMobile.value = e.matches })
tabletQuery.addEventListener('change', (e) => { isTablet.value = e.matches })

const width = ref(window.innerWidth)
let resizeTimer = null
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => { width.value = window.innerWidth }, 150)
})

export { isMobile, isTablet, isDesktop, screenSize, width }
