<template>
  <a-modal
    v-model:open="visible"
    title="Set System Prompt"
    :width="600"
    @ok="handleSave"
    @cancel="handleCancel"
    :confirm-loading="loading"
    ok-text="Save"
    cancel-text="Cancel"
  >
    <div class="prompt-modal-content">
      <a-form :model="form" layout="vertical">
        <a-form-item label="" name="prompt">
          <a-textarea
            v-model:value="form.prompt"
            placeholder="Please enter system prompt..."
            :rows="8"
            :maxlength="2000"
            show-count
          />
        </a-form-item>
        <div class="prompt-tips">
          <a-alert
            message="Tips"
            description="The system prompt will affect the AI's response style and behavior, please set it carefully."
            type="info"
            show-icon
          />
        </div>
      </a-form>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { message } from 'ant-design-vue'
import { systemPromptAPI } from '@/api'

// Props
const props = defineProps({
  open: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:open', 'success'])

// Reactive data
const visible = ref(false)
const loading = ref(false)
const form = reactive({
  prompt: ''
})

// Watch props.open to sync with internal visible state
watch(() => props.open, (newVal) => {
  visible.value = newVal
  if (newVal) {
    // Load current system prompt when modal opens
    loadCurrentPrompt()
  }
})

// Watch internal visible state to emit update
watch(visible, (newVal) => {
  emit('update:open', newVal)
})

// Load current system prompt
const loadCurrentPrompt = async () => {
  try {
    // Call API to get current system prompt
    // const response = await systemPromptAPI.getPrompt()
    // form.prompt = response.data?.prompt || response.prompt || ''
  } catch (error) {
    console.error('Failed to load current prompt:', error)
    // If loading fails, don't show error message, keep blank state
  }
}

// Handle save
const handleSave = async () => {
  if (!form.prompt.trim()) {
    message.warning('Please enter system prompt')
    return
  }

  loading.value = true

  try {
    // Call API to save system prompt
    await systemPromptAPI.savePrompt(form.prompt.trim())

    // message.success('System prompt saved successfully')
    visible.value = false
    emit('success', form.prompt)

  } catch (error) {
    console.error('Failed to save system prompt:', error)
    message.error('Save failed: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// Handle cancel
const handleCancel = () => {
  visible.value = false
}

// Reset form
const resetForm = () => {
  form.prompt = ''
}

// Expose methods
defineExpose({
  resetForm
})
</script>

<style scoped>
.prompt-modal-content {
  padding: 10px 0;
}

.prompt-tips {
  margin-top: 16px;
}

:deep(.ant-form-item-label) {
  font-weight: 500;
}

:deep(.ant-input) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
}

:deep(.ant-alert) {
  border-radius: 6px;
}
</style>
