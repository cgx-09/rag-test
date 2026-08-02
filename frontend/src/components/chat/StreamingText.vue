<script setup lang="ts">
import { watch, nextTick, ref } from 'vue'

const props = defineProps<{
  text: string
}>()

const containerRef = ref<HTMLElement>()

// 自动滚动到底部
watch(() => props.text, async () => {
  await nextTick()
  if (containerRef.value) {
    containerRef.value.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }
})
</script>

<template>
  <div ref="containerRef" class="streaming-text markdown-body">
    {{ text }}
    <span class="cursor-blink">|</span>
  </div>
</template>

<style scoped>
.streaming-text {
  white-space: pre-wrap;
}

.cursor-blink {
  display: inline;
  color: var(--color-primary);
  font-weight: 700;
  animation: blink 0.8s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
</style>
