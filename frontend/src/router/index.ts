import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/articles',
    name: 'Articles',
    component: () => import('@/views/Articles.vue')
  },
  {
    path: '/articles/add',
    name: 'AddArticle',
    component: () => import('@/views/AddArticle.vue')
  },
  {
    path: '/articles/:id',
    name: 'ArticleDetail',
    component: () => import('@/views/ArticleDetail.vue')
  },
  {
    path: '/papers',
    name: 'Papers',
    component: () => import('@/views/Papers.vue')
  },
  {
    path: '/datasets',
    name: 'Datasets',
    component: () => import('@/views/Datasets.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
