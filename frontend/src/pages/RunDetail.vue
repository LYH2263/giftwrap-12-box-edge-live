<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import { fmtDims } from '../format'

const props = defineProps({ id: String })
const run = ref(null)
const err = ref('')
const verify = ref(null)
const verifyErr = ref('')
const busy = ref(false)

async function replay() {
  verifyErr.value = ''
  verify.value = null
  busy.value = true
  try {
    verify.value = await postJSON(`/api/runs/${props.id}/verify`, {})
  } catch (e) {
    verifyErr.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})

const rows = [
  { key: 'box_surface', label: '盒表面积', unit: 'm²' },
  { key: 'paper_m2', label: '用纸面积', unit: 'm²' },
  { key: 'ribbon_m', label: '丝带长度', unit: 'm' },
]
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>用纸档 #{{ run.id }}</h1>
      <p class="lede">
        {{ run.box_name }}
        <span v-if="run.has_snapshot">· 写入时三边 {{ fmtDims(run.length, run.width, run.height) }}</span>
        <span v-else class="pill warn">旧档无三边快照</span>
      </p>

      <ul class="item-list">
        <li><span>折边系数 overlap</span><span class="meta">{{ run.overlap }}</span></li>
        <li><span>丝带绕法 wrap_style</span><span class="meta">{{ run.wrap_style ?? run.result?.ribbon?.wrap_style }}</span></li>
        <li><span>盒表面积</span><span class="meta">{{ run.result?.box_surface ?? '—' }} m²</span></li>
        <li><span>用纸面积</span><span class="meta">{{ run.result?.paper_m2 ?? '—' }} m²</span></li>
        <li><span>丝带长度</span><span class="meta">{{ run.result?.ribbon?.ribbon_m ?? '—' }} m</span></li>
        <li><span>写入时间</span><span class="meta">{{ run.created_at }}</span></li>
      </ul>

      <div class="row" style="margin-top: 1.25rem">
        <button v-if="run.has_snapshot" :disabled="busy" @click="replay">用写入时三边干算</button>
        <router-link class="btn ghost" to="/history">返回用纸档</router-link>
      </div>
      <p v-if="verifyErr" class="bad">{{ verifyErr }}</p>

      <div v-if="verify" class="result-board">
        <p class="stat-line">
          干算三边 {{ fmtDims(verify.dims.length, verify.dims.width, verify.dims.height) }}
          · overlap {{ verify.overlap }} · {{ verify.wrap_style }}
        </p>
        <ul class="item-list">
          <li v-for="row in rows" :key="row.key">
            <span>{{ row.label }}</span>
            <span class="meta">
              存档 {{ verify.stored[row.key] }} · 重算 {{ verify.recomputed[row.key] }} {{ row.unit }}
              <strong :class="verify.matches[row.key] ? 'ok-mark' : 'bad'">
                {{ verify.matches[row.key] ? '✓ 一致' : '✗ 不符' }}
              </strong>
            </span>
          </li>
        </ul>
        <p class="stat-line">
          互证结论：
          <strong :class="verify.all_match ? 'ok-mark' : 'bad'">
            {{ verify.all_match ? '全部一致，回看与干算互证通过' : '存在不符项' }}
          </strong>
        </p>
      </div>
    </template>
  </div>
</template>
