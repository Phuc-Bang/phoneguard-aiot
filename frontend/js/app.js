// ==========================================================================
// PHONEGUARD AIOT - DASHBOARD LOGIC (WEBSOCKETS & CHART.JS)
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  // UI Selectors
  const connStatusBadge = document.getElementById('connection-status');
  const connStatusText = connStatusBadge.querySelector('.indicator-text');
  const deviceSelector = document.getElementById('device-selector');
  
  const deviceHealthBadge = document.getElementById('device-health-badge');
  const timePredictionText = document.getElementById('time-prediction');
  const metaName = document.getElementById('meta-name');
  const metaModel = document.getElementById('meta-model');
  
  const healthProgressCircle = document.getElementById('health-progress');
  const healthValueText = document.getElementById('health-value');
  const summaryCard = document.getElementById('summary-section');
  
  const batteryFill = document.getElementById('battery-level-fill');
  const batteryPctText = document.getElementById('battery-percentage');
  const batteryVoltText = document.getElementById('battery-voltage');
  const batteryCapText = document.getElementById('battery-capacity');
  const batteryStatusText = document.getElementById('battery-status-text');
  const batteryChargeBolt = document.getElementById('battery-charge-bolt');
  
  const tempFill = document.getElementById('temp-bar-fill');
  const tempValText = document.getElementById('temp-value');
  const tempStatusText = document.getElementById('temp-status-text');
  
  const netTypeBadge = document.getElementById('network-type');
  const netSignalText = document.getElementById('network-signal-strength');
  const netStatusMsg = document.getElementById('network-status-message');
  
  const accXText = document.getElementById('acc-x');
  const accYText = document.getElementById('acc-y');
  const accZText = document.getElementById('acc-z');
  
  const alertsCountBadge = document.getElementById('alerts-count');
  const alertsList = document.getElementById('alerts-list');
  const recommendationsList = document.getElementById('recommendations-list');

  // Chart instances
  let batteryChart = null;
  let accelChart = null;
  
  // Data history for charts
  const maxHistoryPoints = 30;
  const batteryHistory = [];
  const tempHistory = [];
  const timeLabels = [];
  
  const accelXHistory = [];
  const accelYHistory = [];
  const accelZHistory = [];
  const accelLabels = [];
  
  // WebSocket Configuration
  let socket = null;
  const deviceId = "redmi_note_12_turbo";
  
  // Initialize Charts
  function initCharts() {
    // 1. Battery & Temp Chart
    const ctxBattery = document.getElementById('batteryChart').getContext('2d');
    batteryChart = new Chart(ctxBattery, {
      type: 'line',
      data: {
        labels: timeLabels,
        datasets: [
          {
            label: 'Pin (%)',
            data: batteryHistory,
            borderColor: '#39ff14',
            backgroundColor: 'rgba(57, 255, 20, 0.05)',
            borderWidth: 2,
            tension: 0.3,
            fill: true,
            yAxisID: 'y-battery'
          },
          {
            label: 'Nhiệt độ (°C)',
            data: tempHistory,
            borderColor: '#ffaa00',
            backgroundColor: 'rgba(255, 170, 0, 0.05)',
            borderWidth: 2,
            tension: 0.3,
            fill: false,
            yAxisID: 'y-temp'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#94a3b8',
              font: { family: 'Outfit', size: 12 }
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.03)' },
            ticks: { color: '#64748b' }
          },
          'y-battery': {
            type: 'linear',
            position: 'left',
            min: 0,
            max: 100,
            grid: { color: 'rgba(255, 255, 255, 0.03)' },
            ticks: { color: '#94a3b8' }
          },
          'y-temp': {
            type: 'linear',
            position: 'right',
            min: 15,
            max: 60,
            grid: { drawOnChartArea: false },
            ticks: { color: '#94a3b8' }
          }
        }
      }
    });

    // 2. Accelerometer Chart
    const ctxAccel = document.getElementById('accelChart').getContext('2d');
    accelChart = new Chart(ctxAccel, {
      type: 'line',
      data: {
        labels: accelLabels,
        datasets: [
          {
            label: 'X (Ngang)',
            data: accelXHistory,
            borderColor: '#00f0ff',
            borderWidth: 1.5,
            pointRadius: 0,
            tension: 0.2,
            fill: false
          },
          {
            label: 'Y (Dọc)',
            data: accelYHistory,
            borderColor: '#ffaa00',
            borderWidth: 1.5,
            pointRadius: 0,
            tension: 0.2,
            fill: false
          },
          {
            label: 'Z (Trực diện)',
            data: accelZHistory,
            borderColor: '#ff0055',
            borderWidth: 1.5,
            pointRadius: 0,
            tension: 0.2,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#94a3b8',
              font: { family: 'Outfit', size: 11 }
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.03)' },
            ticks: { display: false }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.03)' },
            ticks: { color: '#94a3b8' },
            min: -35,
            max: 35
          }
        }
      }
    });
  }

  // Connect to server WebSocket
  function connectWebSocket() {
    let protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let host = window.location.host;
    
    // Fallback for opening HTML directly in browser
    if (window.location.protocol === 'file:') {
      host = 'localhost:8005';
      protocol = 'ws:';
    }
    
    const wsUrl = `${protocol}//${host}/ws/live`;
    console.log(`Connecting to WebSocket: ${wsUrl}`);
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = () => {
      console.log('WebSocket Connected!');
      connStatusBadge.classList.add('connected');
      connStatusText.innerText = 'Connected';
    };
    
    socket.onclose = () => {
      console.log('WebSocket Disconnected. Reconnecting...');
      connStatusBadge.classList.remove('connected');
      connStatusText.innerText = 'Disconnected';
      setTimeout(connectWebSocket, 3000); // Reconnect in 3s
    };
    
    socket.onerror = (error) => {
      console.error('WebSocket Error: ', error);
    };
    
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.device_id === deviceId) {
          updateUI(data);
        }
      } catch (err) {
        console.error('Error parsing WebSocket message: ', err);
      }
    };
  }

  // Update UI Elements with server telemetry data
  function updateUI(stats) {
    const telemetry = stats.latest_telemetry;
    const device = stats.device_info;
    
    if (device) {
      metaName.innerText = device.name;
      metaModel.innerText = device.model;
      batteryCapText.innerText = `${device.battery_capacity} mAh`;
      
      // Update selector if device id is not present
      if (!Array.from(deviceSelector.options).some(opt => opt.value === device.device_id)) {
        const option = document.createElement('option');
        option.value = device.device_id;
        option.text = device.name;
        deviceSelector.appendChild(option);
      }
    }
    
    if (!telemetry) return;

    // 1. Health Status Card
    const healthPercent = Math.round((1.0 - stats.anomaly_score) * 100);
    healthValueText.innerText = `${healthPercent}%`;
    
    // Update SVG Radial dashoffset
    const perimeter = 2 * Math.PI * 40; // ~251.2
    const offset = perimeter * (1 - healthPercent / 100);
    healthProgressCircle.style.strokeDashoffset = offset;
    
    // Clear previous classes
    summaryCard.className = 'card summary-card';
    deviceHealthBadge.className = 'health-badge';
    
    if (stats.health_status.toLowerCase() === 'good') {
      deviceHealthBadge.innerText = 'Tốt';
      deviceHealthBadge.classList.add('status-good');
    } else if (stats.health_status.toLowerCase() === 'warning') {
      deviceHealthBadge.innerText = 'Cảnh báo';
      deviceHealthBadge.classList.add('status-warning');
      summaryCard.classList.add('warn');
    } else {
      deviceHealthBadge.innerText = 'Nguy hiểm';
      deviceHealthBadge.classList.add('status-critical');
      summaryCard.classList.add('crit');
    }
    
    timePredictionText.innerText = stats.time_to_empty_or_full;

    // 2. Battery Card
    batteryPctText.innerText = `${Math.round(telemetry.battery_level)}%`;
    batteryFill.style.width = `${telemetry.battery_level}%`;
    batteryVoltText.innerText = telemetry.battery_voltage ? `${telemetry.battery_voltage.toFixed(2)} V` : '-- V';
    
    const batStatus = telemetry.battery_status.toLowerCase();
    if (batStatus === 'charging') {
      batteryStatusText.innerText = 'Đang sạc';
      batteryStatusText.style.color = 'var(--color-success)';
      batteryChargeBolt.classList.remove('hidden');
      batteryFill.style.background = 'linear-gradient(90deg, #2ecc71, var(--color-success))';
    } else if (batStatus === 'full') {
      batteryStatusText.innerText = 'Đầy pin';
      batteryStatusText.style.color = 'var(--color-success)';
      batteryChargeBolt.classList.add('hidden');
      batteryFill.style.background = 'var(--color-success)';
    } else {
      batteryStatusText.innerText = 'Đang xả pin';
      batteryStatusText.style.color = 'var(--text-muted)';
      batteryChargeBolt.classList.add('hidden');
      
      // If low battery, turn red
      if (telemetry.battery_level <= 20) {
        batteryFill.style.background = 'var(--color-danger)';
        batteryFill.style.boxShadow = '0 0 15px var(--color-danger-glow)';
      } else {
        batteryFill.style.background = 'linear-gradient(90deg, #3498db, var(--color-primary))';
        batteryFill.style.boxShadow = '0 0 15px var(--color-primary-glow)';
      }
    }

    // 3. Temperature Card
    tempValText.innerText = `${telemetry.battery_temperature.toFixed(1)}°C`;
    
    // Safe temp range up to 55 degrees
    const tempPct = Math.min(100, (telemetry.battery_temperature / 55) * 100);
    tempFill.style.height = `${tempPct}%`;
    
    if (telemetry.battery_temperature >= 45.0) {
      tempStatusText.innerText = 'Quá nhiệt';
      tempStatusText.style.color = 'var(--color-danger)';
      tempFill.style.background = 'var(--color-danger)';
    } else if (telemetry.battery_temperature >= 40.0) {
      tempStatusText.innerText = 'Nóng';
      tempStatusText.style.color = 'var(--color-warning)';
      tempFill.style.background = 'var(--color-warning)';
    } else {
      tempStatusText.innerText = 'Mát mẻ';
      tempStatusText.style.color = 'var(--color-success)';
      tempFill.style.background = 'linear-gradient(to top, var(--color-primary), var(--color-success))';
    }

    // 4. Network Card
    netTypeBadge.innerText = telemetry.network_type;
    const signalStrength = telemetry.network_strength;
    
    if (signalStrength !== null) {
      netSignalText.innerText = `${signalStrength.toFixed(0)} dBm`;
      
      // Update Signal bars active state
      const bars = [
        document.getElementById('sig-bar-1'),
        document.getElementById('sig-bar-2'),
        document.getElementById('sig-bar-3'),
        document.getElementById('sig-bar-4')
      ];
      
      bars.forEach(b => b.classList.remove('active'));
      
      if (signalStrength > -70) {
        bars[0].classList.add('active');
        bars[1].classList.add('active');
        bars[2].classList.add('active');
        bars[3].classList.add('active');
        netStatusMsg.innerText = 'Tín hiệu tuyệt vời';
      } else if (signalStrength > -85) {
        bars[0].classList.add('active');
        bars[1].classList.add('active');
        bars[2].classList.add('active');
        netStatusMsg.innerText = 'Kết nối ổn định';
      } else if (signalStrength > -100) {
        bars[0].classList.add('active');
        bars[1].classList.add('active');
        netStatusMsg.innerText = 'Tín hiệu trung bình';
      } else {
        bars[0].classList.add('active');
        netStatusMsg.innerText = 'Sóng rất yếu (gây hao pin)';
      }
    } else {
      netSignalText.innerText = '-- dBm';
      netStatusMsg.innerText = 'Không có kết nối mạng';
    }

    // 5. Accelerometer values
    accXText.innerText = telemetry.accel_x.toFixed(2);
    accYText.innerText = telemetry.accel_y.toFixed(2);
    accZText.innerText = telemetry.accel_z.toFixed(2);

    // 6. Update Charts Data
    const timeStr = new Date(telemetry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    // Battery chart update
    if (timeLabels.length === 0 || timeLabels[timeLabels.length - 1] !== timeStr) {
      timeLabels.push(timeStr);
      batteryHistory.push(telemetry.battery_level);
      tempHistory.push(telemetry.battery_temperature);
      
      if (timeLabels.length > maxHistoryPoints) {
        timeLabels.shift();
        batteryHistory.shift();
        tempHistory.shift();
      }
      batteryChart.update();
    }
    
    // Accelerometer chart update (always append for real-time vibe)
    accelLabels.push('');
    accelXHistory.push(telemetry.accel_x);
    accelYHistory.push(telemetry.accel_y);
    accelZHistory.push(telemetry.accel_z);
    
    if (accelLabels.length > 40) {
      accelLabels.shift();
      accelXHistory.shift();
      accelYHistory.shift();
      accelZHistory.shift();
    }
    accelChart.update('none'); // Update without animation for performance

    // 7. Update AI Alerts
    const alerts = stats.recent_alerts || [];
    alertsCountBadge.innerText = `${alerts.length} cảnh báo`;
    
    if (alerts.length === 0) {
      alertsList.innerHTML = `
        <div class="empty-state">
          <i class="fa-solid fa-square-check"></i>
          <p>Hệ thống hoạt động bình thường. Không phát hiện dị thường.</p>
        </div>
      `;
    } else {
      alertsList.innerHTML = alerts.map(a => {
        const time = new Date(a.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const severityClass = a.severity.toLowerCase() === 'critical' ? 'severity-critical' : 'severity-warning';
        const icon = a.anomaly_type === 'FREE_FALL' ? 'fa-person-falling-burst' : 
                     a.anomaly_type === 'SEVERE_SHOCK' ? 'fa-circle-radiation' : 'fa-triangle-exclamation';
                     
        return `
          <div class="alert-item ${severityClass}">
            <div class="alert-icon"><i class="fa-solid ${icon}"></i></div>
            <div class="alert-details">
              <h5>${a.anomaly_type} ${a.resolved ? '<span style="color:var(--color-success); font-size:11px;">(ĐÃ GIẢI QUYẾT)</span>' : ''}</h5>
              <p>${a.description}</p>
            </div>
            <div class="alert-time">${time}</div>
          </div>
        `;
      }).join('');
    }

    // 8. Update Recommendations
    const recs = stats.recent_recommendations || [];
    if (recs.length === 0) {
      recommendationsList.innerHTML = `
        <div class="empty-state">
          <i class="fa-regular fa-lightbulb"></i>
          <p>Đang phân tích thói quen và trạng thái để sinh khuyến nghị...</p>
        </div>
      `;
    } else {
      recommendationsList.innerHTML = recs.map(r => {
        const catClass = r.category.toLowerCase() === 'temperature' ? 'category-temperature' : 
                         r.category.toLowerCase() === 'battery' ? 'category-battery' : 'category-usage';
        const icon = r.category.toLowerCase() === 'temperature' ? 'fa-temperature-arrow-down' : 
                     r.category.toLowerCase() === 'battery' ? 'fa-battery-empty' : 'fa-mobile-screen';
        return `
          <div class="rec-item ${catClass}">
            <div class="rec-icon"><i class="fa-solid ${icon}"></i></div>
            <div class="rec-details">
              <h5>${r.title}</h5>
              <p>${r.content}</p>
            </div>
          </div>
        `;
      }).join('');
    }
  }

  // Fetch initial state via REST API first
  async function fetchInitialStats() {
    try {
      const response = await fetch(`/api/v1/dashboard/${deviceId}`);
      if (response.ok) {
        const data = await response.json();
        updateUI(data);
      }
    } catch (err) {
      console.log('Failed fetching initial API dashboard stats, waiting for WebSocket...');
    }
  }

  // Run init
  initCharts();
  fetchInitialStats();
  connectWebSocket();

  // Allow switching devices (extensible)
  deviceSelector.addEventListener('change', (e) => {
    console.log(`Device switched to: ${e.target.value}`);
    // Clear histories
    timeLabels.length = 0;
    batteryHistory.length = 0;
    tempHistory.length = 0;
    accelLabels.length = 0;
    accelXHistory.length = 0;
    accelYHistory.length = 0;
    accelZHistory.length = 0;
    
    // Request new state via socket
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        action: 'get_device',
        device_id: e.target.value
      }));
    }
  });
});
