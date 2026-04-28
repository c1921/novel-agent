<script setup lang="ts">
import { ref, onMounted } from "vue";

const msg = ref("loading...");

onMounted(async () => {
  const res = await fetch("/api/health");
  const data = await res.json();
  msg.value = JSON.stringify(data);
});

onMounted(() => {
  setTimeout(() => window.HSStaticMethods.autoInit(), 100)
});
</script>

<template>
  <h1>Backend says:</h1>
  <pre>{{ msg }}</pre>
</template>