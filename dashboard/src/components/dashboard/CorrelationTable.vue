<template>
    <div class="data-table-section">
      <div class="table-header">
        <h3>Historical Correlation Analysis</h3>
        <div class="table-actions">
          <button class="table-action-btn">
            <span>📊</span> Export Data
          </button>
          <button class="table-action-btn">
            <span>🔍</span> Detailed View
          </button>
        </div>
      </div>
      <div class="table-container">
        <table class="correlation-table">
          <thead>
            <tr>
              <th>Time Period</th>
              <th>Avg. Sentiment</th>
              <th>Stock Change</th>
              <th>Correlation</th>
              <th>Prediction Accuracy</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(period, index) in data" :key="index">
              <td>{{ period.label }}</td>
              <td>
                <div class="table-sentiment" :style="{ color: getSentimentColor(period.sentiment) }">
                  {{ period.sentiment.toFixed(1) }}/10
                  <div class="mini-bar" :style="{ width: `${(period.sentiment / 10) * 100}%`, backgroundColor: getSentimentColor(period.sentiment) }"></div>
                </div>
              </td>
              <td :class="period.stockChange > 0 ? 'up' : 'down'">
                {{ period.stockChange > 0 ? '▲' : '▼' }} {{ Math.abs(period.stockChange).toFixed(2) }}%
              </td>
              <td>
                <div class="correlation-value">{{ period.correlation.toFixed(2) }}</div>
                <div class="correlation-strength" :class="getCorrelationClass(period.correlation)">
                  {{ getCorrelationLabel(period.correlation) }}
                </div>
              </td>
              <td>
                <div class="accuracy-meter">
                  <div class="accuracy-value">{{ period.accuracy.toFixed(1) }}%</div>
                  <div class="accuracy-bar" :style="{ width: `${period.accuracy}%` }"></div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'CorrelationTable',
    props: {
      data: {
        type: Array,
        required: true
      }
    },
    methods: {
      getSentimentColor(score) {
        if (score >= 7) return '#10b981'; // green
        if (score >= 5) return '#f59e0b'; // amber
        return '#ef4444'; // red
      },
      getCorrelationClass(correlation) {
        if (correlation >= 0.7) return 'strong';
        if (correlation >= 0.5) return 'moderate';
        return 'weak';
      },
      getCorrelationLabel(correlation) {
        if (correlation >= 0.7) return 'Strong';
        if (correlation >= 0.5) return 'Moderate';
        return 'Weak';
      }
    }
  }
  </script>
  
  <style scoped>
  .data-table-section {
    background-color: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
  
  .table-header h3 {
    margin: 0;
    font-size: 1rem;
    color: #666;
  }
  
  .table-actions {
    display: flex;
    gap: 0.5rem;
  }
  
  .table-action-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    background-color: #f0f0f0;
    border: none;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .table-action-btn:hover {
    background-color: #e0e0e0;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .correlation-table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .correlation-table th,
  .correlation-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #eee;
  }
  
  .correlation-table th {
    font-weight: 600;
    color: #666;
  }
  
  .table-sentiment {
    position: relative;
  }
  
  .mini-bar {
    height: 4px;
    border-radius: 2px;
    margin-top: 4px;
  }
  
  .correlation-value {
    font-weight: 600;
  }
  
  .correlation-strength {
    font-size: 0.75rem;
  }
  
  .correlation-strength.strong {
    color: #10b981;
  }
  
  .correlation-strength.moderate {
    color: #f59e0b;
  }
  
  .correlation-strength.weak {
    color: #ef4444;
  }
  
  .accuracy-meter {
    position: relative;
  }
  
  .accuracy-value {
    font-weight: 600;
    margin-bottom: 4px;
  }
  
  .accuracy-bar {
    height: 4px;
    background-color: #10b981;
    border-radius: 2px;
  }
  
  .up {
    color: #10b981;
  }
  
  .down {
    color: #ef4444;
  }
  </style>