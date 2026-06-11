/* ============================================
   WAYNE ENTERPRISES — CEO BOARD REPORT
   Application Logic: Data Processing & Charts
   ============================================ */

// ─── Chart.js Global Defaults ───
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyleWidth = 10;
Chart.defaults.plugins.legend.labels.padding = 16;
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15,22,41,0.95)';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255,255,255,0.1)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.titleFont = { weight: '600', size: 12 };
Chart.defaults.plugins.tooltip.bodyFont = { size: 11 };
Chart.defaults.elements.point.radius = 3;
Chart.defaults.elements.point.hoverRadius = 6;
Chart.defaults.elements.line.tension = 0.35;
Chart.defaults.elements.line.borderWidth = 2;
Chart.defaults.elements.bar.borderRadius = 4;
Chart.defaults.scale.grid = { color: 'rgba(255,255,255,0.04)' };

// ─── Color Palette ───
const COLORS = {
  blue:    '#3b82f6',
  cyan:    '#22d3ee',
  purple:  '#8b5cf6',
  emerald: '#10b981',
  amber:   '#f59e0b',
  rose:    '#f43f5e',
  indigo:  '#6366f1',
  pink:    '#ec4899',
  teal:    '#14b8a6',
  sky:     '#0ea5e9',
};

const alpha = (hex, a) => {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return `rgba(${r},${g},${b},${a})`;
};

// ─── CSV Parser ───
function parseCSV(text) {
  const lines = text.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim());
  return lines.slice(1).map(line => {
    const vals = line.split(',').map(v => v.trim());
    const obj = {};
    headers.forEach((h, i) => {
      const v = vals[i];
      obj[h] = isNaN(v) || v === '' || v === 'N/A' ? v : parseFloat(v);
    });
    return obj;
  });
}

// ─── Data Loading ───
let financialData, securityData, rdData, supplyData, hrData;

async function loadData() {
  const [fin, sec, rd, supply, hr] = await Promise.all([
    fetch('data/wayne_financial_data.csv').then(r => r.text()),
    fetch('data/wayne_security_data.csv').then(r => r.text()),
    fetch('data/wayne_rd_portfolio.csv').then(r => r.text()),
    fetch('data/wayne_supply_chain.csv').then(r => r.text()),
    fetch('data/wayne_hr_analytics.csv').then(r => r.text()),
  ]);
  financialData = parseCSV(fin);
  securityData  = parseCSV(sec);
  rdData        = parseCSV(rd);
  supplyData    = parseCSV(supply);
  hrData        = parseCSV(hr);
}

// ─── Utilities ───
function groupBy(arr, key) {
  return arr.reduce((acc, item) => {
    const k = item[key];
    (acc[k] = acc[k] || []).push(item);
    return acc;
  }, {});
}

function unique(arr, key) {
  return [...new Set(arr.map(d => d[key]))];
}

function sum(arr, key) {
  return arr.reduce((s, d) => s + (d[key] || 0), 0);
}

function avg(arr, key) {
  const valid = arr.filter(d => typeof d[key] === 'number');
  return valid.length ? valid.reduce((s, d) => s + d[key], 0) / valid.length : 0;
}

// ─── Chart Registry ───
const chartInstances = {};

function makeChart(id, config) {
  if (chartInstances[id]) chartInstances[id].destroy();
  const ctx = document.getElementById(id);
  if (!ctx) return null;
  chartInstances[id] = new Chart(ctx, config);
  return chartInstances[id];
}

// ═══════════════════════════════════════════
//  NARRATIVE CHARTS
// ═══════════════════════════════════════════

function renderNarrativeCharts() {
  renderNarrativeRevenue();
  renderNarrativeSecurity();
  renderNarrativeRD();
  renderNarrativeSupply();
  renderNarrativeHR();
  renderNarrativeCross();
}

// 1. Financial — Grouped bar: Revenue by division per quarter
function renderNarrativeRevenue() {
  const divisions = ['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction', 'Wayne Foundation'];
  const colors = [COLORS.blue, COLORS.emerald, COLORS.purple, COLORS.amber, COLORS.rose];
  const byDiv = groupBy(financialData, 'Division');
  const quarters = unique(financialData, 'Quarter').sort();
  // Use only unique quarter-year combos
  const labels = [];
  const seen = new Set();
  financialData.forEach(d => {
    const key = `${d.Quarter} ${d.Year}`;
    if (!seen.has(key)) { seen.add(key); labels.push(key); }
  });

  const datasets = divisions.map((div, i) => {
    const divData = byDiv[div] || [];
    return {
      label: div.replace('Wayne ', ''),
      data: labels.map(label => {
        const [q, y] = label.split(' ');
        const rec = divData.find(d => d.Quarter === q && d.Year === +y);
        return rec ? rec.Revenue_M : 0;
      }),
      backgroundColor: alpha(colors[i], 0.75),
      borderColor: colors[i],
      borderWidth: 1,
    };
  });

  makeChart('chart-narrative-revenue', {
    type: 'bar',
    data: { labels: labels.map(l => l.replace('20', "'")), datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        x: { stacked: false },
        y: { title: { display: true, text: '$M' } }
      }
    }
  });
}

// 2. Security — Line: incidents by district
function renderNarrativeSecurity() {
  const districts = ['Bristol', 'Park Row', 'Downtown', 'Diamond District', 'East End', 'The Narrows'];
  const colors = [COLORS.emerald, COLORS.blue, COLORS.cyan, COLORS.purple, COLORS.amber, COLORS.rose];
  const byDistrict = groupBy(securityData, 'District');
  const dates = unique(securityData, 'Date');

  const datasets = districts.map((dist, i) => ({
    label: dist,
    data: (byDistrict[dist] || []).map(d => d.Security_Incidents),
    borderColor: colors[i],
    backgroundColor: alpha(colors[i], 0.1),
    fill: dist === 'The Narrows',
    pointRadius: 2,
  }));

  makeChart('chart-narrative-security', {
    type: 'line',
    data: { labels: dates.map(d => d.substring(0, 7)), datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        y: { title: { display: true, text: 'Incidents' }, beginAtZero: true }
      }
    }
  });
}

// 3. R&D — Horizontal bar: budget allocated vs spent by division
function renderNarrativeRD() {
  const byDiv = groupBy(rdData, 'Division');
  const divNames = Object.keys(byDiv).sort();
  const labels = divNames.map(d => d.replace('Wayne ', ''));
  const allocated = divNames.map(d => sum(byDiv[d], 'Budget_Allocated_M'));
  const spent = divNames.map(d => sum(byDiv[d], 'Budget_Spent_M'));

  makeChart('chart-narrative-rd', {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Allocated', data: allocated, backgroundColor: alpha(COLORS.purple, 0.5), borderColor: COLORS.purple, borderWidth: 1 },
        { label: 'Spent', data: spent, backgroundColor: alpha(COLORS.cyan, 0.5), borderColor: COLORS.cyan, borderWidth: 1 },
      ]
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        x: { title: { display: true, text: '$M' } }
      }
    }
  });
}

// 4. Supply Chain — Line: production volumes by facility
function renderNarrativeSupply() {
  const facilities = ['Gotham_Main', 'Metropolis_North', 'Central_City', 'Star_City', 'Keystone_City'];
  const colors = [COLORS.blue, COLORS.emerald, COLORS.amber, COLORS.rose, COLORS.purple];
  const byFac = groupBy(supplyData, 'Facility_Location');
  const dates = unique(supplyData, 'Date');

  const datasets = facilities.map((fac, i) => ({
    label: fac.replace('_', ' '),
    data: (byFac[fac] || []).map(d => d.Monthly_Production_Volume),
    borderColor: colors[i],
    backgroundColor: alpha(colors[i], 0.05),
    fill: false,
    pointRadius: 2,
  }));

  makeChart('chart-narrative-supply', {
    type: 'line',
    data: { labels: dates, datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        y: { title: { display: true, text: 'Units' } }
      }
    }
  });
}

// 5. HR — Grouped bar: retention by level (latest period for each dept)
function renderNarrativeHR() {
  const levels = ['Entry Level', 'Mid Level', 'Senior Level', 'Executive'];
  const depts = unique(hrData, 'Department');
  const colors = [COLORS.blue, COLORS.emerald, COLORS.purple];

  // Get latest month for each dept-level combo
  const latest = {};
  hrData.forEach(d => {
    const key = `${d.Department}|${d.Employee_Level}`;
    if (!latest[key] || d.Date > latest[key].Date) latest[key] = d;
  });

  const datasets = depts.map((dept, i) => ({
    label: dept.replace('Wayne ', ''),
    data: levels.map(lev => {
      const rec = latest[`${dept}|${lev}`];
      return rec ? rec.Retention_Rate_Pct : 0;
    }),
    backgroundColor: alpha(colors[i], 0.6),
    borderColor: colors[i],
    borderWidth: 1,
  }));

  makeChart('chart-narrative-hr', {
    type: 'bar',
    data: { labels: levels, datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        y: { min: 85, max: 101, title: { display: true, text: '% Retention' } }
      }
    }
  });
}

// 6. Cross-dataset — Scatter: R&D intensity vs revenue growth
function renderNarrativeCross() {
  const divisions = ['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction'];
  const colors = [COLORS.blue, COLORS.emerald, COLORS.purple, COLORS.amber];

  const points = divisions.map((div, i) => {
    const divFin = financialData.filter(d => d.Division === div);
    const first = divFin.find(d => d.Quarter === 'Q1' && d.Year === 2023);
    const last = divFin.find(d => d.Quarter === 'Q4' && d.Year === 2024);
    const revGrowth = first && last ? ((last.Revenue_M - first.Revenue_M) / first.Revenue_M * 100) : 0;
    const rdIntensity = last ? (last.RD_Investment_M / last.Revenue_M * 100) : 0;
    return { x: rdIntensity, y: revGrowth, label: div.replace('Wayne ', '') };
  });

  makeChart('chart-narrative-cross', {
    type: 'scatter',
    data: {
      datasets: points.map((p, i) => ({
        label: p.label,
        data: [{ x: p.x, y: p.y }],
        backgroundColor: colors[i],
        borderColor: colors[i],
        pointRadius: 10,
        pointHoverRadius: 14,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.dataset.label}: R&D ${ctx.parsed.x.toFixed(1)}%, Growth ${ctx.parsed.y.toFixed(1)}%`
          }
        }
      },
      scales: {
        x: { title: { display: true, text: 'R&D as % of Revenue' }, min: 3, max: 12 },
        y: { title: { display: true, text: 'Revenue Growth (%)' }, min: 40, max: 80 }
      }
    }
  });
}

// ═══════════════════════════════════════════
//  DASHBOARD CHARTS
// ═══════════════════════════════════════════

function renderDashboardCharts() {
  renderDashFinancial();
  renderDashSecurity();
  renderDashRD();
  renderDashSupply();
  renderDashHR();
  renderDashCross();
  renderForecastCharts();
}

// ─── Financial Dashboard ───
function renderDashFinancial() {
  // Revenue Trend
  const divisions = ['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction'];
  const colors = [COLORS.blue, COLORS.emerald, COLORS.purple, COLORS.amber];
  const byDiv = groupBy(financialData, 'Division');
  const labels = [];
  const seen = new Set();
  financialData.forEach(d => {
    const key = `${d.Quarter} ${d.Year}`;
    if (!seen.has(key)) { seen.add(key); labels.push(key); }
  });

  makeChart('dash-fin-revenue-trend', {
    type: 'line',
    data: {
      labels: labels.map(l => l.replace('20', "'")),
      datasets: divisions.map((div, i) => ({
        label: div.replace('Wayne ', ''),
        data: labels.map(l => {
          const [q, y] = l.split(' ');
          const rec = (byDiv[div]||[]).find(d => d.Quarter===q && d.Year===+y);
          return rec ? rec.Revenue_M : 0;
        }),
        borderColor: colors[i],
        backgroundColor: alpha(colors[i], 0.05),
        fill: true,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { title: { display: true, text: 'Revenue ($M)' } } }
    }
  });

  // Profit Margin
  makeChart('dash-fin-profit-margin', {
    type: 'line',
    data: {
      labels: labels.map(l => l.replace('20', "'")),
      datasets: divisions.map((div, i) => ({
        label: div.replace('Wayne ', ''),
        data: labels.map(l => {
          const [q, y] = l.split(' ');
          const rec = (byDiv[div]||[]).find(d => d.Quarter===q && d.Year===+y);
          return rec ? (rec.Net_Profit_M / rec.Revenue_M * 100).toFixed(1) : 0;
        }),
        borderColor: colors[i],
        borderDash: i === 3 ? [5,5] : [],
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { title: { display: true, text: 'Margin (%)' }, min: 15, max: 40 } }
    }
  });

  // Market Share - Doughnut
  const q4_2024 = financialData.filter(d => d.Quarter === 'Q4' && d.Year === 2024 && d.Market_Share_Pct !== 'N/A');
  makeChart('dash-fin-market-share', {
    type: 'doughnut',
    data: {
      labels: q4_2024.map(d => d.Division.replace('Wayne ', '')),
      datasets: [{
        data: q4_2024.map(d => d.Market_Share_Pct),
        backgroundColor: [COLORS.blue, COLORS.emerald, COLORS.purple, COLORS.amber].map(c => alpha(c, 0.7)),
        borderColor: [COLORS.blue, COLORS.emerald, COLORS.purple, COLORS.amber],
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '65%',
      plugins: { legend: { position: 'bottom' } }
    }
  });

  // R&D as % of revenue
  makeChart('dash-fin-rd-pct', {
    type: 'bar',
    data: {
      labels: divisions.map(d => d.replace('Wayne ', '')),
      datasets: [{
        label: 'R&D % of Revenue',
        data: divisions.map(div => {
          const rec = financialData.find(d => d.Division === div && d.Quarter === 'Q4' && d.Year === 2024);
          return rec ? (rec.RD_Investment_M / rec.Revenue_M * 100).toFixed(1) : 0;
        }),
        backgroundColor: [COLORS.blue, COLORS.emerald, COLORS.purple, COLORS.amber].map(c => alpha(c, 0.6)),
        borderColor: [COLORS.blue, COLORS.emerald, COLORS.purple, COLORS.amber],
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { title: { display: true, text: '% of Revenue' } } }
    }
  });

  // Customer satisfaction
  makeChart('dash-fin-csat', {
    type: 'line',
    data: {
      labels: labels.map(l => l.replace('20', "'")),
      datasets: divisions.map((div, i) => ({
        label: div.replace('Wayne ', ''),
        data: labels.map(l => {
          const [q, y] = l.split(' ');
          const rec = (byDiv[div]||[]).find(d => d.Quarter===q && d.Year===+y);
          return rec ? rec.Customer_Satisfaction_Score : 0;
        }),
        borderColor: colors[i],
        pointRadius: 3,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { min: 3.5, max: 5.0, title: { display: true, text: 'Score (out of 5)' } } }
    }
  });
}

// ─── Security Dashboard ───
function renderDashSecurity() {
  const districts = ['Bristol', 'Park Row', 'Downtown', 'Diamond District', 'East End', 'The Narrows'];
  const colors = [COLORS.emerald, COLORS.blue, COLORS.cyan, COLORS.purple, COLORS.amber, COLORS.rose];
  const byDist = groupBy(securityData, 'District');
  const dates = unique(securityData, 'Date');

  // Incidents over time
  makeChart('dash-sec-incidents', {
    type: 'line',
    data: {
      labels: dates.map(d => d.substring(0,7)),
      datasets: districts.map((dist, i) => ({
        label: dist,
        data: (byDist[dist]||[]).map(d => d.Security_Incidents),
        borderColor: colors[i],
        fill: false,
        pointRadius: 2,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { beginAtZero: true, title: { display: true, text: 'Incidents' } } }
    }
  });

  // Response time
  makeChart('dash-sec-response', {
    type: 'line',
    data: {
      labels: dates.map(d => d.substring(0,7)),
      datasets: districts.map((dist, i) => ({
        label: dist,
        data: (byDist[dist]||[]).map(d => d.Response_Time_Minutes),
        borderColor: colors[i],
        fill: false,
        pointRadius: 2,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { title: { display: true, text: 'Minutes' } } }
    }
  });

  // Tech deployments vs crime prevention (scatter)
  const latestSec = {};
  securityData.forEach(d => {
    if (!latestSec[d.District] || d.Date > latestSec[d.District].Date) latestSec[d.District] = d;
  });
  makeChart('dash-sec-tech-crime', {
    type: 'scatter',
    data: {
      datasets: districts.map((dist, i) => {
        const rec = latestSec[dist];
        return {
          label: dist,
          data: [{ x: rec.Wayne_Tech_Deployments, y: rec.Crime_Prevention_Effectiveness_Pct }],
          backgroundColor: colors[i],
          pointRadius: 10,
          pointHoverRadius: 14,
        };
      })
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        x: { title: { display: true, text: 'Wayne Tech Deployments' } },
        y: { title: { display: true, text: 'Crime Prevention (%)' }, min: 60, max: 101 }
      }
    }
  });

  // Safety radar
  makeChart('dash-sec-safety-radar', {
    type: 'radar',
    data: {
      labels: districts,
      datasets: [{
        label: 'Public Safety Score',
        data: districts.map(d => latestSec[d]?.Public_Safety_Score || 0),
        backgroundColor: alpha(COLORS.emerald, 0.15),
        borderColor: COLORS.emerald,
        pointBackgroundColor: COLORS.emerald,
      }, {
        label: 'Employee Safety Index',
        data: districts.map(d => latestSec[d]?.Employee_Safety_Index || 0),
        backgroundColor: alpha(COLORS.blue, 0.15),
        borderColor: COLORS.blue,
        pointBackgroundColor: COLORS.blue,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { r: { min: 5, max: 10.5, ticks: { stepSize: 1 } } }
    }
  });
}

// ─── R&D Dashboard ───
function renderDashRD() {
  const byDiv = groupBy(rdData, 'Division');
  const divNames = Object.keys(byDiv).sort();
  const colors = [COLORS.purple, COLORS.emerald, COLORS.blue, COLORS.amber, COLORS.rose];

  // Budget allocated vs spent
  makeChart('dash-rd-budget', {
    type: 'bar',
    data: {
      labels: divNames.map(d => d.replace('Wayne ', '')),
      datasets: [
        { label: 'Allocated ($M)', data: divNames.map(d => sum(byDiv[d], 'Budget_Allocated_M').toFixed(0)), backgroundColor: colors.map(c => alpha(c, 0.4)), borderColor: colors, borderWidth: 1 },
        { label: 'Spent ($M)', data: divNames.map(d => sum(byDiv[d], 'Budget_Spent_M').toFixed(0)), backgroundColor: colors.map(c => alpha(c, 0.8)), borderColor: colors, borderWidth: 1 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { title: { display: true, text: '$M' } } }
    }
  });

  // Commercialization potential distribution
  const potentials = ['Very High', 'High', 'Medium', 'Low', 'Very Low'];
  const potCounts = potentials.map(p => rdData.filter(d => d.Commercialization_Potential === p).length);
  const potColors = [COLORS.emerald, COLORS.blue, COLORS.amber, COLORS.rose, '#64748b'];
  makeChart('dash-rd-potential', {
    type: 'doughnut',
    data: {
      labels: potentials,
      datasets: [{ data: potCounts, backgroundColor: potColors.map(c => alpha(c, 0.7)), borderColor: potColors, borderWidth: 2 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '60%',
      plugins: { legend: { position: 'bottom' } }
    }
  });

  // Timeline adherence box-style (bar)
  makeChart('dash-rd-timeline', {
    type: 'bar',
    data: {
      labels: divNames.map(d => d.replace('Wayne ', '')),
      datasets: [{
        label: 'Avg Timeline Adherence (%)',
        data: divNames.map(d => avg(byDiv[d], 'Timeline_Adherence_Pct').toFixed(1)),
        backgroundColor: divNames.map((_, i) => {
          const v = avg(byDiv[divNames[i]], 'Timeline_Adherence_Pct');
          return v > 75 ? alpha(COLORS.emerald, 0.6) : v > 50 ? alpha(COLORS.amber, 0.6) : alpha(COLORS.rose, 0.6);
        }),
        borderColor: divNames.map((_, i) => {
          const v = avg(byDiv[divNames[i]], 'Timeline_Adherence_Pct');
          return v > 75 ? COLORS.emerald : v > 50 ? COLORS.amber : COLORS.rose;
        }),
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { min: 0, max: 100, title: { display: true, text: '% Adherence' } } }
    }
  });

  // Patent applications
  makeChart('dash-rd-patents', {
    type: 'bar',
    data: {
      labels: divNames.map(d => d.replace('Wayne ', '')),
      datasets: [{
        label: 'Patent Applications',
        data: divNames.map(d => sum(byDiv[d], 'Patent_Applications')),
        backgroundColor: colors.map(c => alpha(c, 0.6)),
        borderColor: colors,
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { title: { display: true, text: 'Patents' } } }
    }
  });
}

// ─── Supply Chain Dashboard ───
function renderDashSupply() {
  const facilities = ['Gotham_Main', 'Metropolis_North', 'Central_City', 'Star_City', 'Keystone_City'];
  const colors = [COLORS.blue, COLORS.emerald, COLORS.amber, COLORS.rose, COLORS.purple];
  const byFac = groupBy(supplyData, 'Facility_Location');
  const dates = unique(supplyData, 'Date');

  // Quality trend
  makeChart('dash-supply-quality', {
    type: 'line',
    data: {
      labels: dates,
      datasets: facilities.map((fac, i) => ({
        label: fac.replace('_', ' '),
        data: (byFac[fac]||[]).map(d => d.Quality_Score_Pct),
        borderColor: colors[i],
        fill: false,
        pointRadius: 2,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { min: 88, max: 98, title: { display: true, text: 'Quality (%)' } } }
    }
  });

  // Production volume
  makeChart('dash-supply-volume', {
    type: 'line',
    data: {
      labels: dates,
      datasets: facilities.map((fac, i) => ({
        label: fac.replace('_', ' '),
        data: (byFac[fac]||[]).map(d => d.Monthly_Production_Volume),
        borderColor: colors[i],
        backgroundColor: alpha(colors[i], 0.05),
        fill: true,
        pointRadius: 2,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { title: { display: true, text: 'Units' } } }
    }
  });

  // Disruptions (bar)
  makeChart('dash-supply-disruptions', {
    type: 'bar',
    data: {
      labels: facilities.map(f => f.replace('_', ' ')),
      datasets: [{
        label: 'Avg Monthly Disruptions',
        data: facilities.map(f => avg(byFac[f], 'Supply_Chain_Disruptions').toFixed(1)),
        backgroundColor: facilities.map((f, i) => {
          const v = avg(byFac[f], 'Supply_Chain_Disruptions');
          return v > 3 ? alpha(COLORS.rose, 0.6) : v > 2 ? alpha(COLORS.amber, 0.6) : alpha(COLORS.emerald, 0.6);
        }),
        borderWidth: 0,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { title: { display: true, text: 'Avg Disruptions/Month' } } }
    }
  });

  // Inventory turnover
  makeChart('dash-supply-turnover', {
    type: 'bar',
    data: {
      labels: facilities.map(f => f.replace('_', ' ')),
      datasets: [{
        label: 'Avg Inventory Turnover',
        data: facilities.map(f => avg(byFac[f], 'Inventory_Turnover').toFixed(1)),
        backgroundColor: colors.map(c => alpha(c, 0.6)),
        borderColor: colors,
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { title: { display: true, text: 'Turns/Year' } } }
    }
  });

  // Carbon footprint
  makeChart('dash-supply-carbon', {
    type: 'bar',
    data: {
      labels: facilities.map(f => f.replace('_', ' ')),
      datasets: [{
        label: 'Avg Carbon (MT)',
        data: facilities.map(f => avg(byFac[f], 'Carbon_Footprint_MT').toFixed(0)),
        backgroundColor: colors.map(c => alpha(c, 0.6)),
        borderColor: colors,
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { title: { display: true, text: 'Metric Tons' } } }
    }
  });
}

// ─── HR Dashboard ───
function renderDashHR() {
  const levels = ['Entry Level', 'Mid Level', 'Senior Level', 'Executive'];
  const depts = unique(hrData, 'Department');
  const colors = [COLORS.blue, COLORS.emerald, COLORS.purple];
  const dates = [...new Set(hrData.map(d => d.Date))].sort();

  // Retention by level and division (latest)
  const latest = {};
  hrData.forEach(d => {
    const key = `${d.Department}|${d.Employee_Level}`;
    if (!latest[key] || d.Date > latest[key].Date) latest[key] = d;
  });

  makeChart('dash-hr-retention', {
    type: 'bar',
    data: {
      labels: levels,
      datasets: depts.map((dept, i) => ({
        label: dept.replace('Wayne ', ''),
        data: levels.map(lev => latest[`${dept}|${lev}`]?.Retention_Rate_Pct || 0),
        backgroundColor: alpha(colors[i], 0.6),
        borderColor: colors[i],
        borderWidth: 1,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { min: 85, max: 101, title: { display: true, text: '% Retention' } } }
    }
  });

  // Satisfaction trend (entry level across depts)
  const byDept = groupBy(hrData.filter(d => d.Employee_Level === 'Entry Level'), 'Department');
  makeChart('dash-hr-satisfaction', {
    type: 'line',
    data: {
      labels: dates.filter((_, i) => i % 2 === 0).map(d => d.substring(0,7)),
      datasets: depts.map((dept, i) => ({
        label: dept.replace('Wayne ', ''),
        data: (byDept[dept]||[]).filter((_, j) => j % 2 === 0).map(d => d.Employee_Satisfaction_Score),
        borderColor: colors[i],
        fill: false,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { min: 6, max: 10, title: { display: true, text: 'Satisfaction Score' } } }
    }
  });

  // Diversity trend (entry level)
  makeChart('dash-hr-diversity', {
    type: 'line',
    data: {
      labels: dates.filter((_, i) => i % 2 === 0).map(d => d.substring(0,7)),
      datasets: depts.map((dept, i) => ({
        label: dept.replace('Wayne ', ''),
        data: (byDept[dept]||[]).filter((_, j) => j % 2 === 0).map(d => d.Diversity_Index),
        borderColor: colors[i],
        fill: false,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { min: 0.6, max: 1.0, title: { display: true, text: 'Diversity Index' } } }
    }
  });

  // Training vs Performance scatter
  const latestAll = Object.values(latest);
  makeChart('dash-hr-training', {
    type: 'scatter',
    data: {
      datasets: depts.map((dept, i) => ({
        label: dept.replace('Wayne ', ''),
        data: latestAll.filter(d => d.Department === dept).map(d => ({ x: d.Training_Hours_Annual, y: d.Performance_Rating })),
        backgroundColor: colors[i],
        pointRadius: 8,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        x: { title: { display: true, text: 'Training Hours' } },
        y: { title: { display: true, text: 'Performance Rating' } }
      }
    }
  });
}

// ─── Cross-Insights Dashboard ───
function renderDashCross() {
  // R&D investment vs revenue growth
  const divisions = ['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction'];
  const colors = [COLORS.blue, COLORS.emerald, COLORS.purple, COLORS.amber];

  // Per-quarter R&D investment and revenue for each division
  const byDiv = groupBy(financialData, 'Division');
  makeChart('dash-cross-rd-rev', {
    type: 'line',
    data: {
      labels: ['Q1 23', 'Q2 23', 'Q3 23', 'Q4 23', 'Q1 24', 'Q2 24', 'Q3 24', 'Q4 24'],
      datasets: [
        ...divisions.map((div, i) => ({
          label: `${div.replace('Wayne ', '')} Revenue`,
          data: (byDiv[div]||[]).map(d => d.Revenue_M),
          borderColor: colors[i],
          fill: false,
          yAxisID: 'y',
        })),
        ...divisions.map((div, i) => ({
          label: `${div.replace('Wayne ', '')} R&D`,
          data: (byDiv[div]||[]).map(d => d.RD_Investment_M),
          borderColor: colors[i],
          borderDash: [5, 5],
          fill: false,
          yAxisID: 'y1',
          pointRadius: 1,
        }))
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { position: 'left', title: { display: true, text: 'Revenue ($M)' } },
        y1: { position: 'right', title: { display: true, text: 'R&D ($M)' }, grid: { drawOnChartArea: false } }
      }
    }
  });

  // Community engagement vs crime (security data)
  const latestSec = {};
  securityData.forEach(d => {
    if (!latestSec[d.District] || d.Date > latestSec[d.District].Date) latestSec[d.District] = d;
  });
  const districts = Object.keys(latestSec);
  const distColors = [COLORS.cyan, COLORS.blue, COLORS.emerald, COLORS.purple, COLORS.amber, COLORS.rose];
  
  makeChart('dash-cross-community', {
    type: 'scatter',
    data: {
      datasets: districts.map((dist, i) => ({
        label: dist,
        data: [{ x: latestSec[dist].Community_Engagement_Events, y: latestSec[dist].Security_Incidents }],
        backgroundColor: distColors[i],
        pointRadius: 10,
        pointHoverRadius: 14,
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        x: { title: { display: true, text: 'Community Events/Month' } },
        y: { title: { display: true, text: 'Security Incidents' }, beginAtZero: true }
      }
    }
  });

  // Employee satisfaction vs product quality (cross)
  const qualityMap = {
    'Wayne Aerospace': avg(supplyData.filter(d => d.Facility_Location === 'Gotham_Main'), 'Quality_Score_Pct'),
    'Wayne Biotech': avg(supplyData.filter(d => d.Facility_Location === 'Metropolis_North'), 'Quality_Score_Pct'),
    'Wayne Applied Sciences': avg(supplyData.filter(d => d.Facility_Location === 'Central_City'), 'Quality_Score_Pct'),
  };
  
  const depts = ['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences'];
  const deptColors = [COLORS.blue, COLORS.emerald, COLORS.purple];
  
  makeChart('dash-cross-sat-quality', {
    type: 'scatter',
    data: {
      datasets: depts.map((dept, i) => {
        const latestHR = hrData.filter(d => d.Department === dept).sort((a,b) => b.Date.localeCompare(a.Date))[0];
        return {
          label: dept.replace('Wayne ', ''),
          data: [{ x: avg(hrData.filter(d => d.Department === dept), 'Employee_Satisfaction_Score'), y: qualityMap[dept] || 0 }],
          backgroundColor: deptColors[i],
          pointRadius: 12,
          pointHoverRadius: 16,
        };
      })
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        x: { title: { display: true, text: 'Avg Employee Satisfaction' }, min: 7, max: 10 },
        y: { title: { display: true, text: 'Avg Product Quality (%)' }, min: 90, max: 98 }
      }
    }
  });

  // Operational efficiency radar
  makeChart('dash-cross-radar', {
    type: 'radar',
    data: {
      labels: ['Revenue Growth', 'Profit Margin', 'R&D Intensity', 'Customer Satisfaction', 'Employee Retention'],
      datasets: divisions.map((div, i) => {
        const divFin = financialData.filter(d => d.Division === div);
        const first = divFin[0];
        const last = divFin[divFin.length-1];
        const growth = first ? ((last.Revenue_M - first.Revenue_M) / first.Revenue_M * 100) : 0;
        const margin = last ? (last.Net_Profit_M / last.Revenue_M * 100) : 0;
        const rdPct = last ? (last.RD_Investment_M / last.Revenue_M * 100) : 0;
        const csat = last ? last.Customer_Satisfaction_Score * 20 : 0; // scale to 100
        // Get retention from HR
        const deptName = div;
        const hrRec = hrData.filter(d => d.Department === deptName).sort((a,b) => b.Date.localeCompare(a.Date))[0];
        const retention = hrRec ? hrRec.Retention_Rate_Pct : 80;
        return {
          label: div.replace('Wayne ', ''),
          data: [growth, margin, rdPct * 8, csat, retention],
          backgroundColor: alpha(colors[i], 0.1),
          borderColor: colors[i],
          pointBackgroundColor: colors[i],
        };
      })
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { r: { min: 0, max: 100 } }
    }
  });
}

// ─── Forecast Charts ───
function renderForecastCharts() {
  // Revenue forecast
  const divisions = ['Wayne Aerospace', 'Wayne Biotech', 'Wayne Applied Sciences', 'Wayne Construction'];
  const colors = [COLORS.blue, COLORS.emerald, COLORS.purple, COLORS.amber];
  const byDiv = groupBy(financialData, 'Division');
  const historicalLabels = ['Q1 23', 'Q2 23', 'Q3 23', 'Q4 23', 'Q1 24', 'Q2 24', 'Q3 24', 'Q4 24'];
  const forecastLabels = ['Q1 25', 'Q2 25', 'Q3 25', 'Q4 25'];
  const allLabels = [...historicalLabels, ...forecastLabels];

  const datasets = divisions.map((div, i) => {
    const divData = (byDiv[div]||[]).map(d => d.Revenue_M);
    // Simple linear forecast
    const last4 = divData.slice(-4);
    const growthRate = (last4[3] - last4[0]) / last4[0];
    const quarterly = growthRate / 3;
    const forecast = [];
    let base = last4[3];
    for (let q = 0; q < 4; q++) {
      base = base * (1 + quarterly * 0.9);
      forecast.push(Math.round(base * 10) / 10);
    }
    return {
      label: div.replace('Wayne ', ''),
      data: [...divData, ...forecast],
      borderColor: colors[i],
      backgroundColor: alpha(colors[i], 0.05),
      fill: false,
      segment: {
        borderDash: ctx => ctx.p0DataIndex >= 7 ? [6, 4] : [],
      },
      pointRadius: (ctx) => ctx.dataIndex >= 8 ? 5 : 3,
      pointStyle: (ctx) => ctx.dataIndex >= 8 ? 'triangle' : 'circle',
    };
  });

  makeChart('chart-forecast-revenue', {
    type: 'line',
    data: { labels: allLabels, datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' },
        annotation: {}
      },
      scales: { y: { title: { display: true, text: 'Revenue ($M)' } } }
    }
  });

  // Security incident forecast
  const secDistricts = ['Bristol', 'Downtown', 'The Narrows'];
  const secColors = [COLORS.emerald, COLORS.cyan, COLORS.rose];
  const byDist = groupBy(securityData, 'District');
  const secDates = unique(securityData, 'Date').map(d => d.substring(0,7));
  const forecastMonths = ['2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12'];
  const allSecLabels = [...secDates, ...forecastMonths];

  const secDatasets = secDistricts.map((dist, i) => {
    const data = (byDist[dist]||[]).map(d => d.Security_Incidents);
    // Simple trend extrapolation
    const last6 = data.slice(-6);
    const monthlyDecline = (last6[0] - last6[5]) / 6;
    const forecast = [];
    let base = last6[5];
    for (let m = 0; m < 6; m++) {
      base = Math.max(0, base - monthlyDecline * 0.8);
      forecast.push(Math.round(base));
    }
    return {
      label: dist,
      data: [...data, ...forecast],
      borderColor: secColors[i],
      fill: false,
      segment: {
        borderDash: ctx => ctx.p0DataIndex >= data.length - 1 ? [6, 4] : [],
      },
    };
  });

  makeChart('chart-forecast-security', {
    type: 'line',
    data: { labels: allSecLabels, datasets: secDatasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { beginAtZero: true, title: { display: true, text: 'Incidents' } } }
    }
  });
}

// ═══════════════════════════════════════════
//  UI INTERACTIONS
// ═══════════════════════════════════════════

// ─── Navbar scroll effect ───
function initNav() {
  const nav = document.getElementById('main-nav');
  const links = document.querySelectorAll('.nav-links a');
  
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 50);
  });

  // Active link tracking
  const sections = ['narratives', 'dashboards', 'predictions'];
  window.addEventListener('scroll', () => {
    const scrollPos = window.scrollY + 200;
    sections.forEach(id => {
      const el = document.getElementById(id);
      if (el && scrollPos >= el.offsetTop && scrollPos < el.offsetTop + el.offsetHeight) {
        links.forEach(l => l.classList.remove('active'));
        const activeLink = document.querySelector(`.nav-links a[href="#${id}"]`);
        if (activeLink) activeLink.classList.add('active');
      }
    });
  });
}

// ─── Dashboard Tabs ───
function initTabs() {
  const tabs = document.querySelectorAll('.dashboard-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      document.querySelectorAll('.dashboard-panel').forEach(p => p.classList.remove('active'));
      const panel = document.getElementById(tab.dataset.panel);
      if (panel) panel.classList.add('active');
    });
  });
}

// ─── Scroll Reveal ───
function initReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('.reveal, .reveal-stagger, .narrative').forEach(el => {
    observer.observe(el);
  });
}

// ─── KPI Counter Animation ───
function initCounters() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounters();
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  observer.observe(document.getElementById('hero-kpis'));
}

function animateCounters() {
  document.querySelectorAll('.kpi-value[data-target]').forEach(el => {
    const target = parseFloat(el.dataset.target);
    const prefix = el.dataset.prefix || '';
    const suffix = el.dataset.suffix || '';
    const duration = 2000;
    const start = performance.now();

    function step(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 4); // ease-out quart
      const current = (target * eased).toFixed(target % 1 === 0 ? 0 : 1);
      el.textContent = `${prefix}${current}${suffix}`;
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  });
}

// ─── Stat Bar Animation ───
function initStatBars() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.querySelectorAll('.mini-stat-bar-fill').forEach(fill => {
          fill.style.width = fill.dataset.width;
        });
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll('.mini-stat-bar-fill').forEach(el => {
    observer.observe(el.closest('.narrative, .chart-card') || el.parentElement);
  });
}

// ═══════════════════════════════════════════
//  INITIALIZATION
// ═══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {
  initNav();
  initTabs();
  initReveal();
  initCounters();
  initStatBars();

  try {
    await loadData();
    renderNarrativeCharts();
    renderDashboardCharts();
  } catch (e) {
    console.error('Failed to load data:', e);
  }
});
