import axios from 'axios'
import type { AxiosError } from 'axios'

export const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export function getErrorMessage(error: unknown): string {
  const axiosError = error as AxiosError<{ detail?: string }>
  return axiosError.response?.data?.detail || axiosError.message || '请求失败'
}

export interface Project {
  id: number
  title: string
  genre: string
  target_audience: string
  style_guide: string
  created_at: string
  updated_at: string
}

export interface Character {
  id: number
  project_id: number
  name: string
  role: string
  personality: string
  goal: string
  speech_style: string
  constraints: string
  background: string
}

export interface WorldSetting {
  id: number
  project_id: number
  title: string
  content: string
  category: string
}

export interface Outline {
  id: number
  project_id: number
  title: string
  content: string
}

export interface Chapter {
  id: number
  project_id: number
  chapter_number: number
  title: string
  goal: string
  outline: string
  draft: string
  polished_draft: string
  status: string
  created_at: string
  updated_at: string
}

export interface Foreshadowing {
  id: number
  project_id: number
  name: string
  setup: string
  payoff_plan: string
  status: string
}

export interface ProjectDetail extends Project {
  characters: Character[]
  world_settings: WorldSetting[]
  outlines: Outline[]
  chapters: Chapter[]
  foreshadowings: Foreshadowing[]
}
