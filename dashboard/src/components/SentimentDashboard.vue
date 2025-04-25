<template>
    <div class="dashboard">
      <DashboardHeader 
        v-model:selectedCompany="selectedCompany"
        v-model:selectedTimeframe="selectedTimeframe"
        :companies="companies"
        @refresh="refreshData"
      />
  
      <div class="dashboard-content">
        <CompanyBanner 
          :companyId="selectedCompany"
          :companyName="getCompanyName(selectedCompany)"
          :companyLogo="getCompanyLogo(selectedCompany)"
          :stockPrice="stockData.currentPrice"
          :stockChange="stockData.change"
          :stockChangePercent="stockData.changePercent"
        />
  
        <div class="main-metrics">
          <SentimentMetric 
            :score="sentimentData.overall.score"
            :label="sentimentData.overall.label"
            :trend="sentimentData.overall.trend"
            :change="sentimentData.overall.change"
          />
          
          <VolumeMetric 
            :volume="sentimentData.tweetVolume"
            :volumeTrend="sentimentData.volumeTrend"
            :volumeBars="volumeBars"
          />
          
          <PredictionMetric 
            :prediction="stockData.prediction"
            :timeframe="selectedTimeframe"
          />
        </div>
  
        <div class="chart-grid">
          <SentimentTrendChart />
          <StockCorrelationChart />
          <SentimentDistributionChart :distribution="sentimentData.distribution" />
          <TopTweets :tweets="topTweets" />
        </div>
  
        <CompanyComparison :companies="comparisonData" />
        <CorrelationTable :data="correlationData" />
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import DashboardHeader from './dashboard/DashboardHeader.vue';
  import CompanyBanner from './dashboard/CompanyBanner.vue';
  import SentimentMetric from './dashboard/SentimentMetric.vue';
  import VolumeMetric from './dashboard/VolumeMetric.vue';
  import PredictionMetric from './dashboard/PredictionMetric.vue';
  import SentimentTrendChart from './dashboard/SentimentTrendChart.vue';
  import StockCorrelationChart from './dashboard/StockCorrelationChart.vue';
  import SentimentDistributionChart from './dashboard/SentimentDistributionChart.vue';
  import TopTweets from './dashboard/TopTweets.vue';
  import CompanyComparison from './dashboard/CompanyComparison.vue';
  import CorrelationTable from './dashboard/CorrelationTable.vue';
  
  import { 
    companies, 
    sentimentData, 
    stockData, 
    topTweets, 
    correlationData, 
    comparisonData, 
    volumeBars,
    getCompanyLogo,
    getCompanyName
  } from './data/mockData';
  
  export default {
    name: 'SentimentDashboard',
    components: {
      DashboardHeader,
      CompanyBanner,
      SentimentMetric,
      VolumeMetric,
      PredictionMetric,
      SentimentTrendChart,
      StockCorrelationChart,
      SentimentDistributionChart,
      TopTweets,
      CompanyComparison,
      CorrelationTable
    },
    setup() {
      const selectedCompany = ref('AAPL');
      const selectedTimeframe = ref('week');
      console.log(companies)
      function updateData() {
        // In a real app, this would fetch new data based on selections
        console.log(`Fetching data for ${selectedCompany.value} over ${selectedTimeframe.value}`);
        // For demo purposes, we'll just simulate a data update
        setTimeout(() => {
          // Randomize some data to simulate changes
          sentimentData.overall.score = 5 + Math.random() * 5;
          sentimentData.overall.trend = Math.random() > 0.5 ? 'up' : 'down';
          sentimentData.overall.change = Math.random() * 5;
          stockData.prediction.confidence = 50 + Math.random() * 40;
          stockData.prediction.direction = Math.random() > 0.4 ? 'up' : 'down';
        }, 500);
      }
      
      function refreshData() {
        // Simulate a refresh with loading state
        console.log('Refreshing data...');
        setTimeout(updateData, 800);
      }
      
      onMounted(() => {
        // Initialize data
        console.log('Dashboard mounted');
      });
      
      return {
        selectedCompany,
        selectedTimeframe,
        companies,
        sentimentData,
        stockData,
        topTweets,
        correlationData,
        comparisonData,
        volumeBars,
        getCompanyLogo,
        getCompanyName,
        updateData,
        refreshData
      };
    }
  }
  </script>
  
  <style>
  .dashboard {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #333;
    background-color: #f5f5f7;
    min-height: 100vh;
  }
  
  .dashboard-content {
    padding: 1.5rem;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .main-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }
  
  .chart-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }
  
  @media (max-width: 768px) {
    .chart-grid {
      grid-template-columns: 1fr;
    }
  }
  </style>