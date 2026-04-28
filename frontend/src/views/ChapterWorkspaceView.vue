<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import type { Chapter } from '../api/client'
import { getErrorMessage } from '../api/client'
import { updateChapter } from '../api/projects'
import AgentPanel from '../components/AgentPanel.vue'
import { useProjectStore } from '../stores/projectStore'

const route = useRoute()
const store = useProjectStore()
const projectId = computed(() => Number(route.params.projectId))
const chapterId = computed(() => Number(route.params.chapterId))
const project = computed(() => store.currentProject)
const chapter = computed(() => project.value?.chapters.find((item) => item.id === chapterId.value) ?? null)

const goal = ref('')
const chapterOutline = ref('')
const draft = ref('')
const polishedDraft = ref('')
const saving = ref(false)
const error = ref('')
const message = ref('')

function syncFromChapter(current: Chapter | null) {
  goal.value = current?.goal ?? ''
  chapterOutline.value = current?.outline ?? ''
  draft.value = current?.draft ?? ''
  polishedDraft.value = current?.polished_draft ?? ''
}

async function refresh() {
  await store.loadProject(projectId.value)
}

onMounted(refresh)

watch(chapter, syncFromChapter, { immediate: true })

async function saveManual() {
  if (!chapter.value) return
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    await updateChapter(projectId.value, chapter.value.id, {
      chapter_number: chapter.value.chapter_number,
      title: chapter.value.title,
      goal: goal.value,
      outline: chapterOutline.value,
      draft: draft.value,
      polished_draft: polishedDraft.value,
      status: chapter.value.status,
    })
    await refresh()
    message.value = '章节已保存。'
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}

function handleSaved(savedChapter: Chapter) {
  message.value = `已保存第 ${savedChapter.chapter_number} 章。`
  refresh()
}
</script>

<template>
  <div class="grid gap-5">
    <RouterLink class="text-sm text-slate-600 hover:text-slate-950" :to="`/projects/${projectId}`">返回项目详情</RouterLink>

    <p v-if="store.error" class="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ store.error }}</p>
    <p v-if="error" class="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
    <p v-if="message" class="rounded border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{{ message }}</p>

    <div v-if="store.loading" class="text-sm text-slate-500">加载中...</div>
    <div v-else-if="project && chapter" class="grid gap-5 xl:grid-cols-[280px_minmax(0,1fr)_360px]">
      <aside class="grid gap-4 self-start">
        <section class="panel">
          <div class="panel-header">{{ project.title }}</div>
          <div class="panel-body grid gap-2 text-sm">
            <div><span class="font-semibold">类型：</span>{{ project.genre || '未设置' }}</div>
            <div><span class="font-semibold">读者：</span>{{ project.target_audience || '未设置' }}</div>
            <div class="text-slate-600">{{ project.style_guide || '暂无风格指南。' }}</div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-header">人物</div>
          <div class="panel-body grid gap-2 text-sm">
            <div v-for="character in project.characters" :key="character.id">
              <span class="font-semibold">{{ character.name }}</span>
              <span class="text-slate-500"> / {{ character.role }}</span>
            </div>
            <div v-if="!project.characters.length" class="text-slate-500">暂无人物。</div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-header">世界观</div>
          <div class="panel-body grid gap-2 text-sm">
            <div v-for="setting in project.world_settings" :key="setting.id">
              <span class="font-semibold">{{ setting.title }}</span>
              <span class="text-slate-500"> / {{ setting.category || '未分类' }}</span>
            </div>
            <div v-if="!project.world_settings.length" class="text-slate-500">暂无设定。</div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-header">章节</div>
          <div class="panel-body grid gap-2 text-sm">
            <RouterLink
              v-for="item in project.chapters"
              :key="item.id"
              class="rounded border border-slate-200 px-3 py-2 hover:bg-slate-50"
              :class="{ 'border-blue-300 bg-blue-50': item.id === chapter.id }"
              :to="`/projects/${project.id}/chapters/${item.id}`"
            >
              第 {{ item.chapter_number }} 章 {{ item.title || '未命名' }}
            </RouterLink>
          </div>
        </section>
      </aside>

      <section class="grid gap-4">
        <div class="panel">
          <div class="panel-header">第 {{ chapter.chapter_number }} 章 {{ chapter.title || '未命名章节' }}</div>
          <div class="panel-body grid gap-3">
            <label class="grid gap-1 text-sm font-medium">
              本章目标
              <textarea v-model="goal" class="form-textarea" placeholder="本章希望完成的剧情推进" />
            </label>
            <label class="grid gap-1 text-sm font-medium">
              章节大纲
              <textarea v-model="chapterOutline" class="form-textarea min-h-56" />
            </label>
            <label class="grid gap-1 text-sm font-medium">
              正文草稿
              <textarea v-model="draft" class="form-textarea min-h-80" />
            </label>
            <label class="grid gap-1 text-sm font-medium">
              润色版本
              <textarea v-model="polishedDraft" class="form-textarea min-h-80" />
            </label>
            <div>
              <button class="btn" :disabled="saving" @click="saveManual">{{ saving ? '保存中...' : '手动保存' }}</button>
            </div>
          </div>
        </div>
      </section>

      <section class="grid gap-4 self-start">
        <AgentPanel
          :project-id="project.id"
          :chapter-id="chapter.id"
          :user-goal="goal"
          @outline="chapterOutline = $event"
          @draft="draft = $event"
          @polished="polishedDraft = $event"
          @saved="handleSaved"
        />
      </section>
    </div>

    <div v-else class="text-sm text-slate-500">未找到章节。</div>
  </div>
</template>
