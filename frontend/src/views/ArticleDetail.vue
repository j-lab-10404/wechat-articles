<template>
  <div class="article-detail" v-loading="loading">
    <el-page-header @back="$router.back()" style="margin-bottom:16px">
      <template #content>{{ article?.title || '文章详情' }}</template>
      <template #extra>
        <el-button @click="toggleFavorite" :type="article?.is_favorite ? 'warning' : 'default'">
          {{ article?.is_favorite ? '★ 已收藏' : '☆ 收藏' }}
        </el-button>
        <el-button v-if="!article?.content_text" type="warning" @click="fetchContent" :loading="fetching">
          获取内容
        </el-button>
        <el-button type="primary" @click="reAnalyze" :loading="analyzing" :disabled="!article?.content_text">
          {{ article?.content_text ? '重新分析' : 'AI 分析（需先获取内容）' }}
        </el-button>
      </template>
    </el-page-header>

    <template v-if="article">
      <!-- 基本信息 -->
      <el-card style="margin-bottom:16px">
        <div class="meta-row">
          <el-tag v-if="article.article_type" :type="typeColor(article.article_type)">
            {{ typeLabel(article.article_type) }}
          </el-tag>
          <span v-if="article.author" style="color:#606266">{{ article.author }}</span>
          <span style="color:#909399">{{ formatDate(article.published_at) }}</span>
          <a v-if="article.url" :href="article.url" target="_blank" style="color:#409eff;text-decoration:none">原文链接 ↗</a>
        </div>

        <!-- 摘要 -->
        <div v-if="article.summary" style="margin-top:12px;padding:12px;background:#f5f7fa;border-radius:6px;line-height:1.8">
          {{ article.summary }}
        </div>

        <!-- 标签 -->
        <div v-if="article.labels?.length" style="margin-top:12px">
          <span style="color:#909399;font-size:13px;margin-right:8px">标签：</span>
          <el-tag v-for="l in article.labels" :key="l" closable size="small" style="margin:2px"
            @close="removeLabel(l)">{{ l }}</el-tag>
          <el-button size="small" @click="showAddLabel = true" style="margin-left:4px">+ 添加</el-button>
        </div>
        <div v-else style="margin-top:8px">
          <el-button size="small" @click="showAddLabel = true">+ 添加标签</el-button>
        </div>

        <!-- 添加标签弹窗 -->
        <el-dialog v-model="showAddLabel" title="添加标签" width="360px">
          <el-input v-model="newLabel" placeholder="输入标签名" @keyup.enter="addLabel" />
          <template #footer>
            <el-button @click="showAddLabel = false">取消</el-button>
            <el-button type="primary" @click="addLabel">添加</el-button>
          </template>
        </el-dialog>

        <!-- 关键词 -->
        <div v-if="article.keywords?.length" style="margin-top:8px">
          <span style="color:#909399;font-size:13px;margin-right:8px">关键词：</span>
          <el-tag v-for="k in article.keywords" :key="k" type="info" size="small" style="margin:2px">{{ k }}</el-tag>
        </div>
      </el-card>

      <!-- 论文信息 -->
      <el-card v-if="article.papers?.length" style="margin-bottom:16px">
        <template #header><span>📄 相关论文 ({{ article.papers.length }})</span></template>
        <div v-for="(p, i) in article.papers" :key="i" class="paper-item">
          <h4>{{ p.title }}</h4>
          <p v-if="p.title_cn" style="color:#606266">{{ p.title_cn }}</p>
          <div class="paper-meta">
            <span v-if="p.authors?.length">{{ p.authors.join(', ') }}</span>
            <span v-if="p.journal">{{ p.journal }}</span>
            <span v-if="p.year">{{ p.year }}</span>
          </div>
          <p v-if="p.main_findings" style="margin-top:6px;color:#606266;line-height:1.6">{{ p.main_findings }}</p>
          <div style="margin-top:6px">
            <el-link v-if="p.doi" :href="`https://doi.org/${p.doi}`" target="_blank" type="primary" style="margin-right:12px">
              DOI: {{ p.doi }}
            </el-link>
            <el-link v-if="p.arxiv_id" :href="`https://arxiv.org/abs/${p.arxiv_id}`" target="_blank" type="primary" style="margin-right:12px">
              arXiv: {{ p.arxiv_id }}
            </el-link>
            <el-link v-if="p.pdf_url" :href="p.pdf_url" target="_blank" type="success">
              📥 PDF
            </el-link>
          </div>
          <el-divider v-if="i < article.papers.length - 1" />
        </div>
      </el-card>

      <!-- 数据集信息 -->
      <el-card v-if="article.datasets?.length" style="margin-bottom:16px">
        <template #header><span>📊 相关数据集 ({{ article.datasets.length }})</span></template>
        <div v-for="(d, i) in article.datasets" :key="i" class="dataset-item">
          <h4>{{ d.name }}</h4>
          <p v-if="d.description" style="color:#606266;line-height:1.6">{{ d.description }}</p>
          <div class="dataset-meta">
            <el-tag v-if="d.data_type" size="small">{{ d.data_type }}</el-tag>
            <el-tag v-if="d.domain" size="small" type="success">{{ d.domain }}</el-tag>
            <span v-if="d.scale" style="color:#909399">规模: {{ d.scale }}</span>
          </div>
          <div v-if="d.access_method" style="margin-top:6px">
            <span style="color:#909399;font-size:13px">获取方式：</span>{{ d.access_method }}
          </div>
          <div v-if="d.tutorial" style="margin-top:6px;padding:8px;background:#f5f7fa;border-radius:4px;white-space:pre-wrap;font-size:13px">
            {{ d.tutorial }}
          </div>
          <el-link v-if="d.download_url" :href="d.download_url" target="_blank" type="primary" style="margin-top:6px">
            📥 下载链接
          </el-link>
          <el-divider v-if="i < article.datasets.length - 1" />
        </div>
      </el-card>

      <!-- 文章正文 -->
      <el-card>
        <template #header><span>📖 文章正文</span></template>
        <div v-if="article.content" class="article-body" v-html="article.content"></div>
        <div v-else-if="article.content_text" class="article-body" style="white-space:pre-wrap">{{ article.content_text }}</div>
        <el-empty v-else description="暂无正文内容" />
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import client from '../api/client'

const route = useRoute()
const loading = ref(false)
const analyzing = ref(false)
const fetching = ref(false)
const article = ref<any>(null)
const showAddLabel = ref(false)
const newLabel = ref('')

const typeLabel = (t: string) => ({
  paper_review: '论文解读', dataset: '数据集', tool: '工具',
  tutorial: '教程', news: '资讯', other: '其他'
}[t] || t)

const typeColor = (t: string) => ({
  paper_review: 'danger', dataset: 'warning', tool: '',
  tutorial: 'success', news: 'info', other: 'info'
}[t] || 'info')

const formatDate = (d: string) => d ? new Date(d).toLocaleDateString('zh-CN') : ''

const loadArticle = async () => {
  loading.value = true
  try {
    const resp = await client.get(`/articles/${route.params.id}`)
    article.value = resp.data
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const toggleFavorite = async () => {
  try {
    await client.post(`/articles/${article.value.id}/favorite`)
    article.value.is_favorite = !article.value.is_favorite
  } catch (e) { ElMessage.error('操作失败') }
}

const reAnalyze = async () => {
  analyzing.value = true
  try {
    await client.post(`/articles/${article.value.id}/analyze`)
    ElMessage.success('分析完成')
    loadArticle()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '分析失败')
  } finally {
    analyzing.value = false
  }
}

const fetchContent = async () => {
  fetching.value = true
  try {
    await client.post(`/articles/${article.value.id}/fetch-content`)
    ElMessage.success('内容获取成功')
    loadArticle()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '内容获取失败')
  } finally {
    fetching.value = false
  }
}

const addLabel = async () => {
  if (!newLabel.value.trim()) return
  try {
    const resp = await client.post(`/articles/${article.value.id}/labels/add`, null, {
      params: { label: newLabel.value.trim() }
    })
    article.value.labels = resp.data.labels
    newLabel.value = ''
    showAddLabel.value = false
  } catch (e) { ElMessage.error('添加失败') }
}

const removeLabel = async (label: string) => {
  try {
    const resp = await client.delete(`/articles/${article.value.id}/labels/${encodeURIComponent(label)}`)
    article.value.labels = resp.data.labels
  } catch (e) { ElMessage.error('删除失败') }
}

onMounted(loadArticle)
</script>

<style scoped>
.article-detail { max-width: 900px; margin: 0 auto; }
.meta-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.paper-item, .dataset-item { padding: 8px 0; }
.paper-item h4, .dataset-item h4 { margin: 0 0 4px 0; font-size: 15px; }
.paper-meta, .dataset-meta { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; color: #909399; font-size: 13px; margin-top: 4px; }
.article-body { line-height: 1.8; font-size: 15px; }
.article-body :deep(img) { max-width: 100%; height: auto; margin: 12px 0; }
</style>
