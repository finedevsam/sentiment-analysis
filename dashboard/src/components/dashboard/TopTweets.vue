<template>
    <ChartContainer title="Top Influential Tweets">
      <div class="tweets-list">
        <div v-for="(tweet, index) in tweets" :key="index" class="tweet-item">
          <div class="tweet-sentiment-indicator" :style="{ backgroundColor: getSentimentColor(tweet.sentiment) }"></div>
          <div class="tweet-content">
            <div class="tweet-header">
              <div class="tweet-author">
                <img :src="tweet.avatar || 'https://via.placeholder.com/24'" class="tweet-avatar" alt="User avatar" />
                @{{ tweet.author }}
              </div>
              <div class="tweet-time">{{ tweet.time }}</div>
            </div>
            <div class="tweet-text">{{ tweet.text }}</div>
            <div class="tweet-metrics">
              <span>❤️ {{ tweet.likes }}</span>
              <span>🔄 {{ tweet.retweets }}</span>
              <span>💬 {{ tweet.replies }}</span>
              <span class="tweet-sentiment-score" :style="{ color: getSentimentColor(tweet.sentiment) }">
                Sentiment: {{ tweet.sentiment.toFixed(1) }}/10
              </span>
            </div>
          </div>
        </div>
      </div>
    </ChartContainer>
  </template>
  
  <script>
  import ChartContainer from './ChartContainer.vue';
  
  export default {
    name: 'TopTweets',
    components: {
      ChartContainer
    },
    props: {
      tweets: {
        type: Array,
        required: true
      }
    },
    methods: {
      getSentimentColor(score) {
        if (score >= 7) return '#10b981'; // green
        if (score >= 5) return '#f59e0b'; // amber
        return '#ef4444'; // red
      }
    }
  }
  </script>
  
  <style scoped>
  .tweets-list {
    max-height: 250px;
    overflow-y: auto;
  }
  
  .tweet-item {
    display: flex;
    padding: 0.75rem 0;
    border-bottom: 1px solid #eee;
  }
  
  .tweet-item:last-child {
    border-bottom: none;
  }
  
  .tweet-sentiment-indicator {
    width: 4px;
    margin-right: 0.75rem;
    border-radius: 2px;
  }
  
  .tweet-content {
    flex: 1;
  }
  
  .tweet-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.25rem;
  }
  
  .tweet-author {
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .tweet-avatar {
    width: 1.5rem;
    height: 1.5rem;
    border-radius: 50%;
  }
  
  .tweet-time {
    font-size: 0.75rem;
    color: #666;
  }
  
  .tweet-text {
    margin-bottom: 0.5rem;
    line-height: 1.4;
  }
  
  .tweet-metrics {
    display: flex;
    gap: 1rem;
    color: #666;
    font-size: 0.875rem;
  }
  
  .tweet-sentiment-score {
    margin-left: auto;
    font-weight: 600;
  }
  </style>