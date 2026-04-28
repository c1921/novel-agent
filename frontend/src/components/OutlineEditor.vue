<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import type { Outline } from '../api/client'
import { getErrorMessage } from '../api/client'
import { createOutline, deleteOutline, updateOutline, type OutlineInput } from '../api/projects'

const props = defineProps<{
  projectId: number
  items: Outline[]
}>()

const emit = defineEmits<{
  refresh: []
}>()

const edited = ref<Outline[]>([])
const error = ref('')
const saving = ref(false)
const newItem = reactive<OutlineInput>({
  title: '',
  content: '',
})

watch(
  () => props.items,
  (items) => {
    edited.value = items.map((item) => ({ ...item }))
  },
  { immediate: true, deep: true },
)

async function createItem() {
  saving.value = true
  error.value = ''
  try {
    await createOutline(props.projectId, { ...newItem })
    newItem.title = ''
    newItem.content = ''
    emit('refresh')
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}

async function saveItem(item: Outline) {
  saving.value = true
  error.value = ''
  try {
    await updateOutline(props.projectId, item.id, item)
    emit('refresh')
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}

async function removeItem(item: Outline) {
  saving.value = true
  error.value = ''
  try {
    await deleteOutline(props.projectId, item.id)
    emit('refresh')
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <section class="panel">
    <div class="panel-header">大纲</div>
    <div class="panel-body grid gap-4">
      <p v-if="error" class="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
      <form class="grid gap-2 md:grid-cols-[1fr_auto]" @submit.prevent="createItem">
        <input v-model.trim="newItem.title" class="form-input" placeholder="大纲标题" required />
        <button class="btn btn-primary" :disabled="saving || !newItem.title">新增大纲</button>
        <textarea v-model="newItem.content" class="form-textarea md:col-span-2" placeholder="大纲内容" />
      </form>

      <div v-for="item in edited" :key="item.id" class="grid gap-2 border-t border-slate-200 pt-4 md:grid-cols-[1fr_auto]">
        <input v-model.trim="item.title" class="form-input" placeholder="大纲标题" />
        <div class="flex gap-2">
          <button class="btn" :disabled="saving" @click="saveItem(item)">保存</button>
          <button class="btn btn-danger" :disabled="saving" @click="removeItem(item)">删除</button>
        </div>
        <textarea v-model="item.content" class="form-textarea md:col-span-2" placeholder="大纲内容" />
      </div>
    </div>
  </section>
</template>
