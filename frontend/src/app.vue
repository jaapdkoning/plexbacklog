<template>
  <main>
    <h1>PlexBacklog</h1>
    <div>
      <label for="type">Type:</label>
      <select id="type" v-model="type">
        <option value="radarr">Film</option>
        <option value="sonarr">Serie</option>
        <option value="lidarr">Muziek</option>
      </select>
    </div>

    <div>
      <label for="query">Zoekterm:</label>
      <input id="query" v-model="query" placeholder="Bijv. 'Dune'" />
      <button @click="search">Zoeken</button>
    </div>

    <div v-if="results.length">
      <h2>Resultaten</h2>
      <ul>
        <li v-for="item in results" :key="item.id">
          {{ item.title || item.name }}
          <button @click="add(item)">Toevoegen</button>
        </li>
      </ul>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const type = ref('radarr')
const query = ref('')
const results = ref<any[]>([])

async function search() {
  const res = await axios.post('/api/search', { type: type.value, query: query.value })
  results.value = res.data
}

async function add(item: any) {
  await axios.post('/api/add', { type: type.value, payload: item })
  alert('Toegevoegd!')
}
</script>

<style>
body {
  font-family: sans-serif;
  padding: 2rem;
  background: #f8f8f8;
}

input, select {
  margin: 0.5rem 0;
}
</style>
