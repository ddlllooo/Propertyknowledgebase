import { computed } from 'vue'
import { isMobile, isTablet } from './useBreakpoint'

export function useDialogWidth(desktopPx) {
  return computed(() => {
    if (isMobile.value) return '90vw'
    if (isTablet.value) return Math.min(desktopPx, 80) + 'vw'
    return desktopPx + 'px'
  })
}
