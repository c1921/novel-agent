<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import type { Chapter } from '../api/client'
import { getErrorMessage } from '../api/client'
import { createChapter, deleteChapter, updateChapter, type ChapterInput } from '../api/projects'

const props = defineProps<{
  projectId: number
  items: Chapter[]
}>()

const emit = defineEmits<{
  refresh: []
}>()

const edited = ref<Chapter[]>([])
const error = ref('')
const saving = ref(false)
const nextNumber = computed(() => Math.max(0, ...props.items.map((item) => item.chapter_number)) + 1)
const newItem = reactive<ChapterInput>({
  chapter_number: 1,
  title: '',
  goal: '',
  outline: '',
  draft: '',
  polished_draft: '',
  status: 'planned',
})

watch(
  () => props.items,
  (items) => {
    edited.value = items.map((item) => ({ ...item }))
    newItem.chapter_number = nextNumber.value
  },
  { immediate: true, deep: true },
)

async function createItem() {
  saving.value = true
  error.value = ''
  try {
    await createChapter(props.projectId, { ...newItem, chapter_number: nextNumber.value })
    newItem.title = ''
    newItem.goal = ''
    newItem.outline = ''
    newItem.draft = ''
    newItem.polished_draft = ''
    newItem.status = 'planned'
    emit('refresh')
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}

async function saveItem(item: Chapter) {
  saving.value = true
  error.value = ''
  try {
    await updateChapter(props.projectId, item.id, item)
    emit('refresh')
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}

async function removeItem(item: Chapter) {
  saving.value = true
  error.value = ''
  try {
    await deleteChapter(props.projectId, item.id)
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
    <div class="panel-header">章节</div>
    <div class="panel-body grid gap-4">
      <p v-if="error" class="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
      <form class="grid gap-2 md:grid-cols-[100px_1fr_auto]" @submit.prevent="createItem">
        <input class="form-input" :value="nextNumber" disabled />
        <input v-model.trim="newItem.title" class="form-input" placeholder="章节标题" />
        <button class="btn btn-primary" :disabled="saving">新增章节</button>
        <textarea v-model="newItem.goal" class="form-textarea md:col-span-3" placeholder="章节目标" />
      </form>

      <div v-for="item in edited" :key="item.id" class="grid gap-2 border-t border-slate-200 pt-4 md:grid-cols-[90px_1fr_140px]">
        <input v-model.number="item.chapter_number" class="form-input" />
        <input v-model.trim="item.title" class="form-input" placeholder="标题" />
        <select v-model="item.status" class="form-select">
          <option value="planned">planned</option>
          <option value="planning">planning</option>
          <option value="saved">saved</option>
        </select>
        <textarea v-model="item.goal" class="form-textarea md:col-span-3" placeholder="目标" />
        <div class="flex flex-wrap gap-2 md:col-span-3">
          <RouterLink class="btn btn-primary" :to="`/projects/${projectId}/chapters/${item.id}`">工作台</RouterLink>
          <button class="btn" :disabled="saving" @click="saveItem(item)">保存</button>
          <button class="btn btn-danger" :disabled="saving" @click="removeItem(item)">删除</button>
        </div>
      </div>
    </div>
  </section>
</template>
