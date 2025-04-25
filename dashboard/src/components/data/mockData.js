export const companies = [
    { id: 'AAPL', name: 'Apple Inc.' },
    { id: 'GOOGL', name: 'Alphabet Inc.' },
    { id: 'MSFT', name: 'Microsoft Corp.' },
    { id: 'AMZN', name: 'Amazon.com Inc.' },
    { id: 'NFLX', name: 'Netflix.' },
    { id: 'TSLA', name: 'Tesla Inc.' },
    { id: 'NVDA', name: 'Nvidia.' },
    { id: 'AMD', name: 'AMD' },
  ];
  
  export const sentimentData = {
    overall: {
      score: 7.2,
      label: 'Positive',
      trend: 'up',
      change: 3.5
    },
    tweetVolume: 24863,
    volumeTrend: {
      trend: 'up',
      change: 12.3
    },
    distribution: {
      positive: 62,
      neutral: 25,
      negative: 13
    },
    timeline: [
      { date: '2023-04-01', score: 6.8 },
      { date: '2023-04-02', score: 6.9 },
      { date: '2023-04-03', score: 7.1 },
      { date: '2023-04-04', score: 6.7 },
      { date: '2023-04-05', score: 6.5 },
      { date: '2023-04-06', score: 6.8 },
      { date: '2023-04-07', score: 7.2 }
    ]
  };
  
  export const stockData = {
    currentPrice: 178.72,
    change: 0.92,
    changePercent: 0.52,
    prediction: {
      direction: 'up',
      confidence: 72.5
    },
    timeline: [
      { date: '2023-04-01', price: 172.50 },
      { date: '2023-04-02', price: 173.75 },
      { date: '2023-04-03', price: 175.20 },
      { date: '2023-04-04', price: 174.90 },
      { date: '2023-04-05', price: 176.30 },
      { date: '2023-04-06', price: 177.80 },
      { date: '2023-04-07', price: 178.72 }
    ]
  };
  
  export const topTweets = [
    {
      author: 'techanalyst',
      avatar: 'https://via.placeholder.com/24?text=TA',
      text: 'Apple\'s new product announcement exceeded all expectations. The innovation is back! #Apple',
      sentiment: 9.2,
      likes: 1243,
      retweets: 532,
      replies: 89,
      time: '2h ago'
    },
    {
      author: 'investorprime',
      avatar: 'https://via.placeholder.com/24?text=IP',
      text: 'Strong quarterly results from $AAPL again. Revenue growth in services is the key story here.',
      sentiment: 7.8,
      likes: 876,
      retweets: 321,
      replies: 54,
      time: '4h ago'
    },
    {
      author: 'marketwatcher',
      avatar: 'https://via.placeholder.com/24?text=MW',
      text: 'Some concerns about supply chain issues affecting next quarter\'s iPhone production. $AAPL',
      sentiment: 4.2,
      likes: 567,
      retweets: 189,
      replies: 76,
      time: '6h ago'
    },
    {
      author: 'techreview',
      avatar: 'https://via.placeholder.com/24?text=TR',
      text: 'The new MacBook Pro is impressive but the price point remains a barrier for many consumers.',
      sentiment: 5.5,
      likes: 432,
      retweets: 112,
      replies: 67,
      time: '12h ago'
    }
  ];
  
  export const correlationData = [
    { label: 'Last Week', sentiment: 7.2, stockChange: 3.45, correlation: 0.78, accuracy: 82.5 },
    { label: 'Last Month', sentiment: 6.8, stockChange: 2.12, correlation: 0.72, accuracy: 76.3 },
    { label: 'Last Quarter', sentiment: 6.2, stockChange: -1.23, correlation: 0.65, accuracy: 71.8 },
    { label: 'Year to Date', sentiment: 6.5, stockChange: 12.87, correlation: 0.68, accuracy: 74.2 }
  ];
  
  export const comparisonData = [
    { id: 'AAPL', name: 'Apple', sentiment: 7.2, stockTrend: 'up', stockChange: 0.52 },
    { id: 'GOOGL', name: 'Google', sentiment: 6.8, stockTrend: 'up', stockChange: 0.35 },
    { id: 'MSFT', name: 'Microsoft', sentiment: 7.5, stockTrend: 'up', stockChange: 0.78 },
    { id: 'AMZN', name: 'Amazon', sentiment: 6.2, stockTrend: 'down', stockChange: -0.42 },
    { id: 'META', name: 'Meta', sentiment: 5.8, stockTrend: 'down', stockChange: -0.65 },
    { id: 'TSLA', name: 'Tesla', sentiment: 6.5, stockTrend: 'up', stockChange: 1.23 }
  ];
  
  // Generate random volume bars for the volume chart
  export const volumeBars = [45, 60, 75, 55, 80, 65, 90];
  
  export function getCompanyLogo(companyId) {
    // In a real app, you would use actual company logos
    return `/logos/${companyId.toLowerCase()}.png`;
  }
  
  export function getCompanyName(companyId) {
    const company = companies.find(c => c.id === companyId);
    return company ? company.name : companyId;
  }