<template>
    <div class="metric-card" :class="customClass">
      <h3>{{ title }}</h3>
      <slot></slot>
    </div>
  </template>
  
  <script>
  export default {
    name: 'MetricCard',
    props: {
      title: {
        type: String,
        required: true
      },
      customClass: {
        type: String,
        default: ''
      }
    }
  }
  </script>
  
  <style scoped>
  .metric-card {
    background-color: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    position: relative;
    overflow: hidden;
  }
  
  .metric-card h3 {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1rem;
    color: #666;
  }
  </style>