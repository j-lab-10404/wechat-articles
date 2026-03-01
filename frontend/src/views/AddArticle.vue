<template>
  <div class="add-article">
    <el-card>
      <template #header>
        <h2>📝 添加微信文章</h2>
        <p style="color:#909399;font-size:13px;margin-top:4px">
          粘贴微信公众号文章链接，自动从 WeWe-RSS 获取全文并 AI 分析
        </p>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="文章链接" prop="url">
          <el-input
            v-model="form.url"
            placeholder="https://mp.weixin.qq.com/s/..."
            clearable
            :disabled="loading"
          />
        </el-form-item>

        <el-form-item label="自动分析">
          <el-switch v-model="form.autoAnalyze" :disabled="loading" />
          <span style="margin-left:8px;color:#909399;font-size:12px">
            AI 自动分类、提取标签、论文和数据集信息
          </span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading" size="large">
            {{ loading ? statusText : '添加文章' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 结果 -->
      <el-result v-if="result" icon="success" title="添加成功">
        <template #sub-title>
          <div style="text-align:left;max-width:500px;margin:0 auto">
            <p>标题：{{ result.title }}</p>
            <p>内容长度：{{ result.content_length }} 字</p>
            <p v-if="result.article_type">类型：{{ typeLabel(result.article_type) }}</p>
            <p v-if="result.labels?.length">标签：
              <el-tag v-for="l in result.labels" :key="l" size="small" style="margin:2px">{{ l }}</el-tag>
            </p>
            <p v-if="result.papers_count">提取论文：{{ result.papers_count }} 篇</p>
            <p v-if="result.datasets_count">提取数据集：{{ result.datasets_count }} 个</p>
            <p v-if="result.analysis_status === 'failed'" style="color:#f56c6c">
              AI 分析失败：{{ result.analysis_error }}
            </p>
          </div>
        </template>
        <template #extra>
          <el-button type="primary" @click="$router.push(`/articles/${result.id}`)">查看详情</el-button>
          <el-button @click="reset">继续添加</el-button>
        </template>
      </el-result>
    </el-card>

    <!-- 最近添加 -->
    <el-card v-if="recentArticles.length" style="margin-top:16px">
      <template #header><span>📚 最近添加</span></template>
      <el-table :data="recentArticles" @row-click="(row: any) => $router.push(`/articles/${row.id}`)" style="cursor:pointer">
        <el-table-column prop="title" label="标题" show-overflow-tooltip />
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.article_type" size="small" :type="typeTagColor(row.article_type)">
              {{ typeLabel(row.article_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="l in (row.labels || []).slice(0, 3)" :key="l" size="small" style="margin:2px">{{ l }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import client from '../api/client'

const formRef = ref<FormInstance>()
const loading = ref(false)
const statusText = ref('处理中...')
const result = ref<any>(null)
const recentArticles = ref<any[]>([])

const form = reactive({ url: '', autoAnalyze: true })

const rules: FormRules = {
  url: [
    { required: true, message: '请输入文章链接', trigger: 'blur' },
    { pattern: /^https?:\/\/mp\.weixin\.qq\.com\//, message: '请输入微信公众号文章链接', trigger: 'blur' }
  ]
}

const typeLabel = (t: string) => ({
  paper_review: '论文解读', dataset: '数据集', tool: '工具',
  tutorial: '教程', news: '资讯', other: '其他'
}[t] || t)

const typeTagColor = (t: string) => ({
  paper_review: 'danger', dataset: 'warning', tool: '',
  tutorial: 'success', news: 'info', other: 'info'
}[t] || 'info')

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    result.value = null
    statusText.value = '正在添加文章...'

    try {
      // Step 1: Add article
      const resp = await client.post('/articles/add', {
        url: form.url,
        auto_analyze: form.autoAnalyze
      })
      let data = resp.data

      // Step 2: If content not fetched, retry
      if (data.need_fetch && data.id) {
        statusText.value = '正在从 WeWe-RSS 获取内容...'
        try {
          const fetchResp = await client.post(`/articles/${data.id}/fetch-content`)
          data.title = fetchResp.data.title
          data.content_length = fetchResp.data.content_length
          data.need_fetch = false

          // Step 3: Analyze if content was fetched
          if (form.autoAnalyze && data.content_length > 0) {
            statusText.value = '正在 AI 分析...'
            try {
              const analyzeResp = await client.post(`/articles/${data.id}/analyze`)
              data.analysis_status = 'completed'
              data.article_type = analyzeResp.data.article_type
              data.labels = analyzeResp.data.labels
              data.summary = analyzeResp.data.summary
            } catch (e) {
              data.analysis_status = 'failed'
            }
          }
        } catch (e) {
          // Content fetch failed, article saved without content
          data.analysis_error = '内容获取失败，请稍后在详情页重试'
        }
      }

      result.value = data
      ElMessage.success('添加成功')
      fetchRecent()
    } catch (err: any) {
      const msg = err.response?.data?.detail || '添加失败'
      ElMessage.error(msg)
    } finally {
      loading.value = false
    }
  })
}

const reset = () => {
  form.url = ''
  result.value = null
  formRef.value?.resetFields()
}

const fetchRecent = async () => {
  try {
    const resp = await client.get('/articles/', { params: { limit: 5 } })
    recentArticles.value = resp.data.items || []
  } catch (e) { /* ignore */ }
}

onMounted(fetchRecent)
</script>

<style scoped>
.add-article { max-width: 800px; margin: 0 auto; }
</style>
