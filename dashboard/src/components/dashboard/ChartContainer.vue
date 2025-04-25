<template>
    <div class="chart-container">
      <div class="chart-header" v-if="showHeader">
        <h3>{{ title }}</h3>
        <div class="chart-legend" v-if="legend && legend.length">
          <div class="legend-item" v-for="(item, index) in legend" :key="index">
            <div class="legend-color" :style="{ backgroundColor: item.color }"></div>
            <div class="legend-label">{{ item.label }}</div>
          </div>
        </div>
      </div>
      <div class="chart">
        <slot></slot>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ChartContainer',
    props: {
      title: {
        type: String,
        required: true
      },
      showHeader: {
        type: Boolean,
        default: true
      },
      legend: {
        type: Array,
        default: () => []
      }
    }
  }
  </script>
  
  <style scoped>
  .chart-container {
    background-color: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
  
  .chart-header h3 {
    margin: 0;
    font-size: 1rem;
    color: #666;
  }
  
  .chart-legend {
    display: flex;
    gap: 1rem;
  }
  
  .legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.75rem;
  }
  
  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 2px;
  }
  
  .chart {
    height: 250px;
    position: relative;
  }
  </style>