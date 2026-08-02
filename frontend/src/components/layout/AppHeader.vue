<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

const navItems = [
  { path: '/chat', label: '💬 对话' },
  { path: '/upload', label: '📤 上传' },
  { path: '/docs', label: '📋 文档管理' },
]

const currentLabel = computed(() => {
  const item = navItems.find((n) => n.path === route.path)
  return item ? item.label : ''
})
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <router-link to="/" class="logo">
        <span class="logo-icon">🧠</span>
        <span class="logo-text">企业知识库助手</span>
      </router-link>
    </div>

    <nav class="header-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-link"
        :class="{ active: route.path === item.path }"
      >
        {{ item.label }}
      </router-link>
    </nav>

    <div class="header-right">
      <span class="current-page">{{ currentLabel }}</span>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 var(--space-lg);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  text-decoration: none;
  color: var(--color-text);
}

.logo-icon {
  font-size: 22px;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
}

.header-nav {
  display: flex;
  gap: 4px;
}

.nav-link {
  padding: 6px 16px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.nav-link:hover {
  color: var(--color-text);
  background: var(--color-border-light);
}

.nav-link.active {
  color: var(--color-primary);
  background: var(--color-primary-bg);
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
}

.current-page {
  font-size: 13px;
  color: var(--color-text-muted);
}
</style>
