<template>
  <div class="articles-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>文章列表</span>
          <div class="filters">
            <el-select v-model="filters.article_type" placeholder="文章类型" clearable style="width:130px;margin-right:8px">
              <el-option label="论文解读" value="paper_review" />
              <el-option label="数据集" value="dataset" />
              <el-option label="工具" value="tool" />
              <el-option label="教程" value="tutorial" />
              <el-option label="资讯" value="news" />
              <el-option label="其他" value="other" />
            </el-select>
            <el-select v-model="filters.label" placeholder="标签筛选" clearable filterable style="width:160px;margin-right:8px">
              <el-option v-for="l in allLabels" :key="l.label" :label="`${l.label} (${l.count})`" :value="l.label" />
            </el-select>
            <el-input v-model="searchQuery" placeholder="搜索..." clearable style="width:200px;margin-right:8px"
              @keyup.enter="doSearch" />
            <el-button type="primary" @click="loadArticles">查询</el-button>
          </div>
        </div>
      </template>

      <el-table :data="articles" v-loading="loading" @row-click="viewArticle" style="cursor:pointer">
        <el-table-column prop="title" label="标题" min-width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <span>
              <el-icon v-if="row.is_favorite" color="#f56c6c" style="vertical-align:middle"><Star /></el-icon>
              {{ row.title }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.article_type" size="small" :type="typeColor(row.article_type)">
              {{ typeLabel(row.article_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="l in (row.labels || []).slice(0, 4)" :key="l" size="small" style="margin:2px">{{ l }}</el-tag>
            <span v-if="(row.labels || []).length > 4" style="color:#909399;font-size:12px">
              +{{ row.labels.length - 4 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="author" label="来源" width="120" show-overflow-tooltip />
        <el-table-column label="时间" width="110">
          <template #default="{ row }">
            {{ formatDate(row.published_at || row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button size="small" @click.stop="toggleFavorite(row)">
              {{ row.is_favorite ? '取消收藏' : '收藏' }}
            </el-button>
            <el-button size="small" type="danger" @click.stop="deleteArticle(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadArticles"
        @current-change="loadArticles"
        style="margin-top:16px;justify-content:center"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Star } from '@element-plus/icons-vue'
import client from '../api/client'

const router = useRouter()
const loading = ref(false)
const articles = ref<any[]>([])
const allLabels = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const filters = ref({ article_type: undefined as string | undefined, label: undefined as string | undefined })

const typeLabel = (t: string) => ({
  paper_review: '论文解读', dataset: '数据集', tool: '工具',
  tutorial: '教程', news: '资讯', other: '其他'
}[t] || t)

const typeColor = (t: string) => ({
  paper_review: 'danger', dataset: 'warning', tool: '',
  tutorial: 'success', news: 'info', other: 'info'
}[t] || 'info')

const loadArticles = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (filters.value.article_type) params.article_type = filters.value.article_type
    if (filters.value.label) params.label = filters.value.label

    const resp = await client.get('/articles/', { params })
    articles.value = resp.data.items || []
    total.value = resp.data.total || 0
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const doSearch = async () => {
  if (!searchQuery.value.trim()) { loadArticles(); return }
  loading.value = true
  try {
    const resp = await client.get('/articles/search/', { params: { q: searchQuery.value, limit: pageSize.value } })
    articles.value = resp.data.items || []
    total.value = resp.data.total || 0
  } catch (e) {
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
  }
}

const loadLabels = async () => {
  try {
    const resp = await client.get('/articles/labels')
    allLabels.value = resp.data || []
  } catch (e) { /* ignore */ }
}

const viewArticle = (row: any) => router.push(`/articles/${row.id}`)

const toggleFavorite = async (row: any) => {
  try {
    await client.post(`/articles/${row.id}/favorite`)
    row.is_favorite = !row.is_favorite
  } catch (e) { ElMessage.error('操作失败') }
}

const deleteArticle = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定删除「${row.title}」？`, '确认')
    await client.delete(`/articles/${row.id}`)
    ElMessage.success('已删除')
    loadArticles()
  } catch (e) { /* cancelled or error */ }
}

const formatDate = (d: string) => {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('zh-CN')
}

onMounted(() => { loadArticles(); loadLabels() })
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.filters { display: flex; align-items: center; flex-wrap: wrap; gap: 4px; }
</style>
