<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
import { dims } from '../format'
import BoxUnfold from '../components/BoxUnfold.vue'

const props = defineProps({ id: String })
const box = ref(null)
const form = ref({ length: '', width: '', height: '' })
const err = ref('')
const ok = ref('')
const busy = ref(false)

async function load() {
  box.value = await getJSON(`/api/boxes/${props.id}`)
  form.value = { length: box.value.length, width: box.value.width, height: box.value.height }
}

onMounted(async () => {
  try {
    await load()
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function save() {
  err.value = ''
  ok.value = ''
  const payload = {
    length: Number(form.value.length),
    width: Number(form.value.width),
    height: Number(form.value.height),
  }
  // 任一边 ≤ 0（或非数字）直接拦下，不发请求
  if (Object.values(payload).some((v) => !Number.isFinite(v) || v <= 0)) {
    err.value = '长宽高必须均为正数，已保留原合法尺寸。'
    form.value = { length: box.value.length, width: box.value.width, height: box.value.height }
    return
  }
  busy.value = true
  try {
    box.value = await putJSON(`/api/boxes/${props.id}`, payload)
    form.value = { length: box.value.length, width: box.value.width, height: box.value.height }
    ok.value = '三边已更新，算纸台再选此盒即按新尺寸出纸。'
  } catch (e) {
    err.value = `保存失败：${String(e.message || e)}，仍显示原合法尺寸。`
    form.value = { length: box.value.length, width: box.value.width, height: box.value.height }
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <p v-if="err && !box" class="bad">{{ err }}</p>
    <template v-else-if="box">
      <h1>{{ box.name }}</h1>
      <p class="lede">
        {{ dims(box) }}
        <span class="pill" :class="{ warn: box.data_quality === 'dirty' }">
          {{ box.data_quality === 'dirty' ? '脏数据' : '可用' }}
        </span>
      </p>
      <p v-if="box.data_quality === 'dirty'" class="bad">{{ box.note }}</p>

      <form class="dim-form" @submit.prevent="save">
        <label>长 (m)<input v-model.number="form.length" type="number" step="0.01" min="0" required /></label>
        <label>宽 (m)<input v-model.number="form.width" type="number" step="0.01" min="0" required /></label>
        <label>高 (m)<input v-model.number="form.height" type="number" step="0.01" min="0" required /></label>
        <button class="ribbon" :disabled="busy" type="submit">保存三边</button>
      </form>
      <p v-if="err" class="bad">{{ err }}</p>
      <p v-if="ok" class="ok">{{ ok }}</p>

      <BoxUnfold :l="box.length" :w="box.width" :h="box.height" />
      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn" to="/bench">用此盒去算纸</router-link>
        <router-link class="btn ghost" to="/boxes">返回清单</router-link>
      </div>
    </template>
  </div>
</template>
