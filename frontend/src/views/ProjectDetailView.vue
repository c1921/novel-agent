<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { getErrorMessage } from '../api/client'
import { rebuildIndex, updateProject, type ProjectInput } from '../api/projects'
import ChapterEditor from '../components/ChapterEditor.vue'
import CharacterEditor from '../components/CharacterEditor.vue'
import ForeshadowingEditor from '../components/ForeshadowingEditor.vue'
import OutlineEditor from '../components/OutlineEditor.vue'
import ProjectForm from '../components/ProjectForm.vue'
import WorldSettingEditor from '../components/WorldSettingEditor.vue'
import { useProjectStore } from '../stores/projectStore'

const route = useRoute()
const store = useProjectStore()
const saving = ref(false)
const actionMessage = ref('')
const actionError = ref('')
const projectId = computed(() => Number(route.params.projectId))
const project = computed(() => store.currentProject)

async function refresh() {
  await store.loadProject(projectId.value)
}

onMounted(refresh)

watch(projectId, () => {
  refresh()
})

async function handleUpdate(payload: ProjectInput) {
  saving.value = true
  actionError.value = ''
  actionMessage.value = ''
  try {
    await updateProject(projectId.value, payload)
    await refresh()
    actionMessage.value = '项目已保存。'
  } catch (caught) {
    actionError.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}

async function handleRebuildIndex() {
  saving.value = true
  actionError.value = ''
  actionMessage.value = ''
  try {
    const result = await rebuildIndex(projectId.value)
    actionMessage.value = result.message
  } catch (caught) {
    actionError.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="grid gap-5">
    <RouterLink class="text-sm text-slate-600 hover:text-slate-950" to="/">返回项目列表</RouterLink>

    <p v-if="store.error" class="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ store.error }}</p>
    <div v-if="store.loading" class="text-sm text-slate-500">加载中...</div>

    <template v-if="project">
      <section class="panel">
        <div class="panel-header flex items-center justify-between gap-3">
          <span>项目设置</span>
          <button class="btn" :disabled="saving" @click="handleRebuildIndex">重建知识库</button>
        </div>
        <div class="panel-body grid gap-3">
          <p v-if="actionError" class="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ actionError }}</p>
          <p v-if="actionMessage" class="rounded border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {{ actionMessage }}
          </p>
          <ProjectForm :initial="project" submit-label="保存项目" :loading="saving" @submit="handleUpdate" />
        </div>
      </section>

      <CharacterEditor :project-id="project.id" :items="project.characters" @refresh="refresh" />
      <WorldSettingEditor :project-id="project.id" :items="project.world_settings" @refresh="refresh" />
      <OutlineEditor :project-id="project.id" :items="project.outlines" @refresh="refresh" />
      <ForeshadowingEditor :project-id="project.id" :items="project.foreshadowings" @refresh="refresh" />
      <ChapterEditor :project-id="project.id" :items="project.chapters" @refresh="refresh" />
    </template>
  </div>
</template>
