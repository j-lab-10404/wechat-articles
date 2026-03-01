<template>
  <el-config-provider :locale="zhCn">
    <el-container class="app-container">
      <el-header class="app-header">
        <div class="header-inner">
          <h1 class="logo" @click="$router.push('/')">📚 微信文章知识库</h1>
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            router
            class="nav-menu"
            :ellipsis="false"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/articles">文章</el-menu-item>
            <el-menu-item index="/articles/add">添加文章</el-menu-item>
            <el-menu-item index="/papers">论文</el-menu-item>
            <el-menu-item index="/datasets">数据集</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const route = useRoute()
const activeMenu = computed(() => {
  if (route.path.startsWith('/articles/add')) return '/articles/add'
  if (route.path.startsWith('/articles')) return '/articles'
  if (route.path.startsWith('/papers')) return '/papers'
  if (route.path.startsWith('/datasets')) return '/datasets'
  return route.path
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  color: #2c3e50;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.app-container { min-height: 100vh; }

.app-header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  padding: 0 20px;
  height: 60px !important;
  line-height: 60px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
}

.logo {
  font-size: 18px;
  white-space: nowrap;
  cursor: pointer;
  margin-right: 40px;
}

.nav-menu { border-bottom: none !important; flex: 1; }

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
  width: 100%;
}
</style>
