<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import type { Character } from '../api/client'
import { getErrorMessage } from '../api/client'
import {
  createCharacter,
  deleteCharacter,
  updateCharacter,
  type CharacterInput,
} from '../api/projects'

const props = defineProps<{
  projectId: number
  items: Character[]
}>()

const emit = defineEmits<{
  refresh: []
}>()

const edited = ref<Character[]>([])
const error = ref('')
const saving = ref(false)
const newItem = reactive<CharacterInput>({
  name: '',
  role: '',
  personality: '',
  goal: '',
  speech_style: '',
  constraints: '',
  background: '',
})

watch(
  () => props.items,
  (items) => {
    edited.value = items.map((item) => ({ ...item }))
  },
  { immediate: true, deep: true },
)

function resetNewItem() {
  newItem.name = ''
  newItem.role = ''
  newItem.personality = ''
  newItem.goal = ''
  newItem.speech_style = ''
  newItem.constraints = ''
  newItem.background = ''
}

async function createItem() {
  saving.value = true
  error.value = ''
  try {
    await createCharacter(props.projectId, { ...newItem })
    resetNewItem()
    emit('refresh')
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}

async function saveItem(item: Character) {
  saving.value = true
  error.value = ''
  try {
    await updateCharacter(props.projectId, item.id, item)
    emit('refresh')
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}

async function removeItem(item: Character) {
  saving.value = true
  error.value = ''
  try {
    await deleteCharacter(props.projectId, item.id)
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
    <div class="panel-header">人物卡</div>
    <div class="panel-body grid gap-4">
      <p v-if="error" class="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
      <form class="grid gap-2 md:grid-cols-2" @submit.prevent="createItem">
        <input v-model.trim="newItem.name" class="form-input" placeholder="姓名" required />
        <input v-model.trim="newItem.role" class="form-input" placeholder="角色定位" />
        <textarea v-model="newItem.personality" class="form-textarea md:col-span-2" placeholder="性格" />
        <textarea v-model="newItem.goal" class="form-textarea md:col-span-2" placeholder="目标" />
        <textarea v-model="newItem.speech_style" class="form-textarea md:col-span-2" placeholder="说话风格" />
        <textarea v-model="newItem.constraints" class="form-textarea md:col-span-2" placeholder="约束" />
        <textarea v-model="newItem.background" class="form-textarea md:col-span-2" placeholder="背景" />
        <button class="btn btn-primary md:col-span-2" :disabled="saving || !newItem.name">新增人物</button>
      </form>

      <div v-for="item in edited" :key="item.id" class="grid gap-2 border-t border-slate-200 pt-4 md:grid-cols-2">
        <input v-model.trim="item.name" class="form-input" placeholder="姓名" />
        <input v-model.trim="item.role" class="form-input" placeholder="角色定位" />
        <textarea v-model="item.personality" class="form-textarea md:col-span-2" placeholder="性格" />
        <textarea v-model="item.goal" class="form-textarea md:col-span-2" placeholder="目标" />
        <textarea v-model="item.speech_style" class="form-textarea md:col-span-2" placeholder="说话风格" />
        <textarea v-model="item.constraints" class="form-textarea md:col-span-2" placeholder="约束" />
        <textarea v-model="item.background" class="form-textarea md:col-span-2" placeholder="背景" />
        <div class="flex gap-2 md:col-span-2">
          <button class="btn" :disabled="saving" @click="saveItem(item)">保存</button>
          <button class="btn btn-danger" :disabled="saving" @click="removeItem(item)">删除</button>
        </div>
      </div>
    </div>
  </section>
</template>
