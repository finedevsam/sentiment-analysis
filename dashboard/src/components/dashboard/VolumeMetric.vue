<template>
    <MetricCard title="Tweet Volume">
      <div class="volume-score">{{ formattedVolume }}</div>
      <div class="volume-label">tweets analyzed</div>
      <div class="trend" :class="volumeTrend.trend">
        {{ volumeTrend.trend === 'up' ? '↑' : '↓' }} 
        {{ volumeTrend.change.toFixed(1) }}% from previous period
      </div>
      <div class="volume-chart">
        <div v-for="(bar, index) in volumeBars" :key="index" 
             class="volume-bar" 
             :style="{ height: `${bar}%`, backgroundColor: getVolumeBarColor(index) }">
        </div>
      </div>
    </MetricCard>
  </template>
  
  <script>
  import MetricCard from './MetricCard.vue';
  
  export default {
    name: 'VolumeMetric',
    components: {
      MetricCard
    },
    props: {
      volume: {
        type: Number,
        required: true
      },
      volumeTrend: {
        type: Object,
        required: true
      },
      volumeBars: {
        type: Array,
        required: true
      }
    },
    computed: {
      formattedVolume() {
        return new Intl.NumberFormat().format(this.volume);
      }
    },
    methods: {
      getVolumeBarColor(index) {
        // Gradient from light to dark teal
        const colors = [
          'rgba(56, 178, 172, 0.5)',
          'rgba(56, 178, 172, 0.6)',
          'rgba(56, 178, 172, 0.7)',
          'rgba(56, 178, 172, 0.8)',
          'rgba(56, 178, 172, 0.9)',
          'rgba(56, 178, 172, 1.0)',
          'rgba(56, 178, 172, 1.0)'
        ];
        return colors[index];
      }
    }
  }
  </script>
  
  <style scoped>
  .volume-score {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
  }
  
  .volume-label {
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
  
  .volume-chart {
    display: flex;
    align-items: flex-end;
    height: 50px;
    gap: 4px;
    margin-top: 1rem;
  }
  
  .volume-bar {
    flex: 1;
    border-radius: 2px 2px 0 0;
  }
  </style>