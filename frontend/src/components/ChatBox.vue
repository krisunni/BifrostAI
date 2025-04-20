<template>
    <div class="chat-box">

        <!-- Chat Messages -->
        <div class="chat-messages">
            <div class="message" :class="message.type === 'user' ? 'user-message' : 'server-message'"
                v-for="(message, index) in messages" :key="index">
                <div class="message-content">{{ message.text }}</div>
            </div>
        </div>

        <!-- User Input -->
        <div class="chat-input">
            <textarea v-model="queryText" @keydown.enter="submitQuery" placeholder="Enter your query here" rows="2"
                :disabled="isSubmitting" @input="adjustHeight"></textarea>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const queryText = ref('')
const messages = ref([])  // Store messages to display chat history
const isSubmitting = ref(false)

const submitQuery = async () => {
    if (!queryText.value.trim()) return

    // Add user query to chat history
    messages.value.push({ text: queryText.value, type: 'user' })
    isSubmitting.value = true

    try {
        const res = await axios.post('/query', { query: queryText.value })
        const serverResponse = res.data?.answer || 'No response'

        // Add server response to chat history
        messages.value.push({ text: serverResponse, type: 'server' })
    } catch (error) {
        messages.value.push({ text: 'Error: Unable to get response.', type: 'server' })
    } finally {
        isSubmitting.value = false
        queryText.value = ''  // Clear input after submission
    }
}

const adjustHeight = (event) => {
    const textarea = event.target
    textarea.style.height = 'auto' 
    textarea.style.height = `${textarea.scrollHeight}px`  // Set to the scrollHeight to adjust the height dynamically
}

</script>

<style scoped>
.chat-box {
    display: flex;
    flex-direction: column;
    flex: 1 1 auto;
    /* Ensures it fills its container */
    background-color: white;
    border: 1px solid #ccc;
    padding: 1rem;
    border-radius: 8px;
    overflow: hidden;
}





.chat-messages {
    flex-grow: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-height: 0;
    /* Critical to allow scroll inside flex container */
}

.chat-messages::-webkit-scrollbar {
    width: 6px;
}

.chat-messages::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 3px;
}

.message {
    max-width: 80%;
    padding: 1rem;
    border-radius: 8px;
    word-wrap: break-word;
}

.user-message {
    align-self: flex-end;
    background-color: #007bff;
    color: white;
    margin-left: auto;
    border-top-left-radius: 0;
}

.server-message {
    align-self: flex-start;
    background-color: #f1f1f1;
    color: black;
    margin-right: auto;
    border-top-right-radius: 0;
}

.message-content {
    font-size: 1rem;
}

.chat-input {
    display: flex;
    justify-content: space-between;
    padding-top: 1rem;
}

.chat-input textarea {
    width: 100%;
    padding: 0.5rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #f9f9f9;
    resize: none;
    overflow: hidden;
}

.chat-input textarea:disabled {
    background-color: #e0e0e0;
}
</style>