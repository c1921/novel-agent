import { createRouter, createWebHistory } from 'vue-router'

import ChapterWorkspaceView from '../views/ChapterWorkspaceView.vue'
import ProjectDetailView from '../views/ProjectDetailView.vue'
import ProjectListView from '../views/ProjectListView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'projects', component: ProjectListView },
    { path: '/projects/:projectId', name: 'project-detail', component: ProjectDetailView },
    {
      path: '/projects/:projectId/chapters/:chapterId',
      name: 'chapter-workspace',
      component: ChapterWorkspaceView,
    },
  ],
})

export default router
