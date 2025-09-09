<template>
    <header class="header">
      <div class="logo-container">
        <div class="logo">
          <span class="logo-icon">📊</span>
          <span class="logo-text">SentiStock</span>
        </div>
      </div>
      <div class="filters">
        <div class="company-selector">
          <label for="company">Company:</label>
          <div class="select-wrapper">
            <select id="company" :value="selectedCompany" @change="$emit('update:selectedCompany', $event.target.value)">
              <option v-for="company in companies" :key="company.id" :value="company.id">
                {{ company.name }}
              </option>
            </select>
          </div>
        </div>
        <div class="time-selector">
          <label for="timeframe">Timeframe:</label>
          <div class="select-wrapper">
            <input id="timeframe" type="date"/>
          </div>
          to
          <div class="select-wrapper">
            <input id="timeframe" type="date"/>
          </div>
        </div>
        <button class="refresh-btn" @click="$emit('refresh')">
          <span class="refresh-icon">↻</span> Refresh
        </button>
      </div>
    </header>
  </template>
  
  <script>
  export default {
    name: 'DashboardHeader',
    props: {
      selectedCompany: {
        type: String,
        required: true
      },
      selectedTimeframe: {
        type: String,
        required: true
      },
      companies: {
        type: Array,
        required: true
      }
    },
    emits: ['update:selectedCompany', 'update:selectedTimeframe', 'refresh']
  }
  </script>
  
  <style scoped>
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    background-color: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .logo-container {
    display: flex;
    align-items: center;
  }
  
  .logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.5rem;
    font-weight: 700;
    color: #222;
  }
  
  .logo-icon {
    font-size: 1.75rem;
  }
  
  .filters {
    display: flex;
    gap: 1rem;
    align-items: center;
  }
  
  .company-selector,
  .time-selector {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .select-wrapper {
    position: relative;
  }
  
  select {
    padding: 0.5rem 2rem 0.5rem 0.75rem;
    border-radius: 0.375rem;
    border: 1px solid #ddd;
    background-color: white;
    appearance: none;
    min-width: 150px;
  }
  
  .select-wrapper::after {
    content: '▼';
    font-size: 0.7rem;
    position: absolute;
    right: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    color: #666;
  }
  
  .refresh-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: #f0f0f0;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .refresh-btn:hover {
    background-color: #e0e0e0;
  }
  
  .user-menu {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .notifications {
    position: relative;
  }
  
  .notification-icon {
    font-size: 1.25rem;
    cursor: pointer;
  }
  
  .notification-badge {
    position: absolute;
    top: -5px;
    right: -5px;
    background-color: #ef4444;
    color: white;
    font-size: 0.75rem;
    width: 1rem;
    height: 1rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .user-avatar img {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    cursor: pointer;
  }
  
  @media (max-width: 768px) {
    .header {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
      padding: 1rem;
    }
    
    .filters {
      flex-direction: column;
      align-items: flex-start;
      width: 100%;
      gap: 0.5rem;
    }
    
    .company-selector,
    .time-selector {
      width: 100%;
    }
    
    select {
      width: 100%;
    }
    
    .refresh-btn {
      width: 100%;
      justify-content: center;
    }
    
    .user-menu {
      position: absolute;
      top: 1rem;
      right: 1rem;
    }
  }
  </style>