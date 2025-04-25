<template>
    <div class="company-banner">
      <div class="company-info">
        <div class="company-logo">
          <img :src="companyLogo" :alt="companyName + ' logo'" />
        </div>
        <div class="company-details">
          <h2>{{ companyName }}</h2>
          <div class="company-ticker">${{ companyId }}</div>
        </div>
      </div>
      <div class="stock-summary">
        <div class="stock-price">${{ stockPrice.toFixed(2) }}</div>
        <div class="stock-change" :class="stockChange >= 0 ? 'up' : 'down'">
          {{ stockChange >= 0 ? '▲' : '▼' }} ${{ Math.abs(stockChange).toFixed(2) }} ({{ Math.abs(stockChangePercent).toFixed(2) }}%)
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'CompanyBanner',
    props: {
      companyId: {
        type: String,
        required: true
      },
      companyName: {
        type: String,
        required: true
      },
      companyLogo: {
        type: String,
        required: true
      },
      stockPrice: {
        type: Number,
        required: true
      },
      stockChange: {
        type: Number,
        required: true
      },
      stockChangePercent: {
        type: Number,
        required: true
      }
    }
  }
  </script>
  
  <style scoped>
  .company-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: white;
    border-radius: 0.5rem;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .company-info {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .company-logo img {
    width: 3rem;
    height: 3rem;
    border-radius: 0.5rem;
  }
  
  .company-details h2 {
    margin: 0;
    font-size: 1.5rem;
  }
  
  .company-ticker {
    color: #666;
  }
  
  .stock-summary {
    text-align: right;
  }
  
  .stock-price {
    font-size: 1.5rem;
    font-weight: 700;
  }
  
  .stock-change {
    font-weight: 600;
  }
  
  .up {
    color: #10b981;
  }
  
  .down {
    color: #ef4444;
  }
  
  @media (max-width: 1024px) {
    .company-banner {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
    }
    
    .stock-summary {
      text-align: left;
    }
  }
  </style>