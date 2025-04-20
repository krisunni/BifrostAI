<template>
  <div class="app-container">
    <div class="left-panel" :class="{ expanded: bubbleViewerCollapsed }">
      <div class="panel-header">
        <!-- MQTT Controls Section -->
        <div class="mqtt-controls">
          <button @click="toggleMQTT" class="mqtt-button">
            {{ mqttRunning ? 'Stop MQTT' : 'Start MQTT' }}
          </button>
          <span :class="mqttRunning ? 'running' : 'stopped'">{{ mqttRunning ? 'Running' : 'Stopped' }}</span>
        </div>
        <button @click="bubbleViewerCollapsed = !bubbleViewerCollapsed" class="toggle-bubble-viewer">
          {{ bubbleViewerCollapsed ? 'Show Bubble Charts' : 'Hide' }}
        </button>
      </div>
      <div class="chat-box-container">
        <ChatBox />
      </div>
    </div>
    <div class="right-panel" v-if="!bubbleViewerCollapsed">
      <BubbleViewer />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ChatBox from './components/ChatBox.vue'
import BubbleViewer from './components/BubbleViewer.vue'
import axios from 'axios'

const mqttRunning = ref(false)

const bubbleViewerCollapsed = ref(false)
const fetchMQTTStatus = async () => {
  const res = await axios.get('/mqtt/status')
  mqttRunning.value = res.data.running
}

const toggleMQTT = async () => {
  if (mqttRunning.value) {
    await axios.post('/mqtt/stop')
  } else {
    await axios.post('/mqtt/start')
  }
  fetchMQTTStatus()
}

onMounted(() => {
  fetchMQTTStatus()
})
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.left-panel {
  flex: 1;
  min-width: 300px;
  max-width: 100%;
  padding: 1rem;
  background-color: #f4f4f4;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-box-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-box-container>* {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.right-panel {
  flex: 1;
  background-color: white;
  padding: 1rem;
  overflow: hidden;
  transition: all 0.3s ease;
}

.panel-header {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  margin-bottom: 1rem;
}

.mqtt-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.mqtt-button {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border-radius: 4px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.mqtt-button:hover {
  background-color: #0056b3;
}

.mqtt-controls .running {
  color: green;
  font-weight: bold;
}

.mqtt-controls .stopped {
  color: red;
  font-weight: bold;
}

.toggle-bubble-viewer {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border-radius: 4px;
  background-color: #28a745;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 1rem;
}

.toggle-bubble-viewer:hover {
  background-color: #218838;
}

.left-panel.expanded {
  flex: 1 1 auto;
}

.right-panel {
  flex: 1;
  background-color: white;
  padding: 1rem;
  overflow: hidden;
}
</style>
