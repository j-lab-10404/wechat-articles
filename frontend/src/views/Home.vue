<template>
  <div class="home">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>微信公众号文章知识库</h1>
          <el-menu mode="horizontal" :default-active="activeMenu" router>
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/accounts">公众号管理</el-menu-item>
            <el-menu-item index="/articles">文章列表</el-menu-item>
            <el-menu-item index="/knowledge">知识库</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      
      <el-main>
        <div class="welcome">
          <el-card>
            <h2>欢迎使用微信公众号文章知识库系统</h2>
            <p>这是一个帮助你管理和分析微信公众号文章的智能系统</p>
            
            <el-row :gutter="20" style="margin-top: 30px;">
              <el-col :span="6">
                <el-card shadow="hover">
                  <template #header>
                    <el-icon><Plus /></el-icon>
                    <span>添加文章</span>
                  </template>
                  <p>粘贴微信文章链接快速添加</p>
                  <el-button type="primary" @click="$router.push('/articles/add')">
                    添加文章
                  </el-button>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card shadow="hover">
                  <template #header>
                    <el-icon><Collection /></el-icon>
                    <span>订阅管理</span>
                  </template>
                  <p>添加和管理你关注的公众号</p>
                  <el-button type="primary" @click="$router.push('/accounts')">
                    管理公众号
                  </el-button>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card shadow="hover">
                  <template #header>
                    <el-icon><Document /></el-icon>
                    <span>文章阅读</span>
                  </template>
                  <p>浏览、收藏和搜索文章</p>
                  <el-button type="primary" @click="$router.push('/articles')">
                    查看文章
                  </el-button>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card shadow="hover">
                  <template #header>
                    <el-icon><Reading /></el-icon>
                    <span>知识库</span>
                  </template>
                  <p>AI 提取的结构化知识</p>
                  <el-button type="primary" @click="$router.push('/knowledge')">
                    进入知识库
                  </el-button>
                </el-card>
              </el-col>
            </el-row>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = ref(route.path)
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.header-content h1 {
  font-size: 24px;
  margin: 10px 0;
}

.el-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.welcome h2 {
  text-align: center;
  margin-bottom: 10px;
}

.welcome > p {
  text-align: center;
  color: #666;
  margin-bottom: 20px;
}

.el-card {
  text-align: center;
}

.el-card p {
  margin: 15px 0;
  color: #666;
}
</style>
