<template>
  <div style="max-width: 800px; margin: 20px auto; font-family: sans-serif; padding: 0 16px;">
    <h2>Daftar Sesi Workshop</h2>

    <!-- Form Tambah -->
    <SessionForm @created="fetchSessions" />

    <!-- Search & Control -->
    <div style="margin-bottom: 16px; display: flex; gap: 8px;">
      <input 
        v-model="searchQuery" 
        @input="onSearch" 
        type="text" 
        placeholder="Cari berdasarkan judul atau pembicara..." 
        style="flex: 1; padding: 8px;"
      />
    </div>

    <!-- 1. State Loading -->
    <div v-if="state === 'loading'" style="padding: 20px; text-align: center;">
      <p>Sedang memuat data...</p>
    </div>

    <!-- 2. State Error (dengan Retry) -->
    <div v-else-if="state === 'error'" style="padding: 20px; color: red; text-align: center;">
      <p>{{ errorMessage }}</p>
      <button @click="fetchSessions" style="padding: 6px 12px; cursor: pointer;">Coba Lagi (Retry)</button>
    </div>

    <!-- 3. State Empty -->
    <div v-else-if="state === 'empty'" style="padding: 20px; text-align: center; background: #f9f9f9;">
      <p>Tidak ada data sesi yang ditemukan.</p>
    </div>

    <!-- 4. State Success / Data Ready -->
    <div v-else-if="state === 'success'">
      <table border="1" cellpadding="8" cellspacing="0" style="width: 100%; border-collapse: collapse;">
        <thead>
          <tr style="background: #f0f0f0;">
            <th>ID</th>
            <th>Judul</th>
            <th>Pembicara</th>
            <th>Kapasitas</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in sessions" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.title }}</td>
            <td>{{ item.speaker }}</td>
            <td>{{ item.capacity }}</td>
            <td>{{ item.is_active ? 'Aktif' : 'Non-Aktif' }}</td>
            <td>
              <button @click="confirmDelete(item.id)" style="color: red; cursor: pointer;">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination Controls -->
      <div style="margin-top: 16px; display: flex; justify-content: space-between; align-items: center;">
        <button :disabled="page <= 1" @click="changePage(page - 1)">&laquo; Prev</button>
        <span>Halaman {{ page }} dari {{ totalPages }} (Total: {{ total }} data)</span>
        <button :disabled="page >= totalPages" @click="changePage(page + 1)">Next &raquo;</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import SessionForm from './components/SessionForm.vue'

// UI State handling: 'loading' | 'error' | 'empty' | 'success'
const state = ref('loading')
const errorMessage = ref('')

const sessions = ref([])
const searchQuery = ref('')
const page = ref(1)
const limit = ref(5)
const total = ref(0)

const totalPages = computed(() => Math.ceil(total.value / limit.value) || 1)

const fetchSessions = async () => {
  state.value = 'loading'
  errorMessage.value = ''

  try {
    const url = new URL('http://localhost:8000/sessions')
    url.searchParams.append('page', page.value)
    url.searchParams.append('limit', limit.value)
    if (searchQuery.value.trim()) {
      url.searchParams.append('q', searchQuery.value.trim())
    }

    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`Gagal mengambil data (Status: ${response.status})`)
    }

    const result = await response.json()
    sessions.value = result.data
    total.value = result.total

    if (sessions.value.length === 0) {
      state.value = 'empty'
    } else {
      state.value = 'success'
    }
  } catch (err) {
    errorMessage.value = err.message || 'Terjadi kesalahan koneksi backend.'
    state.value = 'error'
  }
}

const onSearch = () => {
  page.value = 1
  fetchSessions()
}

const changePage = (newPage) => {
  page.value = newPage
  fetchSessions()
}

const confirmDelete = async (id) => {
  const isConfirmed = confirm(`Apakah Anda yakin ingin menghapus sesi dengan ID ${id}?`)
  if (!isConfirmed) return

  try {
    const res = await fetch(`http://localhost:8000/sessions/${id}`, {
      method: 'DELETE'
    })

    if (!res.ok) throw new Error('Gagal menghapus data.')

    // Re-fetch data setelah hapus
    fetchSessions()
  } catch (err) {
    alert(err.message)
  }
}

onMounted(() => {
  fetchSessions()
})
</script>