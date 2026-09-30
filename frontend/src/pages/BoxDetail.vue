<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, patchJSON } from '../api'
import { fmtDims } from '../format'
import BoxUnfold from '../components/BoxUnfold.vue'

const props = defineProps({ id: String })
const box = ref(null)
const form = ref({ length: '', width: '', height: '' })
const err = ref('')
const saveErr = ref('')
const saved = ref(false)
const busy = ref(false)

function syncForm() {
  // 表单以服务器真相为基准；仅保存成功后才会随 box 一起更新。
  form.value = {
    length: Number(box.value.length).toFixed(2),
    width: Number(box.value.width).toFixed(2),
    height: Number(box.value.height).toFixed(2),
  }
}

async function load() {
  err.value = ''
  try {
    box.value = await getJSON(`/api/boxes/${props.id}`)
    syncForm()
  } catch (e) {
    err.value = String(e.message || e)
  }
}

async function save() {
  saveErr.value = ''
  saved.value = false
  const v = {
    length: Number(form.value.length),
    width: Number(form.value.width),
    height: Number(form.value.height),
  }
  if (Object.values(v).some((x) => !Number.isFinite(x) || x <= 0)) {
    saveErr.value = '长宽高必须为正数，不能为空或 ≤ 0'
    return
  }
  busy.value = true
  try {
    box.value = await patchJSON(`/api/boxes/${props.id}`, v) // 成功才替换真相
    syncForm()
    saved.value = true
  } catch (e) {
    // 失败：box 未改动，摘要/展开仍是原合法尺寸；表单回退到原值。
    syncForm()
    saveErr.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="box">
      <h1>{{ box.name }}</h1>
      <p class="lede">
        {{ fmtDims(box.length, box.width, box.height) }}
        <span class="pill" :class="{ warn: box.data_quality === 'dirty' }">
          {{ box.data_quality === 'dirty' ? '脏数据' : '可用' }}
        </span>
      </p>
      <p v-if="box.data_quality === 'dirty'" class="bad">{{ box.note }}</p>
      <BoxUnfold :l="box.length" :w="box.width" :h="box.height" />

      <div class="dim-form">
        <p class="unfold-title">修改长宽高（米）</p>
        <div class="row">
          <label>长 <input v-model="form.length" type="number" step="any" inputmode="decimal" /></label>
          <label>宽 <input v-model="form.width" type="number" step="any" inputmode="decimal" /></label>
          <label>高 <input v-model="form.height" type="number" step="any" inputmode="decimal" /></label>
          <button :disabled="busy" @click="save">保存尺寸</button>
        </div>
        <p v-if="saveErr" class="bad">{{ saveErr }}</p>
        <p v-else-if="saved" class="saved">已保存，算纸台再选本盒即按新三边试算。</p>
      </div>

      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn" to="/bench">用此盒去算纸</router-link>
        <router-link class="btn ghost" to="/boxes">返回清单</router-link>
      </div>
    </template>
  </div>
</template>
