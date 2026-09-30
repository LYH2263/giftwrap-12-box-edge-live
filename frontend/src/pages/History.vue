<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import { dims } from '../format'

const items = ref([])
const err = ref('')

onMounted(async () => {
  try {
    items.value = (await getJSON('/api/runs')).items
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="lede">算纸页「写入用纸档」后的落库结果：每条保留写入时三边快照与面积，主数据再改也不覆盖。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id">
        <router-link :to="`/history/${r.id}`">{{ r.result?.box_name ?? r.box_name }} #{{ r.id }}</router-link>
        <span class="meta">
          {{ r.result ? dims(r.result) : '—' }} ｜ {{ r.result?.paper_m2 ?? '—' }} m²
        </span>
      </li>
    </ul>
  </div>
</template>
