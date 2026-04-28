import { apiClient } from './client'
import type {
  Character,
  Chapter,
  Foreshadowing,
  Outline,
  Project,
  ProjectDetail,
  WorldSetting,
} from './client'

export type ProjectInput = Pick<Project, 'title' | 'genre' | 'target_audience' | 'style_guide'>
export type CharacterInput = Omit<Character, 'id' | 'project_id'>
export type WorldSettingInput = Omit<WorldSetting, 'id' | 'project_id'>
export type OutlineInput = Omit<Outline, 'id' | 'project_id'>
export type ChapterInput = Omit<Chapter, 'id' | 'project_id' | 'created_at' | 'updated_at'>
export type ForeshadowingInput = Omit<Foreshadowing, 'id' | 'project_id'>

export async function listProjects(): Promise<Project[]> {
  const { data } = await apiClient.get<Project[]>('/projects')
  return data
}

export async function createProject(payload: ProjectInput): Promise<Project> {
  const { data } = await apiClient.post<Project>('/projects', payload)
  return data
}

export async function getProject(projectId: number): Promise<ProjectDetail> {
  const { data } = await apiClient.get<ProjectDetail>(`/projects/${projectId}`)
  return data
}

export async function updateProject(projectId: number, payload: Partial<ProjectInput>): Promise<Project> {
  const { data } = await apiClient.patch<Project>(`/projects/${projectId}`, payload)
  return data
}

export async function rebuildIndex(projectId: number): Promise<{ message: string }> {
  const { data } = await apiClient.post<{ message: string }>(`/projects/${projectId}/rebuild-index`)
  return data
}

export async function createCharacter(projectId: number, payload: CharacterInput): Promise<Character> {
  const { data } = await apiClient.post<Character>(`/projects/${projectId}/characters`, payload)
  return data
}

export async function updateCharacter(
  projectId: number,
  characterId: number,
  payload: Partial<CharacterInput>,
): Promise<Character> {
  const { data } = await apiClient.patch<Character>(
    `/projects/${projectId}/characters/${characterId}`,
    payload,
  )
  return data
}

export async function deleteCharacter(projectId: number, characterId: number): Promise<void> {
  await apiClient.delete(`/projects/${projectId}/characters/${characterId}`)
}

export async function createWorldSetting(
  projectId: number,
  payload: WorldSettingInput,
): Promise<WorldSetting> {
  const { data } = await apiClient.post<WorldSetting>(`/projects/${projectId}/worldbuilding`, payload)
  return data
}

export async function updateWorldSetting(
  projectId: number,
  settingId: number,
  payload: Partial<WorldSettingInput>,
): Promise<WorldSetting> {
  const { data } = await apiClient.patch<WorldSetting>(
    `/projects/${projectId}/worldbuilding/${settingId}`,
    payload,
  )
  return data
}

export async function deleteWorldSetting(projectId: number, settingId: number): Promise<void> {
  await apiClient.delete(`/projects/${projectId}/worldbuilding/${settingId}`)
}

export async function createOutline(projectId: number, payload: OutlineInput): Promise<Outline> {
  const { data } = await apiClient.post<Outline>(`/projects/${projectId}/outlines`, payload)
  return data
}

export async function updateOutline(
  projectId: number,
  outlineId: number,
  payload: Partial<OutlineInput>,
): Promise<Outline> {
  const { data } = await apiClient.patch<Outline>(`/projects/${projectId}/outlines/${outlineId}`, payload)
  return data
}

export async function deleteOutline(projectId: number, outlineId: number): Promise<void> {
  await apiClient.delete(`/projects/${projectId}/outlines/${outlineId}`)
}

export async function createChapter(projectId: number, payload: ChapterInput): Promise<Chapter> {
  const { data } = await apiClient.post<Chapter>(`/projects/${projectId}/chapters`, payload)
  return data
}

export async function updateChapter(
  projectId: number,
  chapterId: number,
  payload: Partial<ChapterInput>,
): Promise<Chapter> {
  const { data } = await apiClient.patch<Chapter>(`/projects/${projectId}/chapters/${chapterId}`, payload)
  return data
}

export async function deleteChapter(projectId: number, chapterId: number): Promise<void> {
  await apiClient.delete(`/projects/${projectId}/chapters/${chapterId}`)
}

export async function createForeshadowing(
  projectId: number,
  payload: ForeshadowingInput,
): Promise<Foreshadowing> {
  const { data } = await apiClient.post<Foreshadowing>(`/projects/${projectId}/foreshadowing`, payload)
  return data
}

export async function updateForeshadowing(
  projectId: number,
  itemId: number,
  payload: Partial<ForeshadowingInput>,
): Promise<Foreshadowing> {
  const { data } = await apiClient.patch<Foreshadowing>(
    `/projects/${projectId}/foreshadowing/${itemId}`,
    payload,
  )
  return data
}

export async function deleteForeshadowing(projectId: number, itemId: number): Promise<void> {
  await apiClient.delete(`/projects/${projectId}/foreshadowing/${itemId}`)
}
