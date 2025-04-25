<template>
    <MetricCard title="Stock Prediction" customClass="prediction-card">
      <div class="prediction-indicator">
        <div class="arrow" :class="prediction.direction">
          {{ prediction.direction === 'up' ? '↑' : '↓' }}
        </div>
      </div>
      <div class="prediction-score" :class="predictionClass">
        {{ prediction.confidence.toFixed(1) }}% confidence
      </div>
      <div class="prediction-label">
        {{ prediction.direction === 'up' ? 'Bullish' : 'Bearish' }} prediction
      </div>
      <div class="prediction-time">
        Based on {{ timeframeText }} data
      </div>
    </MetricCard>
  </template>
  
  <script>
  import MetricCard from './MetricCard.vue';
  
  export default {
    name: 'PredictionMetric',
    components: {
      MetricCard
    },
    props: {
      prediction: {
        type: Object,
        required: true
      },
      timeframe: {
        type: String,
        required: true
      }
    },
    computed: {
      predictionClass() {
        return this.prediction.direction === 'up' ? 'positive' : 'negative';
      },
      timeframeText() {
        switch(this.timeframe) {
          case 'day': return '24h';
          case 'week': return '7d';
          case 'month': return '30d';
          case 'quarter': return '90d';
          default: return this.timeframe;
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .prediction-card {
    position: relative;
  }
  
  .prediction-indicator {
    position: absolute;
    top: 1.5rem;
    right: 1.5rem;
  }
  
  .arrow {
    font-size: 2rem;
    font-weight: bold;
  }
  
  .arrow.up {
    color: #10b981;
  }
  
  .arrow.down {
    color: #ef4444;
  }
  
  .prediction-score {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
  }
  
  .prediction-label {
    color: #666;
    margin-bottom: 1rem;
  }
  
  .prediction-time {
    font-size: 0.875rem;
    color: #666;
    margin-top: 0.5rem;
  }
  
  .positive {
    color: #10b981;
  }
  
  .negative {
    color: #ef4444;
  }
  </style>