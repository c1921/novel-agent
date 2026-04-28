<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getErrorMessage } from '../api/client'
import { createProject, type ProjectInput } from '../api/projects'
import ProjectForm from '../components/ProjectForm.vue'
import { useProjectStore } from '../stores/projectStore'

const store = useProjectStore()
const saving = ref(false)
const error = ref('')

onMounted(() => {
  store.loadProjects()
})

async function handleCreate(payload: ProjectInput) {
  saving.value = true
  error.value = ''
  try {
    await createProject(payload)
    await store.loadProjects()
  } catch (caught) {
    error.value = getErrorMessage(caught)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="grid gap-5 lg:grid-cols-[380px_1fr]">
    <section class="panel">
      <div class="panel-header">创建项目</div>
      <div class="panel-body">
        <p v-if="error" class="mb-3 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
        <ProjectForm submit-label="创建项目" :loading="saving" @submit="handleCreate" />
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">项目列表</div>
      <div class="panel-body">
        <p v-if="store.error" class="mb-3 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {{ store.error }}
        </p>
        <div v-if="store.loading" class="text-sm text-slate-500">加载中...</div>
        <div v-else-if="!store.projects.length" class="text-sm text-slate-500">暂无项目。</div>
        <div v-else class="grid gap-3">
          <RouterLink
            v-for="project in store.projects"
            :key="project.id"
            class="block rounded border border-slate-200 p-4 hover:border-blue-300 hover:bg-blue-50"
            :to="`/projects/${project.id}`"
          >
            <div class="flex items-center justify-between gap-3">
              <h2 class="font-semibold">{{ project.title }}</h2>
              <span class="text-xs text-slate-500">{{ project.genre || '未设置类型' }}</span>
            </div>
            <p class="mt-2 line-clamp-2 text-sm text-slate-600">
              {{ project.style_guide || '尚未填写风格指南。' }}
            </p>
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>
