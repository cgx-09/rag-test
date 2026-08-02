<script setup lang="ts">
import AppSidebar from '@/components/layout/AppSidebar.vue'
import ChatPanel from '@/components/chat/ChatPanel.vue'
</script>

<template>
  <div class="chat-view">
    <AppSidebar />
    <ChatPanel />
  </div>
</template>

<style scoped>
.chat-view {
  display: flex;
  height: 100%;
}
</style>
