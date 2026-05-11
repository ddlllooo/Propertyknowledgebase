<template>
  <el-config-provider :size="elSize">
    <router-view />
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { isMobile } from './composables/useBreakpoint'

const elSize = computed(() => (isMobile.value ? 'small' : 'default'))
</script>
