<template>
    <div class="comparison-section">
      <h3>Industry Comparison</h3>
      <div class="comparison-chart">
        <div class="comparison-companies">
          <div v-for="company in companies" :key="company.id" class="comparison-company">
            <div class="company-comparison-logo">
              <img :src="getCompanyLogo(company.id)" :alt="company.name + ' logo'" />
            </div>
            <div class="company-comparison-name">{{ company.name }}</div>
            <div class="company-comparison-sentiment" :style="{ color: getSentimentColor(company.sentiment) }">
              {{ company.sentiment.toFixed(1) }}/10
            </div>
            <div class="company-comparison-bar-container">
              <div class="company-comparison-bar" :style="{ width: `${(company.sentiment / 10) * 100}%`, backgroundColor: getSentimentColor(company.sentiment) }"></div>
            </div>
            <div class="company-comparison-stock" :class="company.stockTrend">
              {{ company.stockTrend === 'up' ? '▲' : '▼' }} {{ company.stockChange.toFixed(2) }}%
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'CompanyComparison',
    props: {
      companies: {
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
      getCompanyLogo(companyId) {
        // In a real app, you would use actual company logos
        return `/logos/${companyId.toLowerCase()}.png`;
      }
    }
  }
  </script>
  
  <style scoped>
  .comparison-section {
    background-color: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin-bottom: 1.5rem;
  }
  
  .comparison-section h3 {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1rem;
    color: #666;
  }
  
  .comparison-companies {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
  }
  
  .comparison-company {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .company-comparison-logo img {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 0.375rem;
    margin-bottom: 0.5rem;
  }
  
  .company-comparison-name {
    font-weight: 600;
    margin-bottom: 0.25rem;
  }
  
  .company-comparison-sentiment {
    font-weight: 700;
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
  }
  
  .company-comparison-bar-container {
    width: 100%;
    height: 0.5rem;
    background-color: #f0f0f0;
    border-radius: 0.25rem;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }
  
  .company-comparison-bar {
    height: 100%;
    border-radius: 0.25rem;
  }
  
  .company-comparison-stock {
    font-weight: 600;
  }
  
  .up {
    color: #10b981;
  }
  
  .down {
    color: #ef4444;
  }
  
  @media (max-width: 768px) {
    .comparison-companies {
      grid-template-columns: 1fr 1fr;
    }
  }
  
  @media (max-width: 480px) {
    .comparison-companies {
      grid-template-columns: 1fr;
    }
  }
  </style>