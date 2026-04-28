import { defineStore } from 'pinia'

import { getErrorMessage } from '../api/client'
import type { Project, ProjectDetail } from '../api/client'
import { getProject, listProjects } from '../api/projects'

export const useProjectStore = defineStore('project', {
  state: () => ({
    projects: [] as Project[],
    currentProject: null as ProjectDetail | null,
    loading: false,
    error: '',
  }),
  actions: {
    async loadProjects() {
      this.loading = true
      this.error = ''
      try {
        this.projects = await listProjects()
      } catch (error) {
        this.error = getErrorMessage(error)
      } finally {
        this.loading = false
      }
    },
    async loadProject(projectId: number) {
      this.loading = true
      this.error = ''
      try {
        this.currentProject = await getProject(projectId)
      } catch (error) {
        this.error = getErrorMessage(error)
      } finally {
        this.loading = false
      }
    },
  },
})
