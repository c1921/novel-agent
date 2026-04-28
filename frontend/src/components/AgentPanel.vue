<script setup lang="ts">
import { reactive, ref } from 'vue'

import {
  answerQuestions,
  approveOutline,
  saveChapter,
  startChapter,
  type ConsistencyReport,
  type PlotQuestion,
} from '../api/agent'
import type { Chapter } from '../api/client'
import { getErrorMessage } from '../api/client'
import ConsistencyReportView from './ConsistencyReport.vue'
import QuestionCard from './QuestionCard.vue'

const props = defineProps<{
  projectId: number
  chapterId: number
  userGoal: string
}>()

const emit = defineEmits<{
  outline: [value: string]
  draft: [value: string]
  polished: [value: string]
  report: [value: ConsistencyReport]
  saved: [chapter: Chapter]
}>()

const sessionId = ref('')
const nextAction = ref('')
const questions = ref<PlotQuestion[]>([])
const autoDecidable = ref<string[]>([])
const consistencyReport = ref<ConsistencyReport | null>(null)
const answers = reactive<Record<string, string>>({})
const revisionInstruction = ref('')
const loading = ref(false)
const error = ref('')

async function runWithLoading(action: () => Promise<void>) {
  loading.value = true
  error.value = ''
  try {
    await action()
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    loading.value = false
  }
}

async function start() {
  if (!props.userGoal.trim()) {
    error.value = '请先输入本章目标。'
    return
  }
  await runWithLoading(async () => {
    const response = await startChapter({
      project_id: props.projectId,
      chapter_id: props.chapterId,
      user_goal: props.userGoal,
    })
    sessionId.value = response.session_id
    nextAction.value = response.next_action
    questions.value = response.plot_questions
    autoDecidable.value = response.auto_decidable
    consistencyReport.value = null
    for (const question of response.plot_questions) {
      answers[question.id] = question.options[0] ?? ''
    }
  })
}

async function submitAnswers() {
  if (!sessionId.value) return
  await runWithLoading(async () => {
    const response = await answerQuestions({
      session_id: sessionId.value,
      answers: questions.value.map((question) => ({
        question_id: question.id,
        answer: answers[question.id] ?? '',
      })),
    })
    nextAction.value = response.next_action
    emit('outline', response.chapter_outline)
  })
}

async function submitOutline(approved: boolean) {
  if (!sessionId.value) return
  await runWithLoading(async () => {
    const response = await approveOutline({
      session_id: sessionId.value,
      approved,
      revision_instruction: revisionInstruction.value,
    })
    nextAction.value = response.next_action
    if (!approved) {
      emit('outline', response.chapter_outline)
      revisionInstruction.value = ''
      return
    }
    emit('draft', response.draft)
    emit('polished', response.polished_draft)
    if (response.consistency_report) {
      consistencyReport.value = response.consistency_report
      emit('report', response.consistency_report)
    }
  })
}

async function persist(usePolished: boolean) {
  if (!sessionId.value) return
  await runWithLoading(async () => {
    const chapter = await saveChapter({
      session_id: sessionId.value,
      use_polished: usePolished,
    })
    nextAction.value = 'completed'
    emit('saved', chapter)
  })
}
</script>

<template>
  <aside class="panel sticky top-4">
    <div class="panel-header">Agent</div>
    <div class="panel-body grid gap-4">
      <p v-if="error" class="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
      <button class="btn btn-primary" :disabled="loading" @click="start">
        {{ loading ? '处理中...' : '开始创作' }}
      </button>

      <div v-if="nextAction" class="text-sm text-slate-600">下一步：{{ nextAction }}</div>
      <div v-if="autoDecidable.length" class="rounded border border-slate-200 bg-slate-50 p-3 text-sm">
        <div class="mb-1 font-semibold">Agent 可自动处理</div>
        <div>{{ autoDecidable.join('、') }}</div>
      </div>

      <section v-if="questions.length" class="grid gap-3">
        <QuestionCard
          v-for="question in questions"
          :key="question.id"
          v-model="answers[question.id]"
          :question="question"
        />
        <button class="btn btn-primary" :disabled="loading" @click="submitAnswers">提交回答并生成大纲</button>
      </section>

      <section v-if="sessionId" class="grid gap-2">
        <textarea v-model="revisionInstruction" class="form-textarea" placeholder="如果不批准大纲，填写修改要求" />
        <div class="flex flex-wrap gap-2">
          <button class="btn" :disabled="loading" @click="submitOutline(false)">要求修改大纲</button>
          <button class="btn btn-primary" :disabled="loading" @click="submitOutline(true)">批准大纲并生成正文</button>
        </div>
      </section>

      <section v-if="nextAction === 'review_draft'" class="grid gap-2">
        <button class="btn" :disabled="loading" @click="persist(false)">保存草稿</button>
        <button class="btn btn-primary" :disabled="loading" @click="persist(true)">保存润色稿</button>
      </section>

      <ConsistencyReportView :report="consistencyReport" />
    </div>
  </aside>
</template>
