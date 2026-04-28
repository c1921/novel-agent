import { apiClient } from './client'
import type { Chapter } from './client'

export interface PlotQuestion {
  id: string
  type: 'must_ask' | 'optional' | 'auto_decidable'
  question: string
  reason: string
  options: string[]
}

export interface QuestionAnswer {
  question_id: string
  answer: string
}

export interface ConsistencyIssue {
  severity: 'high' | 'medium' | 'low'
  type: 'character' | 'timeline' | 'worldbuilding' | 'plot' | 'foreshadowing' | 'style'
  description: string
  suggestion: string
}

export interface ConsistencyReport {
  summary: string
  issues: ConsistencyIssue[]
}

export interface StartChapterResponse {
  session_id: string
  next_action: string
  plot_questions: PlotQuestion[]
  auto_decidable: string[]
}

export interface AnswerQuestionsResponse {
  next_action: string
  chapter_outline: string
}

export interface ApproveOutlineResponse {
  next_action: string
  chapter_outline: string
  draft: string
  polished_draft: string
  consistency_report: ConsistencyReport | null
}

export async function startChapter(payload: {
  project_id: number
  chapter_id: number
  user_goal: string
}): Promise<StartChapterResponse> {
  const { data } = await apiClient.post<StartChapterResponse>('/agent/start-chapter', payload)
  return data
}

export async function answerQuestions(payload: {
  session_id: string
  answers: QuestionAnswer[]
}): Promise<AnswerQuestionsResponse> {
  const { data } = await apiClient.post<AnswerQuestionsResponse>('/agent/answer-questions', payload)
  return data
}

export async function approveOutline(payload: {
  session_id: string
  approved: boolean
  revision_instruction: string
}): Promise<ApproveOutlineResponse> {
  const { data } = await apiClient.post<ApproveOutlineResponse>('/agent/approve-outline', payload)
  return data
}

export async function saveChapter(payload: {
  session_id: string
  use_polished: boolean
}): Promise<Chapter> {
  const { data } = await apiClient.post<Chapter>('/agent/save-chapter', payload)
  return data
}
