<script setup lang="ts">
defineProps<{
  visible: boolean
  docName: string
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="overlay fade-in" @click.self="emit('cancel')">
      <div class="dialog card fade-in">
        <h3 class="dialog-title">确认删除</h3>
        <p class="dialog-desc">
          确定要删除 <strong>{{ docName }}</strong> 吗？该文档的向量索引也会被一并删除。
        </p>
        <div class="dialog-actions">
          <button class="btn btn-secondary" @click="emit('cancel')">取消</button>
          <button class="btn btn-danger" @click="emit('confirm')">确认删除</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.dialog {
  width: 400px;
  padding: var(--space-xl);
}

.dialog-title {
  font-size: 17px;
  font-weight: 700;
  margin-bottom: var(--space-sm);
}

.dialog-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-lg);
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
}
</style>
