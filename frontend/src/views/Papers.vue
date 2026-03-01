<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>📄 论文库</span>
          <el-input v-model="search" placeholder="搜索论文..." clearable style="width:250px" @keyup.enter="load" />
        </div>
      </template>

      <el-table :data="items" v-loading="loading" style="width:100%">
        <el-table-column prop="title" label="论文标题" min-width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <div>
              <div style="font-weight:500">{{ row.title }}</div>
              <div v-if="row.title_cn" style="color:#606266;font-size:13px">{{ row.title_cn }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="作者" width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ (row.authors || []).join(', ') }}</template>
        </el-table-column>
        <el-table-column prop="journal" label="期刊/会议" width="150" show-overflow-tooltip />
        <el-table-column prop="year" label="年份" width="70" align="center" />
        <el-table-column label="链接" width="180">
          <template #default="{ row }">
            <el-link v-if="row.doi" :href="`https://doi.org/${row.doi}`" target="_blank" type="primary" style="margin-right:8px">DOI</el-link>
            <el-link v-if="row.arxiv_id" :href="`https://arxiv.org/abs/${row.arxiv_id}`" target="_blank" type="primary" style="margin-right:8px">arXiv</el-link>
            <el-link v-if="row.pdf_url" :href="row.pdf_url" target="_blank" type="success">PDF</el-link>
          </template>
        </el-table-column>
        <el-table-column label="来源文章" width="80" align="center">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click="$router.push(`/articles/${row.source_article_id}`)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page" :page-size="20" :total="total"
        layout="total, prev, pager, next" style="margin-top:16px;justify-content:center"
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
    const resp = await client.get('/papers/', { params })
    items.value = resp.data.items || []
    total.value = resp.data.total || 0
  } catch (e) { /* ignore */ }
  finally { loading.value = false }
}

onMounted(load)
</script>
