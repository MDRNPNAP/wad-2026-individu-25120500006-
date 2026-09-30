<template>
  <div style="border: 1px solid #ccc; padding: 16px; margin-bottom: 24px; border-radius: 8px;">
    <h3>Tambah Sesi Baru</h3>
    
    <form @submit.prevent="handleSubmit">
      <div style="margin-bottom: 12px;">
        <label>Judul Sesi:</label><br />
        <input v-model="form.title" type="text" style="width: 100%; padding: 6px;" />
        <small v-if="errors.title" style="color: red;">{{ errors.title }}</small>
      </div>

      <div style="margin-bottom: 12px;">
        <label>Pembicara:</label><br />
        <input v-model="form.speaker" type="text" style="width: 100%; padding: 6px;" />
        <small v-if="errors.speaker" style="color: red;">{{ errors.speaker }}</small>
      </div>

      <div style="margin-bottom: 12px;">
        <label>Kapasitas Peserta:</label><br />
        <input v-model.number="form.capacity" type="number" style="width: 100%; padding: 6px;" />
        <small v-if="errors.capacity" style="color: red;">{{ errors.capacity }}</small>
      </div>

      <div style="margin-bottom: 12px;">
        <label>
          <input v-model="form.is_active" type="checkbox" /> Aktif
        </label>
      </div>

      <button type="submit" :disabled="isSubmitting" style="padding: 8px 16px; cursor: pointer;">
        {{ isSubmitting ? 'Menyimpan...' : 'Simpan Sesi' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const emit = defineEmits(['created'])

const form = reactive({
  title: '',
  speaker: '',
  capacity: 30,
  is_active: true
})

const errors = reactive({
  title: '',
  speaker: '',
  capacity: ''
})

const isSubmitting = ref(false)

const validate = () => {
  let isValid = true;
  errors.title = ''
  errors.speaker = ''
  errors.capacity = ''

  if (!form.title || form.title.trim().length < 3) {
    errors.title = 'Judul minimal 3 karakter.'
    isValid = false
  }

  if (!form.speaker || form.speaker.trim().length < 2) {
    errors.speaker = 'Pembicara minimal 2 karakter.'
    isValid = false
  }

  if (!form.capacity || form.capacity <= 0) {
    errors.capacity = 'Kapasitas harus lebih besar dari 0.'
    isValid = false
  }

  return isValid
}

const handleSubmit = async () => {
  if (!validate()) return

  isSubmitting.value = true
  try {
    const res = await fetch('http://localhost:8000/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })

    if (!res.ok) throw new Error('Gagal menambah sesi.')

    // Reset Form
    form.title = ''
    form.speaker = ''
    form.capacity = 30
    form.is_active = true

    emit('created')
  } catch (err) {
    alert(err.message)
  } finally {
    isSubmitting.value = false
  }
}
</script>