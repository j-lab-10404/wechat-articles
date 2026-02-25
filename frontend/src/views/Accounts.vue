<template>
  <div class="accounts-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>公众号管理</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>
            添加公众号
          </el-button>
        </div>
      </template>

      <el-table :data="accounts" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="名称" width="200" />
        <el-table-column prop="account_id" label="账号ID" width="180" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="article_count" label="文章数" width="100" align="center" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="syncAccount(row.id)">同步</el-button>
            <el-button size="small" type="primary" @click="editAccount(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteAccount(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingAccount ? '编辑公众号' : '添加公众号'"
      width="500px"
    >
      <el-form :model="accountForm" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="accountForm.name" placeholder="请输入公众号名称" />
        </el-form-item>
        <el-form-item label="账号ID" required>
          <el-input v-model="accountForm.account_id" placeholder="请输入账号ID" />
        </el-form-item>
        <el-form-item label="RSS地址" required>
          <el-input v-model="accountForm.rss_url" placeholder="请输入RSS订阅地址" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="accountForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveAccount">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '../api/client'

interface Account {
  id: number
  name: string
  account_id: string
  rss_url: string
  description?: string
  is_active: boolean
  article_count: number
}

const loading = ref(false)
const accounts = ref<Account[]>([])
const showAddDialog = ref(false)
const editingAccount = ref<Account | null>(null)
const accountForm = ref({
  name: '',
  account_id: '',
  rss_url: '',
  description: ''
})

const loadAccounts = async () => {
  loading.value = true
  try {
    const response = await api.get('/accounts')
    accounts.value = response.data.items
  } catch (error) {
    ElMessage.error('加载公众号列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const saveAccount = async () => {
  try {
    if (editingAccount.value) {
      await api.put(`/accounts/${editingAccount.value.id}`, accountForm.value)
      ElMessage.success('更新成功')
    } else {
      await api.post('/accounts/', accountForm.value)
      ElMessage.success('添加成功')
    }
    showAddDialog.value = false
    resetForm()
    loadAccounts()
  } catch (error) {
    ElMessage.error('保存失败')
    console.error(error)
  }
}

const editAccount = (account: Account) => {
  editingAccount.value = account
  accountForm.value = {
    name: account.name,
    account_id: account.account_id,
    rss_url: account.rss_url,
    description: account.description || ''
  }
  showAddDialog.value = true
}

const deleteAccount = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个公众号吗？', '提示', {
      type: 'warning'
    })
    await api.delete(`/accounts/${id}`)
    ElMessage.success('删除成功')
    loadAccounts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

const syncAccount = async (id: number) => {
  try {
    await api.post(`/accounts/${id}/sync`)
    ElMessage.success('同步任务已启动')
  } catch (error) {
    ElMessage.error('同步失败')
    console.error(error)
  }
}

const resetForm = () => {
  accountForm.value = {
    name: '',
    account_id: '',
    rss_url: '',
    description: ''
  }
  editingAccount.value = null
}

onMounted(() => {
  loadAccounts()
})
</script>

<style scoped>
.accounts-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
