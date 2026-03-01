<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>📊 数据集库</span>
          <el-input v-model="search" placeholder="搜索数据集..." clearable style="width:250px" @keyup.enter="load" />
        </div>
      </template>

      <div v-loading="loading">
        <div v-for="d in items" :key="d.id" class="ds-item">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
              <h4 style="margin:0 0 4px 0">{{ d.name }}</h4>
              <p v-if="d.description" style="color:#606266;margin:0 0 6px 0;line-height:1.6">{{ d.description }}</p>
              <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
                <el-tag v-if="d.data_type" size="small">{{ d.data_type }}</el-tag>
                <el-tag v-if="d.domain" size="small" type="success">{{ d.domain }}</el-tag>
                <span v-if="d.scale" style="color:#909399;font-size:12px">规模: {{ d.scale }}</span>
              </div>
            </div>
            <el-button size="small" link type="primary" @click="$router.push(`/articles/${d.source_article_id}`)">来源文章</el-button>
          </div>
          <div v-if="d.access_method" style="margin-top:6px;font-size:13px">
            <span style="color:#909399">获取方式：</span>{{ d.access_method }}
          </div>
          <el-link v-if="d.download_url" :href="d.download_url" target="_blank" type="primary" style="margin-top:4px">
            📥 下载链接
          </el-link>
          <el-divider />
        </div>
        <el-empty v-if="!loading && !items.length" description="暂无数据集" />
      </div>

      <el-pagination
        v-model:current-page="page" :page-size="20" :total="total"
        layout="total, prev, pager, next" style="justify-content:center"
        @current-change="load"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import client from '../api/client'

const items = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const search = ref('')
const loading = ref(false)

const load = async () => {
  loading.value = true
  try {
    const params: any = { skip: (page.value - 1) * 20, limit: 20 }
    if (search.value) params.q = search.value
    const resp = await client.get('/datasets/', { params })
    items.value = resp.data.items || []
    total.value = resp.data.total || 0
  } catch (e) { /* ignore */ }
  finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.ds-item { padding: 8px 0; }
</style>
