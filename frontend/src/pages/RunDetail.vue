<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import { dims } from '../format'

const props = defineProps({ id: String })
const run = ref(null)
const replay = ref(null)
const err = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function replayCalc() {
  err.value = ''
  busy.value = true
  try {
    replay.value = await getJSON(`/api/runs/${props.id}/replay`)
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <p v-if="err && !run" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>用纸档 #{{ run.id }}</h1>
      <p class="lede">
        {{ run.result.box_name }} ｜ 折边系数 ×{{ run.result.overlap }}
      </p>

      <ul class="item-list">
        <li>
          <span>写入时三边（快照）</span>
          <span class="meta">{{ dims(run.result) }}</span>
        </li>
        <li>
          <span>归档用纸面积</span>
          <span class="meta">{{ run.result.paper_m2 }} m²</span>
        </li>
        <li>
          <span>归档丝带长度（{{ run.result.ribbon.wrap_style === 'band' ? '带状' : '十字' }}）</span>
          <span class="meta">{{ run.result.ribbon.ribbon_m }} m</span>
        </li>
        <li v-if="run.cur_length != null">
          <span>当前主数据三边</span>
          <span class="meta">{{ dims({ length: run.cur_length, width: run.cur_width, height: run.cur_height }) }}</span>
        </li>
      </ul>

      <div class="row" style="margin-top: 1.25rem">
        <button :disabled="busy" @click="replayCalc">用写入时三边再干算</button>
        <router-link class="btn ghost" to="/history">返回用纸档</router-link>
      </div>
      <p v-if="err" class="bad">{{ err }}</p>

      <div v-if="replay" class="result-board">
        <ul class="item-list">
          <li>
            <span>回看归档</span>
            <span class="meta">
              {{ replay.stored.paper_m2 }} m² ｜ 丝带 {{ replay.stored.ribbon_m }} m
            </span>
          </li>
          <li>
            <span>快照复算</span>
            <span class="meta">
              {{ replay.replay.paper_m2 }} m² ｜ 丝带 {{ replay.replay.ribbon_m }} m
            </span>
          </li>
        </ul>
        <p :class="replay.matches ? 'ok' : 'bad'" style="margin-top: 0.85rem; font-weight: 700">
          {{ replay.matches ? '✓ 复算与归档互证一致（历史面积不受主数据改动影响）' : '✗ 复算与归档不一致' }}
        </p>
      </div>
    </template>
  </div>
</template>
