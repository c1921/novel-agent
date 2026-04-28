<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <header class="border-b border-slate-200 bg-white">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-5 py-3">
        <RouterLink class="text-lg font-semibold" to="/">Novel Agent MVP</RouterLink>
        <nav class="text-sm text-slate-600">
          <RouterLink class="hover:text-slate-950" to="/">项目</RouterLink>
        </nav>
      </div>
    </header>
    <main class="mx-auto max-w-7xl px-5 py-5">
      <RouterView />
    </main>
  </div>
</template>
