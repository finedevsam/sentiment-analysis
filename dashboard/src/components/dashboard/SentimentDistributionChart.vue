<template>
    <ChartContainer title="Sentiment Distribution">
      <div class="donut-chart-container">
        <div class="donut-chart">
          <svg viewBox="0 0 42 42" class="donut">
            <circle class="donut-hole" cx="21" cy="21" r="15.91549430918954" fill="#fff"></circle>
            <circle class="donut-ring" cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#d2d3d4" stroke-width="3"></circle>
            
            <!-- Positive segment -->
            <circle class="donut-segment positive-segment" cx="21" cy="21" r="15.91549430918954" 
                    fill="transparent" stroke="#10b981" stroke-width="3" 
                    stroke-dasharray="62 38" stroke-dashoffset="25"></circle>
            
            <!-- Neutral segment -->
            <circle class="donut-segment neutral-segment" cx="21" cy="21" r="15.91549430918954" 
                    fill="transparent" stroke="#f59e0b" stroke-width="3" 
                    stroke-dasharray="25 75" stroke-dashoffset="-37"></circle>
            
            <!-- Negative segment -->
            <circle class="donut-segment negative-segment" cx="21" cy="21" r="15.91549430918954" 
                    fill="transparent" stroke="#ef4444" stroke-width="3" 
                    stroke-dasharray="13 87" stroke-dashoffset="-62"></circle>
          </svg>
          <div class="donut-text">
            <div class="donut-title">Sentiment</div>
            <div class="donut-subtitle">Distribution</div>
          </div>
        </div>
        <div class="distribution-legend">
          <div class="distribution-item">
            <div class="distribution-color positive"></div>
            <div class="distribution-label">Positive</div>
            <div class="distribution-value">{{ distribution.positive }}%</div>
          </div>
          <div class="distribution-item">
            <div class="distribution-color neutral"></div>
            <div class="distribution-label">Neutral</div>
            <div class="distribution-value">{{ distribution.neutral }}%</div>
          </div>
          <div class="distribution-item">
            <div class="distribution-color negative"></div>
            <div class="distribution-label">Negative</div>
            <div class="distribution-value">{{ distribution.negative }}%</div>
          </div>
        </div>
      </div>
    </ChartContainer>
  </template>
  
  <script>
  import ChartContainer from './ChartContainer.vue';
  
  export default {
    name: 'SentimentDistributionChart',
    components: {
      ChartContainer
    },
    props: {
      distribution: {
        type: Object,
        required: true
      }
    }
  }
  </script>
  
  <style scoped>
  .donut-chart-container {
    display: flex;
    height: 100%;
  }
  
  .donut-chart {
    position: relative;
    width: 50%;
  }
  
  .donut {
    width: 100%;
    height: 100%;
  }
  
  .donut-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
  }
  
  .donut-title {
    font-weight: 600;
    font-size: 0.875rem;
  }
  
  .donut-subtitle {
    font-size: 0.75rem;
    color: #666;
  }
  
  .distribution-legend {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 1rem;
    width: 50%;
  }
  
  .distribution-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .distribution-color {
    width: 12px;
    height: 12px;
    border-radius: 2px;
  }
  
  .distribution-color.positive {
    background-color: #10b981;
  }
  
  .distribution-color.neutral {
    background-color: #f59e0b;
  }
  
  .distribution-color.negative {
    background-color: #ef4444;
  }
  
  .distribution-value {
    font-weight: 600;
    margin-left: auto;
  }
  
  @media (max-width: 480px) {
    .donut-chart-container {
      flex-direction: column;
    }
    
    .donut-chart, .distribution-legend {
      width: 100%;
    }
    
    .donut-chart {
      height: 150px;
    }
  }
  </style>