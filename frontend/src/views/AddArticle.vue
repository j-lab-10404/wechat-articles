<template>
  <div class="add-article-container">
    <el-card class="add-article-card">
      <template #header>
        <div class="card-header">
          <h2>📝 添加微信文章</h2>
          <p class="subtitle">粘贴微信公众号文章链接，自动抓取并分析</p>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="文章链接" prop="url">
          <el-input
            v-model="form.url"
            placeholder="https://mp.weixin.qq.com/s/..."
            clearable
            :disabled="loading"
          >
            <template #prepend>
              <el-icon><Link /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">
            支持微信公众号文章链接（mp.weixin.qq.com）
          </div>
        </el-form-item>

        <el-form-item label="自动分析">
          <el-switch
            v-model="form.autoAnalyze"
            active-text="开启 AI 分析"
            inactive-text="稍后分析"
            :disabled="loading"
          />
          <div class="form-tip">
            开启后将自动使用 AI 分析文章内容、提取关键词和分类
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleSubmit"
            :loading="loading"
            size="large"
          >
            <el-icon v-if="!loading"><Plus /></el-icon>
            {{ loading ? '正在抓取...' : '添加文章' }}
          </el-button>
          <el-button @click="handleReset" :disabled="loading" size="large">
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 进度提示 -->
      <el-alert
        v-if="loading"
        title="正在处理"
        type="info"
        :closable="false"
        class="progress-alert"
      >
        <template #default>
          <div class="progress-steps">
            <div class="step" :class="{ active: step >= 1 }">
              <el-icon><Loading /></el-icon>
              <span>抓取文章</span>
            </div>
            <div class="step" :class="{ active: step >= 2 }">
              <el-icon><Document /></el-icon>
              <span>保存数据</span>
            </div>
            <div class="step" :class="{ active: step >= 3 && form.autoAnalyze }">
              <el-icon><MagicStick /></el-icon>
              <span>AI 分析</span>
            </div>
          </div>
        </template>
      </el-alert>

      <!-- 成功提示 -->
      <el-result
        v-if="successArticle"
        icon="success"
        title="添加成功！"
        :sub-title="`文章《${successArticle.title}》已成功添加`"
        class="success-result"
      >
        <template #extra>
          <el-button type="primary" @click="viewArticle">查看文章</el-button>
          <el-button @click="addAnother">继续添加</el-button>
        </template>
      </el-result>
    </el-card>

    <!-- 最近添加的文章 -->
    <el-card v-if="recentArticles.length > 0" class="recent-articles-card">
      <template #header>
        <h3>📚 最近添加</h3>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="article in recentArticles"
          :key="article.id"
          :timestamp="formatTime(article.created_at)"
          placement="top"
        >
          <el-card class="article-item" @click="goToArticle(article.id)">
            <div class="article-info">
              <h4>{{ article.title }}</h4>
              <div class="article-meta">
                <el-tag v-if="article.category" size="small">
                  {{ article.category }}
                </el-tag>
                <span class="author" v-if="article.author">
                  {{ article.author }}
                </span>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { Link, Plus, Loading, Document, MagicStick } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const step = ref(0)
const successArticle = ref<any>(null)
const recentArticles = ref<any[]>([])

const form = reactive({
  url: '',
  autoAnalyze: true
})

const rules: FormRules = {
  url: [
    { required: true, message: '请输入文章链接', trigger: 'blur' },
    {
      pattern: /^https?:\/\/mp\.weixin\.qq\.com\/s\/.+$/,
      message: '请输入有效的微信公众号文章链接',
      trigger: 'blur'
    }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    step.value = 1
    successArticle.value = null

    try {
      // 抓取文章
      const response = await axios.post('/api/articles/scrape', {
        url: form.url,
        auto_analyze: form.autoAnalyze
      })

      step.value = 2
      await new Promise(resolve => setTimeout(resolve, 500))

      if (form.autoAnalyze) {
        step.value = 3
        await new Promise(resolve => setTimeout(resolve, 500))
      }

      successArticle.value = response.data

      ElNotification({
        title: '添加成功',
        message: `文章《${response.data.title}》已成功添加`,
        type: 'success',
        duration: 3000
      })

      // 刷新最近文章列表
      await fetchRecentArticles()
    } catch (error: any) {
      console.error('添加文章失败:', error)
      ElMessage.error(
        error.response?.data?.detail || '添加文章失败，请检查链接是否正确'
      )
    } finally {
      loading.value = false
      step.value = 0
    }
  })
}

const handleReset = () => {
  formRef.value?.resetFields()
  successArticle.value = null
}

const addAnother = () => {
  handleReset()
}

const viewArticle = () => {
  if (successArticle.value) {
    router.push(`/articles/${successArticle.value.id}`)
  }
}

const goToArticle = (id: number) => {
  router.push(`/articles/${id}`)
}

const fetchRecentArticles = async () => {
  try {
    const response = await axios.get('/api/articles/', {
      params: { limit: 5 }
    })
    recentArticles.value = response.data.items || []
  } catch (error) {
    console.error('获取最近文章失败:', error)
  }
}

const formatTime = (time: string) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  if (hours < 24) return `${hours} 小时前`
  if (days < 7) return `${days} 天前`
  return date.toLocaleDateString()
}

onMounted(() => {
  fetchRecentArticles()
})
</script>

<style scoped>
.add-article-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.add-article-card {
  margin-bottom: 20px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.form-tip {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}

.progress-alert {
  margin-top: 20px;
}

.progress-steps {
  display: flex;
  justify-content: space-around;
  margin-top: 10px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  opacity: 0.3;
  transition: opacity 0.3s;
}

.step.active {
  opacity: 1;
}

.step .el-icon {
  font-size: 24px;
}

.success-result {
  margin-top: 20px;
}

.recent-articles-card {
  margin-top: 20px;
}

.article-item {
  cursor: pointer;
  transition: all 0.3s;
}

.article-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.article-info h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #909399;
}

.author {
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>
