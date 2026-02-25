<template>
  <div class="articles-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>文章列表</span>
          <div class="filters">
            <el-select v-model="filters.account_id" placeholder="选择公众号" clearable style="width: 200px; margin-right: 10px">
              <el-option
                v-for="account in accounts"
                :key="account.id"
                :label="account.name"
                :value="account.id"
              />
            </el-select>
            <el-select v-model="filters.category" placeholder="选择分类" clearable style="width: 150px; margin-right: 10px">
              <el-option label="学术论文" value="paper" />
              <el-option label="工具软件" value="tool" />
              <el-option label="新闻资讯" value="news" />
              <el-option label="其他" value="other" />
            </el-select>
            <el-button type="primary" @click="loadArticles">查询</el-button>
          </div>
        </div>
      </template>

      <el-table :data="articles" v-loading="loading" style="width: 100%" @row-click="viewArticle">
        <el-table-column prop="title" label="标题" min-width="300">
          <template #default="{ row }">
            <div class="article-title">
              <el-icon v-if="row.is_favorite" color="#f56c6c"><Star /></el-icon>
              {{ row.title }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="account.name" label="公众号" width="150" />
        <el-table-column label="分类" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.category" :type="getCategoryType(row.category)">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="AI分析" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.analysis" type="success">已分析</el-tag>
            <el-tag v-else type="info">未分析</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="published_at" label="发布时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.published_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <el-button size="small" @click.stop="toggleFavorite(row)">
              {{ row.is_favorite ? '取消收藏' : '收藏' }}
            </el-button>
            <el-button
              size="small"
              type="primary"
              @click.stop="analyzeArticle(row)"
              :disabled="!!row.analysis"
            >
              AI分析
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadArticles"
        @current-change="loadArticles"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Star } from '@element-plus/icons-vue'
import api from '../api/client'

interface Article {
  id: number
  title: string
  category?: string
  is_favorite: boolean
  published_at: string
  analysis?: any
  account: {
    name: string
  }
}

const router = useRouter()
const loading = ref(false)
const articles = ref<Article[]>([])
const accounts = ref<any[]>([])
const filters = ref({
  account_id: undefined,
  category: undefined
})
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const loadAccounts = async () => {
  try {
    const response = await api.get('/accounts')
    accounts.value = response.data.items
  } catch (error) {
    console.error('加载公众号列表失败', error)
  }
}

const loadArticles = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (pagination.value.page - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    }
    if (filters.value.account_id) params.account_id = filters.value.account_id
    if (filters.value.category) params.category = filters.value.category

    const response = await api.get('/articles', { params })
    articles.value = response.data.items
    pagination.value.total = response.data.total
  } catch (error) {
    ElMessage.error('加载文章列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const viewArticle = (row: Article) => {
  router.push(`/articles/${row.id}`)
}

const toggleFavorite = async (article: Article) => {
  try {
    await api.post(`/articles/${article.id}/favorite`)
    article.is_favorite = !article.is_favorite
    ElMessage.success(article.is_favorite ? '已收藏' : '已取消收藏')
  } catch (error) {
    ElMessage.error('操作失败')
    console.error(error)
  }
}

const analyzeArticle = async (article: Article) => {
  try {
    loading.value = true
    await api.post(`/articles/${article.id}/analyze`)
    ElMessage.success('AI分析已完成')
    loadArticles()
  } catch (error) {
    ElMessage.error('AI分析失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const getCategoryType = (category: string) => {
  const types: Record<string, string> = {
    paper: 'danger',
    tool: 'warning',
    news: 'success',
    other: 'info'
  }
  return types[category] || 'info'
}

const getCategoryLabel = (category: string) => {
  const labels: Record<string, string> = {
    paper: '论文',
    tool: '工具',
    news: '新闻',
    other: '其他'
  }
  return labels[category] || '其他'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadAccounts()
  loadArticles()
})
</script>

<style scoped>
.articles-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  display: flex;
  align-items: center;
}

.article-title {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.article-title:hover {
  color: #409eff;
}

:deep(.el-table__row) {
  cursor: pointer;
}
</style>
