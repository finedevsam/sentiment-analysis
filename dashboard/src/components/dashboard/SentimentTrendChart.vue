<template>
    <ChartContainer 
      title="Sentiment Trend" 
      :legend="[
        { color: 'rgba(56, 178, 172, 0.6)', label: 'Sentiment Score' },
        { color: 'rgba(245, 158, 11, 0.3)', label: 'Average' }
      ]"
    >
      <div class="chart-placeholder">
        <div class="line-chart">
          <svg viewBox="0 0 500 200" class="chart-svg">
            <!-- Background grid -->
            <g class="grid">
              <line x1="0" y1="50" x2="500" y2="50" />
              <line x1="0" y1="100" x2="500" y2="100" />
              <line x1="0" y1="150" x2="500" y2="150" />
            </g>
            
            <!-- Sentiment line -->
            <path d="M0,100 C50,80 100,60 150,70 C200,80 250,40 300,30 C350,20 400,50 450,40 C480,35 500,30 500,30" 
                  class="line sentiment-line" />
            
            <!-- Average line -->
            <path d="M0,90 L500,70" class="line average-line" />
            
            <!-- Data points -->
            <g class="data-points">
              <circle cx="0" cy="100" r="4" />
              <circle cx="71" cy="80" r="4" />
              <circle cx="142" cy="70" r="4" />
              <circle cx="213" cy="60" r="4" />
              <circle cx="284" cy="30" r="4" />
              <circle cx="355" cy="40" r="4" />
              <circle cx="426" cy="35" r="4" />
              <circle cx="500" cy="30" r="4" />
            </g>
          </svg>
        </div>
        <div class="x-axis">
          <div class="tick" v-for="(date, index) in dates" :key="index">{{ date }}</div>
        </div>
      </div>
    </ChartContainer>
  </template>
  
  <script>
  import ChartContainer from './ChartContainer.vue';
  
  export default {
    name: 'SentimentTrendChart',
    components: {
      ChartContainer
    },
    data() {
      return {
        dates: ['Jul 1', 'Jul 2', 'Jul 3', 'Jul 4', 'Jul 5', 'Jul 6', 'Jul 7']
      };
    }
  }
  </script>
  
  <style scoped>
  .chart-placeholder {
    height: 100%;
    position: relative;
  }
  
  .line-chart {
    height: calc(100% - 20px);
  }
  
  .chart-svg {
    width: 100%;
    height: 100%;
  }
  
  .grid line {
    stroke: #e5e7eb;
    stroke-width: 1;
  }
  
  .line {
    fill: none;
    stroke-width: 3;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  
  .sentiment-line {
    stroke: rgba(56, 178, 172, 0.6);
  }
  
  .average-line {
    stroke: rgba(245, 158, 11, 0.3);
    stroke-width: 2;
    stroke-dasharray: 5, 5;
  }
  
  .data-points circle {
    fill: white;
    stroke: rgba(56, 178, 172, 0.8);
    stroke-width: 2;
  }
  
  .x-axis {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #666;
    margin-top: 0.5rem;
  }
  </style>