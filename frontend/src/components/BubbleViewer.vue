<template>
  <div class="app-container">
    <div class="right-panel">
      <div id="d3-bubbles"></div>
    </div>
    <!-- Modal for stats -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>{{ stats.name }} Stats</h3>
        <p><strong>Total Data Points:</strong> {{ stats.total }}</p>
        <p><strong>Last Data:</strong> {{ stats.lastData }}</p>
        <p><strong>First Data:</strong> {{ stats.additionalInfo.first_detection }}</p>
        <!-- <p><strong>Additional Info:</strong> {{ stats.additionalInfo }}</p> -->
        

        <button @click="closeModal">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as d3 from 'd3'

// Modal state
const showModal = ref(false)
const stats = ref({ total: 0, lastData: '', additionalInfo: '' })

// Function to draw the bubble chart
const drawBubbleChart = async () => {
  const container = document.getElementById('d3-bubbles')
  if (!container) {
    console.error('#d3-bubbles not found')
    return
  }

  const width = container.clientWidth
  const height = container.clientHeight

  // Fetch data
  const res = await axios.get('/collections')
  const rawData = res.data

  const grouped = d3.group(rawData, d => d.label)

  const data = {
    name: 'root',
    children: Array.from(grouped, ([label, items]) => ({
      name: label,
      children: items.map(i => ({ name: i.id, value: 1 }))
    }))
  }

  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)

  const pack = d3.pack()
    .size([width, height])
    .padding(3)

  // Create the hierarchy for d3
  let root = d3.hierarchy(data).sum(d => d.value)
  let nodes = pack(root).descendants()

  const node = svg.selectAll('g')
    .data(nodes)
    .join('g')
    .attr('transform', d => `translate(${d.x},${d.y})`)
    .on('click', (event, d) => {
      if (d.depth === 1) {
        // Toggle visibility of child nodes
        if (d.children) {
          d.children = null
        } else {
          // Todo show the children in a nice Animation
          d.children = d.data.children
        }

        root = d3.hierarchy(data).sum(d => d.value)
        nodes = pack(root).descendants()

        node.transition().duration(500)
          .attr('transform', d => `translate(${d.x},${d.y})`)

        node.selectAll('circle')
          .transition().duration(500)
          .attr('r', d => d.r)
      } else if (d.depth === 2) {
        // Show the modal with stats
        showStats(d.parent.data.name)
      }
    })

  node.append('circle')
    .attr('r', d => d.r)
    .attr('fill', d => d.children ? '#69b3a2' : '#ffd54f')

  node.append('text')
    .attr('dy', '0.3em')
    .attr('text-anchor', 'middle')
    .style('font-size', d => d.r / 5)
    .text(d => d.data.name.length < 10 ? d.data.name : '')

  node.selectAll('circle')
    .attr('opacity', d => d.depth === 1 ? 1 : 0)

  node.selectAll('text')
    .attr('opacity', d => d.depth === 1 ? 1 : 0)
}

const showStats = async (label) => {
  try {
    const res = await axios.get(`/collections/${label}/stats`)
    const statsData = res.data

    stats.value = {
      name: label,
      total: statsData.total,
      lastData: statsData.lastData,
      additionalInfo: statsData.additionalInfo
    }

    showModal.value = true
  } catch (error) {
    console.error("Error fetching stats:", error)
  }
}

// Close modal
const closeModal = () => {
  showModal.value = false
}

onMounted(async () => {
  drawBubbleChart()
})
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
}

.right-panel {
  width: 100%;
  background-color: white;
  padding: 1rem;
  overflow: hidden;
}

#d3-bubbles {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  max-width: 400px;
  width: 100%;
  text-align: center;
}

button {
  margin-top: 10px;
  padding: 10px 20px;
  background-color: #007BFF;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style>
