<template>
    <MetricCard title="Overall Sentiment">
      <div class="sentiment-meter">
        <div class="meter">
          <div class="meter-value" :style="{ width: `${(score / 10) * 100}%`, backgroundColor: sentimentColor }"></div>
        </div>
        <div class="meter-labels">
          <span>Negative</span>
          <span>Neutral</span>
          <span>Positive</span>
        </div>
      </div>
      <div class="sentiment-score" :style="{ color: sentimentColor }">
        {{ score.toFixed(1) }}/10
      </div>
      <div class="sentiment-label">{{ label }}</div>
      <div class="trend" :class="trend">
        {{ trend === 'up' ? '↑' : '↓' }} 
        {{ change.toFixed(1) }}% from previous period
      </div>
    </MetricCard>
  </template>
  
  <script>
  import MetricCard from './MetricCard.vue';
  
  export default {
    name: 'SentimentMetric',
    components: {
      MetricCard
    },
    props: {
      score: {
        type: Number,
        required: true
      },
      label: {
        type: String,
        required: true
      },
      trend: {
        type: String,
        required: true,
        validator: value => ['up', 'down'].includes(value)
      },
      change: {
        type: Number,
        required: true
      }
    },
    computed: {
      sentimentColor() {
        if (this.score >= 7) return '#10b981'; // green
        if (this.score >= 5) return '#f59e0b'; // amber
        return '#ef4444'; // red
      }
    }
  }
  </script>
  
  <style scoped>
  .sentiment-meter {
    margin-bottom: 1rem;
  }
  
  .meter {
    height: 0.5rem;
    background-color: #f0f0f0;
    border-radius: 0.25rem;
    overflow: hidden;
    margin-bottom: 0.25rem;
  }
  
  .meter-value {
    height: 100%;
    border-radius: 0.25rem;
  }
  
  .meter-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #666;
  }
  
  .sentiment-score {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
  }
  
  .sentiment-label {
    color: #666;
    margin-bottom: 1rem;
  }
  
  .trend {
    font-weight: 600;
  }
  
  .up {
    color: #10b981;
  }
  
  .down {
    color: #ef4444;
  }
  </style>