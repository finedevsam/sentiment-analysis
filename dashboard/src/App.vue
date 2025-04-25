<template>
  <SentimentDashboard />
</template>

<script>
import SentimentDashboard from './components/SentimentDashboard.vue'

export default {
  name: 'App',
  components: {
    SentimentDashboard
  }
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>