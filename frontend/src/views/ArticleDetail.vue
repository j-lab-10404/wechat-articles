<template>
  <div class="article-detail-page">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-button @click="$router.back()">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <div class="actions">
            <el-button @click="toggleFavorite">
              <el-icon><Star /></el-icon>
              {{ article?.is_favorite ? '取消收藏' : '收藏' }}
            </el-button>
            <el-button type="primary" @click="analyzeArticle" :disabled="!!article?.analysis">
              <el-icon><MagicStick /></el-icon>
              AI分析
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="article" class="article-content">
        <h1 class="article-title">{{ article.title }}</h1>
        
        <div class="article-meta">
          <el-tag>{{ article.account?.name }}</el-tag>
          <el-tag v-if="article.category" :type="getCategoryType(article.category)">
            {{ getCategoryLabel(article.category) }}
          </el-tag>
          <span class="meta-item">
            <el-icon><Clock /></el-icon>
            {{ formatDate(article.published_at) }}
          </span>
          <a v-if="article.url" :href="article.url" target="_blank" class="meta-item">
            <el-icon><Link /></el-icon>
            原文链接
          </a>
        </div>

        <!-- AI 分析结果 -->
        <el-card v-if="article.analysis" class="analysis-card" shadow="never">
          <template #header>
            <div class="analysis-header">
              <el-icon><MagicStick /></el-icon>
              <span>AI 分析结果</span>
            </div>
          </template>
          
          <div class="analysis-content">
            <div v-if="article.analysis.summary" class="analysis-section">
              <h3>摘要</h3>
              <p>{{ article.analysis.summary }}</p>
            </div>

            <div v-if="article.analysis.keywords && article.analysis.keywords.length" class="analysis-section">
              <h3>关键词</h3>
              <div class="keywords">
                <el-tag v-for="keyword in article.analysis.keywords" :key="keyword" type="info">
                  {{ keyword }}
                </el-tag>
              </div>
            </div>

            <div v-if="article.analysis.entities && article.analysis.entities.length" class="analysis-section">
              <h3>实体识别</h3>
              <div class="entities">
                <el-tag v-for="entity in article.analysis.entities" :key="entity" type="success">
                  {{ entity }}
                </el-tag>
              </div>
            </div>

            <div v-if="article.analysis.paper_info" class="analysis-section">
              <h3>论文信息</h3>
              <el-descriptions :column="2" border>
                <el-descriptions-item v-for="(value, key) in article.analysis.paper_info" :key="key" :label="key">
                  {{ value }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <div v-if="article.analysis.tool_info" class="analysis-section">
              <h3>工具信息</h3>
              <el-descriptions :column="2" border>
                <el-descriptions-item v-for="(value, key) in article.analysis.tool_info" :key="key" :label="key">
                  {{ value }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>

        <!-- 文章正文 -->
        <div class="article-body" v-html="article.content"></div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Star, MagicStick, Clock, Link } from '@element-plus/icons-vue'
import api from '../api/client'

const route = useRoute()
const loading = ref(false)
const article = ref<any>(null)

const loadArticle = async () => {
  loading.value = true
  try {
    const response = await api.get(`/articles/${route.params.id}`)
    article.value = response.data
  } catch (error) {
    ElMessage.error('加载文章失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const toggleFavorite = async () => {
  try {
    await api.post(`/articles/${article.value.id}/favorite`)
    article.value.is_favorite = !article.value.is_favorite
    ElMessage.success(article.value.is_favorite ? '已收藏' : '已取消收藏')
  } catch (error) {
    ElMessage.error('操作失败')
    console.error(error)
  }
}

const analyzeArticle = async () => {
  try {
    loading.value = true
    await api.post(`/articles/${article.value.id}/analyze`)
    ElMessage.success('AI分析已完成')
    loadArticle()
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
  loadArticle()
})
</script>

<style scoped>
.article-detail-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  display: flex;
  gap: 10px;
}

.article-content {
  padding: 20px 0;
}

.article-title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 20px;
  line-height: 1.4;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #666;
  text-decoration: none;
}

.meta-item:hover {
  color: #409eff;
}

.analysis-card {
  margin-bottom: 30px;
  background: #f5f7fa;
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.analysis-content {
  padding: 10px 0;
}

.analysis-section {
  margin-bottom: 20px;
}

.analysis-section h3 {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
}

.analysis-section p {
  line-height: 1.8;
  color: #606266;
}

.keywords,
.entities {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.article-body {
  line-height: 1.8;
  font-size: 16px;
  color: #303133;
}

.article-body :deep(img) {
  max-width: 100%;
  height: auto;
  margin: 20px 0;
}

.article-body :deep(p) {
  margin-bottom: 15px;
}

.article-body :deep(h1),
.article-body :deep(h2),
.article-body :deep(h3) {
  margin-top: 30px;
  margin-bottom: 15px;
}
</style>
