<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import type { Foreshadowing } from '../api/client'
import { getErrorMessage } from '../api/client'
import {
  createForeshadowing,
  deleteForeshadowing,
  updateForeshadowing,
  type ForeshadowingInput,
} from '../api/projects'

const props = defineProps<{
  projectId: number
  items: Foreshadowing[]
}>()

const emit = defineEmits<{
  refresh: []
}>()

const edited = ref<Foreshadowing[]>([])
const error = ref('')
const saving = ref(false)
const newItem = reactive<ForeshadowingInput>({
  name: '',
  setup: '',
  payoff_plan: '',
  status: 'planned',
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
    await createForeshadowing(props.projectId, { ...newItem })
    newItem.name = ''
    newItem.setup = ''
    newItem.payoff_plan = ''
    newItem.status = 'planned'
    emit('refresh')
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}

async function saveItem(item: Foreshadowing) {
  saving.value = true
  error.value = ''
  try {
    await updateForeshadowing(props.projectId, item.id, item)
    emit('refresh')
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}

async function removeItem(item: Foreshadowing) {
  saving.value = true
  error.value = ''
  try {
    await deleteForeshadowing(props.projectId, item.id)
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
    <div class="panel-header">伏笔</div>
    <div class="panel-body grid gap-4">
      <p v-if="error" class="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
      <form class="grid gap-2 md:grid-cols-[1fr_160px_auto]" @submit.prevent="createItem">
        <input v-model.trim="newItem.name" class="form-input" placeholder="伏笔名称" required />
        <select v-model="newItem.status" class="form-select">
          <option value="planned">planned</option>
          <option value="setup">setup</option>
          <option value="paid_off">paid_off</option>
        </select>
        <button class="btn btn-primary" :disabled="saving || !newItem.name">新增伏笔</button>
        <textarea v-model="newItem.setup" class="form-textarea md:col-span-3" placeholder="埋设方式" />
        <textarea v-model="newItem.payoff_plan" class="form-textarea md:col-span-3" placeholder="回收计划" />
      </form>

      <div v-for="item in edited" :key="item.id" class="grid gap-2 border-t border-slate-200 pt-4 md:grid-cols-[1fr_160px_auto]">
        <input v-model.trim="item.name" class="form-input" placeholder="伏笔名称" />
        <select v-model="item.status" class="form-select">
          <option value="planned">planned</option>
          <option value="setup">setup</option>
          <option value="paid_off">paid_off</option>
        </select>
        <div class="flex gap-2">
          <button class="btn" :disabled="saving" @click="saveItem(item)">保存</button>
          <button class="btn btn-danger" :disabled="saving" @click="removeItem(item)">删除</button>
        </div>
        <textarea v-model="item.setup" class="form-textarea md:col-span-3" placeholder="埋设方式" />
        <textarea v-model="item.payoff_plan" class="form-textarea md:col-span-3" placeholder="回收计划" />
      </div>
    </div>
  </section>
</template>
