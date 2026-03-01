<template>
  <div class="home">
    <div style="text-align:center;margin-bottom:32px">
      <h2>微信公众号文章知识库</h2>
      <p style="color:#909399;margin-top:8px">收藏感兴趣的微信文章，AI 自动分析、分类、提取论文和数据集信息</p>
    </div>

    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="hover" class="action-card" @click="$router.push('/articles/add')">
          <div class="card-icon">📝</div>
          <h3>添加文章</h3>
          <p>粘贴微信文章链接，自动获取全文并 AI 分析</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="action-card" @click="$router.push('/articles')">
          <div class="card-icon">📚</div>
          <h3>文章列表</h3>
          <p>浏览、搜索、按标签和类型筛选文章</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="action-card" @click="$router.push('/papers')">
          <div class="card-icon">📄</div>
          <h3>论文库</h3>
          <p>从文章中提取的学术论文信息，含 DOI 和 PDF 链接</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- 统计 -->
    <el-row :gutter="16" style="margin-top:24px">
      <el-col :span="6" v-for="s in stats" :key="s.label">
        <el-statistic :title="s.label" :value="s.value" />
      </el-col>
    </el-row>

    <!-- 最近文章 -->
    <el-card style="margin-top:24px" v-if="recentArticles.length">
      <template #header><span>最近添加的文章</span></template>
      <div v-for="a in recentArticles" :key="a.id" class="recent-item" @click="$router.push(`/articles/${a.id}`)">
        <div>
          <span style="font-weight:500">{{ a.title }}</span>
          <el-tag v-if="a.article_type" size="small" :type="typeColor(a.article_type)" style="margin-left:8px">
            {{ typeLabel(a.article_type) }}
          </el-tag>
        </div>
        <span style="color:#909399;font-size:12px">{{ formatDate(a.created_at) }}</span>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import client from '../api/client'

const recentArticles = ref<any[]>([])
const stats = ref([
  { label: '文章总数', value: 0 },
  { label: '论文数', value: 0 },
  { label: '数据集数', value: 0 },
  { label: '标签数', value: 0 }
])

const typeLabel = (t: string) => ({
  paper_review: '论文解读', dataset: '数据集', tool: '工具',
  tutorial: '教程', news: '资讯', other: '其他'
}[t] || t)

const typeColor = (t: string) => ({
  paper_review: 'danger', dataset: 'warning', tool: '',
  tutorial: 'success', news: 'info', other: 'info'
}[t] || 'info')

const formatDate = (d: string) => d ? new Date(d).toLocaleDateString('zh-CN') : ''

onMounted(async () => {
  try {
    const resp = await client.get('/articles/', { params: { limit: 5 } })
    recentArticles.value = resp.data.items || []
    stats.value[0].value = resp.data.total || 0
  } catch (e) { /* ignore */ }
  try {
    const resp = await client.get('/articles/labels')
    stats.value[3].value = (resp.data || []).length
  } catch (e) { /* ignore */ }
  try {
    const resp = await client.get('/papers/')
    stats.value[1].value = resp.data.total || 0
  } catch (e) { /* ignore */ }
  try {
    const resp = await client.get('/datasets/')
    stats.value[2].value = resp.data.total || 0
  } catch (e) { /* ignore */ }
})
</script>

<style scoped>
.action-card { cursor: pointer; text-align: center; transition: transform 0.2s; }
.action-card:hover { transform: translateY(-4px); }
.card-icon { font-size: 36px; margin-bottom: 8px; }
.action-card h3 { margin: 0 0 8px 0; }
.action-card p { color: #909399; font-size: 13px; margin: 0; }
.recent-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0; cursor: pointer; }
.recent-item:hover { background: #f5f7fa; }
.recent-item:last-child { border-bottom: none; }
</style>
