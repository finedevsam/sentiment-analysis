export function useSentiment() {
    function getSentimentColor(score) {
      if (score >= 7) return '#10b981'; // green
      if (score >= 5) return '#f59e0b'; // amber
      return '#ef4444'; // red
    }
    
    function getSentimentClass(score) {
      if (score >= 7) return 'positive';
      if (score >= 5) return 'neutral';
      return 'negative';
    }
    
    function getCorrelationClass(correlation) {
      if (correlation >= 0.7) return 'strong';
      if (correlation >= 0.5) return 'moderate';
      return 'weak';
    }
    
    function getCorrelationLabel(correlation) {
      if (correlation >= 0.7) return 'Strong';
      if (correlation >= 0.5) return 'Moderate';
      return 'Weak';
    }
    
    function formatNumber(num) {
      return new Intl.NumberFormat().format(num);
    }
    
    return {
      getSentimentColor,
      getSentimentClass,
      getCorrelationClass,
      getCorrelationLabel,
      formatNumber
    };
  }