<script setup lang="ts">
import type { ConsistencyReport } from '../api/agent'

defineProps<{
  report: ConsistencyReport | null
}>()

function severityClass(severity: string) {
  if (severity === 'high') return 'border-red-200 bg-red-50 text-red-800'
  if (severity === 'medium') return 'border-amber-200 bg-amber-50 text-amber-800'
  return 'border-slate-200 bg-slate-50 text-slate-700'
}
</script>

<template>
  <section class="grid gap-3">
    <p v-if="!report" class="text-sm text-slate-500">暂无一致性检查报告。</p>
    <template v-else>
      <p class="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm">{{ report.summary }}</p>
      <div v-if="!report.issues.length" class="text-sm text-slate-500">未发现问题。</div>
      <div
        v-for="issue in report.issues"
        :key="`${issue.severity}-${issue.type}-${issue.description}`"
        class="rounded border p-3 text-sm"
        :class="severityClass(issue.severity)"
      >
        <div class="mb-1 font-semibold">{{ issue.severity }} / {{ issue.type }}</div>
        <p>{{ issue.description }}</p>
        <p class="mt-1">建议：{{ issue.suggestion }}</p>
      </div>
    </template>
  </section>
</template>
