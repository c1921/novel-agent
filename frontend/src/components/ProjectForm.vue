<script setup lang="ts">
import { reactive, watch } from 'vue'

import type { Project } from '../api/client'
import type { ProjectInput } from '../api/projects'

const props = defineProps<{
  initial?: Partial<Project> | null
  submitLabel: string
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [payload: ProjectInput]
}>()

const form = reactive<ProjectInput>({
  title: '',
  genre: '',
  target_audience: '',
  style_guide: '',
})

watch(
  () => props.initial,
  (initial) => {
    form.title = initial?.title ?? ''
    form.genre = initial?.genre ?? ''
    form.target_audience = initial?.target_audience ?? ''
    form.style_guide = initial?.style_guide ?? ''
  },
  { immediate: true },
)

function submitForm() {
  emit('submit', { ...form })
}
</script>

<template>
  <form class="grid gap-3" @submit.prevent="submitForm">
    <label class="grid gap-1 text-sm font-medium">
      标题
      <input v-model.trim="form.title" class="form-input" required />
    </label>
    <div class="grid gap-3 md:grid-cols-2">
      <label class="grid gap-1 text-sm font-medium">
        类型
        <input v-model.trim="form.genre" class="form-input" placeholder="都市悬疑 / 奇幻 / 科幻" />
      </label>
      <label class="grid gap-1 text-sm font-medium">
        目标读者
        <input v-model.trim="form.target_audience" class="form-input" placeholder="成人读者 / 轻小说读者" />
      </label>
    </div>
    <label class="grid gap-1 text-sm font-medium">
      风格指南
      <textarea v-model="form.style_guide" class="form-textarea" placeholder="叙事节奏、语言风格、禁忌设定" />
    </label>
    <div>
      <button class="btn btn-primary" :disabled="loading || !form.title">
        {{ loading ? '处理中...' : submitLabel }}
      </button>
    </div>
  </form>
</template>
