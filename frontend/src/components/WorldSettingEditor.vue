<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import type { WorldSetting } from '../api/client'
import { getErrorMessage } from '../api/client'
import {
  createWorldSetting,
  deleteWorldSetting,
  updateWorldSetting,
  type WorldSettingInput,
} from '../api/projects'

const props = defineProps<{
  projectId: number
  items: WorldSetting[]
}>()

const emit = defineEmits<{
  refresh: []
}>()

const edited = ref<WorldSetting[]>([])
const error = ref('')
const saving = ref(false)
const newItem = reactive<WorldSettingInput>({
  title: '',
  content: '',
  category: '',
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
    await createWorldSetting(props.projectId, { ...newItem })
    newItem.title = ''
    newItem.content = ''
    newItem.category = ''
    emit('refresh')
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}

async function saveItem(item: WorldSetting) {
  saving.value = true
  error.value = ''
  try {
    await updateWorldSetting(props.projectId, item.id, item)
    emit('refresh')
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}

async function removeItem(item: WorldSetting) {
  saving.value = true
  error.value = ''
  try {
    await deleteWorldSetting(props.projectId, item.id)
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
    <div class="panel-header">世界观设定</div>
    <div class="panel-body grid gap-4">
      <p v-if="error" class="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
      <form class="grid gap-2 md:grid-cols-3" @submit.prevent="createItem">
        <input v-model.trim="newItem.title" class="form-input" placeholder="标题" required />
        <input v-model.trim="newItem.category" class="form-input" placeholder="分类" />
        <button class="btn btn-primary" :disabled="saving || !newItem.title">新增设定</button>
        <textarea v-model="newItem.content" class="form-textarea md:col-span-3" placeholder="设定内容" />
      </form>

      <div v-for="item in edited" :key="item.id" class="grid gap-2 border-t border-slate-200 pt-4 md:grid-cols-3">
        <input v-model.trim="item.title" class="form-input" placeholder="标题" />
        <input v-model.trim="item.category" class="form-input" placeholder="分类" />
        <div class="flex gap-2">
          <button class="btn" :disabled="saving" @click="saveItem(item)">保存</button>
          <button class="btn btn-danger" :disabled="saving" @click="removeItem(item)">删除</button>
        </div>
        <textarea v-model="item.content" class="form-textarea md:col-span-3" placeholder="设定内容" />
      </div>
    </div>
  </section>
</template>
