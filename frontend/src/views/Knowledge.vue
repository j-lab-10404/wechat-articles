<template>
  <div class="knowledge-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>知识库</span>
          <div class="filters">
            <el-select v-model="filters.type" placeholder="选择类型" clearable style="width: 150px; margin-right: 10px">
              <el-option label="学术论文" value="paper" />
              <el-option label="工具软件" value="tool" />
              <el-option label="新闻资讯" value="news" />
            </el-select>
            <el-input
              v-model="searchQuery"
              placeholder="搜索知识"
              style="width: 300px; margin-right: 10px"
              @keyup.enter="searchKnowledge"
            >
              <template #append>
                <el-button @click="searchKnowledge">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
            <el-button type="primary" @click="loadKnowledge">查询</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col
          v-for="item in knowledgeList"
          :key="item.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card class="knowledge-card" shadow="hover" @click="viewKnowledge(item)">
            <div class="knowledge-type">
              <el-tag :type="getTypeColor(item.type)">
                {{ getTypeLabel(item.type) }}
              </el-tag>
            </div>
            <h3 class="knowledge-title">{{ item.title }}</h3>
            <p class="knowledge-summary">{{ item.summary || '暂无摘要' }}</p>
            <div class="knowledge-meta">
              <span class="meta-item">
                <el-icon><Document /></el-icon>
                {{ item.article_count || 0 }} 篇文章
              </span>
              <span class="meta-item">
                <el-icon><Clock /></el-icon>
                {{ formatDate(item.created_at) }}
              </span>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="!loading && knowledgeList.length === 0" description="暂无知识条目" />

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadKnowledge"
        @current-change="loadKnowledge"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Document, Clock } from '@element-plus/icons-vue'
import api from '../api/client'

interface Knowledge {
  id: number
  title: string
  type: string
  summary?: string
  article_count?: number
  created_at: string
}

const loading = ref(false)
const knowledgeList = ref<Knowledge[]>([])
const searchQuery = ref('')
const filters = ref({
  type: undefined
})
const pagination = ref({
  page: 1,
  pageSize: 12,
  total: 0
})

const loadKnowledge = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (pagination.value.page - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    }
    if (filters.value.type) params.type = filters.value.type

    const response = await api.get('/knowledge', { params })
    knowledgeList.value = response.data.items
    pagination.value.total = response.data.total
  } catch (error) {
    ElMessage.error('加载知识库失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const searchKnowledge = async () => {
  if (!searchQuery.value.trim()) {
    loadKnowledge()
    return
  }

  loading.value = true
  try {
    const params = {
      q: searchQuery.value,
      skip: (pagination.value.page - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    }
    const response = await api.get('/knowledge/search/', { params })
    knowledgeList.value = response.data.items
    pagination.value.total = response.data.total
  } catch (error) {
    ElMessage.error('搜索失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const viewKnowledge = (item: Knowledge) => {
  ElMessage.info('知识详情页面开发中...')
  console.log('View knowledge:', item)
}

const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    paper: 'danger',
    tool: 'warning',
    news: 'success'
  }
  return colors[type] || 'info'
}

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    paper: '论文',
    tool: '工具',
    news: '新闻'
  }
  return labels[type] || '其他'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadKnowledge()
})
</script>

<style scoped>
.knowledge-page {
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

.knowledge-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.2s;
}

.knowledge-card:hover {
  transform: translateY(-5px);
}

.knowledge-type {
  margin-bottom: 10px;
}

.knowledge-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
  min-height: 44px;
}

.knowledge-summary {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  line-height: 1.6;
  min-height: 67px;
}

.knowledge-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
