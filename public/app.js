const byId = (id) => document.getElementById(id);

function renderChart(values) {
  const chart = byId('traffic-chart');
  chart.replaceChildren();
  const max = Math.max(...values);
  values.forEach((value, index) => {
    const bar = document.createElement('span');
    bar.style.height = `${Math.max(12, (value / max) * 100)}%`;
    bar.style.animationDelay = `${index * 35}ms`;
    bar.setAttribute('aria-label', `${value} thousand requests`);
    chart.appendChild(bar);
  });
}

function renderServices(services) {
  const list = byId('service-list');
  list.replaceChildren();
  services.forEach((service) => {
    const row = document.createElement('article');
    row.innerHTML = `
      <div class="service-name"><span class="service-icon">${service.name.slice(0, 1)}</span><strong>${service.name}</strong></div>
      <span class="service-latency">${service.latency}</span>
      <span class="service-status"><i></i>${service.status}</span>
    `;
    list.appendChild(row);
  });
}

async function loadDashboard() {
  try {
    const response = await fetch('/api/metrics');
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    const data = await response.json();

    Object.entries(data.summary).forEach(([key, value]) => {
      const target = byId(key);
      if (target) target.textContent = value;
    });
    renderChart(data.traffic);
    renderServices(data.services);
    byId('last-updated').textContent = `Updated ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  } catch (error) {
    byId('last-updated').textContent = 'Unable to load live data';
    byId('service-list').innerHTML = `<p class="error">${error.message}</p>`;
  }
}

loadDashboard();
