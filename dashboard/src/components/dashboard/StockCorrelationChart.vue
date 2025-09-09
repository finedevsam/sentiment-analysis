<template>
    <ChartContainer 
      title="Stock Price vs Sentiment" 
      :legend="[
        { color: 'rgba(239, 68, 68, 0.6)', label: 'Stock Price' },
        { color: 'rgba(56, 178, 172, 0.6)', label: 'Sentiment' }
      ]"
    >
      <div class="chart-placeholder">
        <div class="dual-axis-chart">
          <svg viewBox="0 0 500 200" class="chart-svg">
            <!-- Background grid -->
            <g class="grid">
              <line x1="0" y1="50" x2="500" y2="50" />
              <line x1="0" y1="100" x2="500" y2="100" />
              <line x1="0" y1="150" x2="500" y2="150" />
            </g>
            
            <!-- Stock price line -->
            <path d="M0,150 C50,140 100,130 150,120 C200,110 250,100 300,80 C350,70 400,60 450,50 C480,45 500,40 500,40" 
                  class="line stock-line" />
            
            <!-- Sentiment line -->
            <path d="M0,120 C50,110 100,100 150,90 C200,100 250,70 300,60 C350,50 400,60 450,50 C480,45 500,40 500,40" 
                  class="line sentiment-correlation-line" />
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
    name: 'StockCorrelationChart',
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
  
  .dual-axis-chart {
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
  
  .stock-line {
    stroke: rgba(239, 68, 68, 0.6);
  }
  
  .sentiment-correlation-line {
    stroke: rgba(56, 178, 172, 0.6);
  }
  
  .x-axis {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #666;
    margin-top: 0.5rem;
  }
  </style>