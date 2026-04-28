<script setup lang="ts">
import type { PlotQuestion } from '../api/agent'

defineProps<{
  question: PlotQuestion
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

function choose(option: string) {
  emit('update:modelValue', option)
}
</script>

<template>
  <div class="rounded border border-slate-200 bg-white p-3">
    <div class="mb-2 flex items-center gap-2">
      <span class="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">{{ question.type }}</span>
      <span class="text-xs text-slate-500">{{ question.id }}</span>
    </div>
    <p class="font-semibold">{{ question.question }}</p>
    <p v-if="question.reason" class="mt-1 text-sm text-slate-600">{{ question.reason }}</p>
    <div v-if="question.options.length" class="mt-3 flex flex-wrap gap-2">
      <button
        v-for="option in question.options"
        :key="option"
        class="btn"
        :class="{ 'btn-primary': modelValue === option }"
        @click="choose(option)"
      >
        {{ option }}
      </button>
    </div>
    <textarea
      class="form-textarea mt-3"
      :value="modelValue"
      placeholder="也可以输入自定义回答"
      @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    />
  </div>
</template>
