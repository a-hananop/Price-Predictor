'use strict';
/* ── Pakistan Electronics Intelligence — script.js ─────────────────────── */

// ── State ──────────────────────────────────────────────────────────────────
const state = {
  userLat: null,
  userLon: null,
  storeFilter: 'all',    // 'all' | 'physical' | 'online'
  results: null,
  catalogFilter: 'all',
  allProducts: [],
  allStores: [],
  branches: [],
};

// ── Helpers ────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const $$ = sel => document.querySelectorAll(sel);

function toast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span>${type === 'error' ? '⚠' : type === 'success' ? '✓' : 'ℹ'}</span> ${msg}`;
  $('toast-container').appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

function stagger(elements, delayMs = 80) {
  elements.forEach((el, i) => {
    el.style.animationDelay = `${i * delayMs}ms`;
  });
}

function stars(n, total = 5) {
  return Array.from({ length: total }, (_, i) =>
    `<span class="star ${i < n ? 'filled' : ''}">★</span>`
  ).join('');
}

function fmt(n, dec = 0) {
  return Number(n).toLocaleString('en-PK', { minimumFractionDigits: dec, maximumFractionDigits: dec });
}

// ── Navigation ────────────────────────────────────────────────────────────
$$('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const view = btn.dataset.view;
    $$('.nav-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    $$('.view').forEach(v => v.classList.remove('active'));
    const target = $(`view-${view}`);
    target.classList.add('active');

    if (view === 'catalog') loadCatalog();
    if (view === 'stores') loadStoresView();
  });
});

// ── Geolocation ────────────────────────────────────────────────────────────
$('btn-geolocate').addEventListener('click', () => {
  if (!navigator.geolocation) { toast('Geolocation not supported', 'error'); return; }
  $('btn-geolocate').textContent = 'Detecting…';
  navigator.geolocation.getCurrentPosition(
    pos => {
      state.userLat = pos.coords.latitude;
      state.userLon = pos.coords.longitude;
      $('inp-lat').value = fmt(state.userLat, 6);
      $('inp-lon').value = fmt(state.userLon, 6);
      $('btn-geolocate').innerHTML = '<span class="btn-icon">◎</span> Detect My Location';
      toast('Location detected!', 'success');
    },
    err => {
      toast('Could not detect location: ' + err.message, 'error');
      $('btn-geolocate').innerHTML = '<span class="btn-icon">◎</span> Detect My Location';
    },
    { timeout: 10000 }
  );
});

// ── Store filter chips (optimizer) ────────────────────────────────────────
$$('#store-filter-chips .chip').forEach(chip => {
  chip.addEventListener('click', () => {
    $$('#store-filter-chips .chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    state.storeFilter = chip.dataset.filter;
  });
});

// ── Optimizer ────────────────────────────────────────────────────────────
$('btn-optimize').addEventListener('click', async () => {
  const lat = parseFloat($('inp-lat').value);
  const lon = parseFloat($('inp-lon').value);
  const budget = $('inp-budget').value ? parseFloat($('inp-budget').value) : null;
  const priority = document.querySelector('[name="priority"]:checked')?.value || 'total_cost';

  if (isNaN(lat) || isNaN(lon)) { toast('Please enter your latitude and longitude.', 'error'); return; }

  state.userLat = lat;
  state.userLon = lon;

  const btn = $('btn-optimize');
  btn.innerHTML = '<div class="spinner"></div> Optimizing…';
  btn.disabled = true;

  $('empty-state').classList.add('hidden');
  $('results-list').classList.add('hidden');
  $('multi-plan').classList.add('hidden');

  try {
    const data = await post('/api/optimize', { user_lat: lat, user_lon: lon, category: 'electronics', budget, priority });
    renderResults(data);
  } catch (err) {
    toast('Error: ' + err.message, 'error');
    $('empty-state').classList.remove('hidden');
  } finally {
    btn.innerHTML = `<span class="btn-icon">⟳</span> <span id="btn-optimize-label">Find Best Deal</span>`;
    btn.disabled = false;
  }
});

async function post(url, body) {
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || 'Server error');
  return data;
}

// ── Render Results ────────────────────────────────────────────────────────
function renderResults(data) {
  if (data.error) { toast(data.error, 'error'); $('empty-state').classList.remove('hidden'); return; }

  const options = data.all_options || [];
  $('results-count').textContent = `${options.length} store${options.length !== 1 ? 's' : ''}`;
  $('results-title').textContent = `Results — Electronics`;

  const adviceBox = $('advice-box');
  adviceBox.innerHTML = (data.advice || []).map(a => `<p>${a}</p>`).join('');
  if (!data.advice?.length) adviceBox.style.display = 'none';
  else adviceBox.style.display = '';

  const grid = $('cards-grid');
  grid.innerHTML = '';
  options.forEach((opt, i) => {
    const card = buildResultCard(opt, i);
    grid.appendChild(card);
  });

  stagger(grid.querySelectorAll('.result-card'));
  $('results-list').classList.remove('hidden');
  $('empty-state').classList.add('hidden');
  state.results = data;
}

function buildResultCard(opt, rank) {
  const el = document.createElement('div');
  el.className = `result-card${rank === 0 ? ' card-best' : ''}`;

  const rankNum = rank + 1;
  const rankClass = rankNum <= 3 ? `rank-${rankNum}` : 'rank-other';
  const storeType = opt.branch_type || 'physical';
  const typeBadge = storeType === 'online'
    ? '<span class="store-type-badge online">🌐 Online</span>'
    : '<span class="store-type-badge physical">🏬 Physical</span>';

  el.innerHTML = `
    <div class="card-rank ${rankClass}">${rankNum}</div>
    ${rank === 0 ? '<div class="best-badge">★ Best Pick</div>' : ''}
    <div class="card-branch-name">${opt.branch_name} ${typeBadge}</div>
    <div class="card-city">📍 ${opt.city} · ${opt.address}</div>

      <div class="card-product">
      <div class="card-product-name">${opt.product}</div>
      <div class="card-product-price">Rs. ${fmt(opt.product_price)} <span>item price</span></div>
      <div class="card-stars">${stars(opt.product_rating)}</div>
    </div>

    <div class="card-metrics">
      <div class="metric">
        <div class="metric-label">Distance</div>
        <div class="metric-value text-accent">${fmt(opt.distance_km, 1)} km</div>
      </div>
      <div class="metric">
        <div class="metric-label">Drive Time</div>
        <div class="metric-value">${fmt(opt.duration_min, 0)} min</div>
      </div>
      <div class="metric">
        <div class="metric-label">Fuel Cost</div>
        <div class="metric-value text-amber">Rs. ${fmt(opt.fuel_cost)}</div>
      </div>
      <div class="metric">
        <div class="metric-label">Time Cost</div>
        <div class="metric-value text-amber">Rs. ${fmt(opt.time_cost)}</div>
      </div>
    </div>

    <div class="card-total">
      <div>
        <div class="total-label">Grand Total (item + travel)</div>
        <div style="font-size:0.72rem;color:var(--muted)">${opt.via === 'haversine_estimate' ? '~est. road distance' : 'via Google Maps'}</div>
      </div>
      <div class="total-value">Rs. ${fmt(opt.grand_total)}</div>
    </div>
  `;

  el.addEventListener('click', () => openModal(opt));
  return el;
}

// ── Modal ─────────────────────────────────────────────────────────────────
function openModal(opt) {
  $('modal-body').innerHTML = `
    <div class="modal-branch-name">${opt.branch_name}</div>
    <div class="modal-address">📍 ${opt.address}</div>
    ${opt.phone ? `<div style="font-size:0.85rem;color:var(--muted);margin-bottom:1rem">📞 ${opt.phone}</div>` : ''}

    <div class="modal-section-title">Best Product Available</div>
    <div style="background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:14px;">
      <div style="font-size:0.9rem;font-weight:500;margin-bottom:8px">${opt.product}</div>
      <div style="font-family:var(--font-head);font-size:1.5rem;font-weight:800;color:var(--accent)">Rs. ${fmt(opt.product_price)}</div>
      <div class="card-stars" style="margin-top:6px">${stars(opt.product_rating)}</div>
    </div>

    <div class="modal-section-title">Travel & Cost Breakdown</div>
    <div class="modal-cost-grid">
      <div class="modal-cost-item">
        <div class="modal-cost-label">Distance</div>
        <div class="modal-cost-value">${fmt(opt.distance_km, 1)} km</div>
      </div>
      <div class="modal-cost-item">
        <div class="modal-cost-label">Driving Time</div>
        <div class="modal-cost-value">${fmt(opt.duration_min, 0)} min</div>
      </div>
      <div class="modal-cost-item">
        <div class="modal-cost-label">⛽ Fuel Cost</div>
        <div class="modal-cost-value" style="color:var(--amber)">Rs. ${fmt(opt.fuel_cost)}</div>
      </div>
      <div class="modal-cost-item">
        <div class="modal-cost-label">Time Cost</div>
        <div class="modal-cost-value" style="color:var(--amber)">Rs. ${fmt(opt.time_cost)}</div>
      </div>
      <div class="modal-cost-item">
        <div class="modal-cost-label">Item Price</div>
        <div class="modal-cost-value">Rs. ${fmt(opt.product_price)}</div>
      </div>
      <div class="modal-cost-item full total">
        <div class="modal-cost-label">Grand Total (All-In)</div>
        <div class="modal-cost-value">Rs. ${fmt(opt.grand_total)}</div>
      </div>
    </div>
    <div style="margin-top:10px;font-size:0.75rem;color:var(--muted)">
      Distances calculated ${opt.via === 'google_maps' ? 'via Google Maps Roads API' : 'via Haversine (estimated road distance)'}
    </div>
  `;

  $('modal-backdrop').classList.remove('hidden');
}

$('modal-close').addEventListener('click', () => $('modal-backdrop').classList.add('hidden'));
$('modal-backdrop').addEventListener('click', e => {
  if (e.target === $('modal-backdrop')) $('modal-backdrop').classList.add('hidden');
});

// ── Catalog ───────────────────────────────────────────────────────────────
async function loadCatalog(filter) {
  const currentFilter = filter || state.catalogFilter;
  state.catalogFilter = currentFilter;

  const grid = $('catalog-grid');
  grid.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Loading products from 30+ stores…</p></div>';

  try {
    let products;
    if (state.allProducts.length > 0) {
      products = state.allProducts;
    } else {
      const r = await fetch('/api/products/electronics?pages=2');
      const data = await r.json();
      products = data.products || [];
      state.allProducts = products;
    }

    // Filter by store type
    if (currentFilter !== 'all') {
      products = products.filter(p => p.store_type === currentFilter);
    }

    renderCatalogProducts(products);
  } catch (err) {
    grid.innerHTML = `<div class="loading-state" style="color:var(--red)">⚠ ${err.message}</div>`;
  }
}

// Catalog filter chips
$$('.catalog-header .chip[data-filter]').forEach(chip => {
  chip.addEventListener('click', () => {
    $$('.catalog-header .chip[data-filter]').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    loadCatalog(chip.dataset.filter);
  });
});

$('btn-refresh-catalog').addEventListener('click', () => {
  state.allProducts = [];
  loadCatalog();
});

function renderCatalogProducts(prods) {
  const grid = $('catalog-grid');
  grid.innerHTML = '';

  if (!prods || !prods.length) {
    grid.innerHTML = '<div class="loading-state"><span style="font-size:2rem">📭</span><p>No products found.</p></div>';
    return;
  }

  prods.forEach((p, i) => {
    const el = document.createElement('div');
    el.className = 'product-card';
    el.style.animationDelay = `${i * 30}ms`;
    const typeBadge = p.store_type === 'online'
      ? '<span class="store-type-badge online">🌐</span>'
      : '<span class="store-type-badge physical">🏬</span>';
    el.innerHTML = `
      <div class="product-source">${typeBadge} ${p.source_store || 'Unknown'}</div>
      <div class="product-name">${p.product}</div>
      <div class="product-price">Rs. ${fmt(p.price)}</div>
      <div class="product-stars">${stars(p.rating || 4)}</div>
      ${p.description ? `<div class="product-desc">${p.description}</div>` : ''}
      <div style="margin-top:auto; padding-top:10px;">
        <a href="${p.source_url}" target="_blank" class="btn btn-secondary" style="font-size:0.7rem; padding:4px 8px; width:100%; border-radius:6px; text-decoration:none; display:inline-block; text-align:center">View on Store</a>
      </div>
    `;
    grid.appendChild(el);
  });
}

// ── Stores View ──────────────────────────────────────────────────────────
async function loadStoresView(filter = 'all') {
  const grid = $('stores-grid');
  grid.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Loading stores…</p></div>';

  try {
    let stores;
    if (state.allStores.length > 0) {
      stores = state.allStores;
    } else {
      const r = await fetch('/api/stores');
      const data = await r.json();
      stores = data.stores || [];
      state.allStores = stores;
    }

    if (filter !== 'all') {
      stores = stores.filter(s => s.type === filter);
    }

    grid.innerHTML = '';
    stores.forEach((s, i) => {
      const el = document.createElement('div');
      el.className = 'store-card';
      el.style.animationDelay = `${i * 50}ms`;
      const typeBadge = s.type === 'online'
        ? '<span class="store-type-badge online">🌐 Online</span>'
        : '<span class="store-type-badge physical">🏬 Physical</span>';
      const hasUrl = s.url ? `<a href="${s.url}" target="_blank" class="btn btn-secondary" style="font-size:0.75rem; padding:4px 10px; text-decoration:none; display:inline-block; border-radius:6px; margin-top:8px">Visit Website ↗</a>` : '<span style="font-size:0.75rem; color:var(--muted)">No website</span>';

      let distanceInfo = '';
      if (s.type === 'physical' && state.userLat && state.userLon) {
        const dist = haversineKm(state.userLat, state.userLon, s.lat, s.lon);
        const roadDist = (dist * 1.3).toFixed(1);
        const fuelCost = Math.round(roadDist * 25); // Rs 25/km
        distanceInfo = `
          <div class="store-distance">
            <span>📏 ~${roadDist} km</span>
            <span>⛽ ~Rs. ${fmt(fuelCost)}</span>
          </div>
        `;
      }

      el.innerHTML = `
        <div class="store-header">
          <div class="store-name">${s.name}</div>
          ${typeBadge}
        </div>
        <div class="store-city">📍 ${s.city} — ${s.address}</div>
        ${s.phone ? `<div class="store-phone">📞 ${s.phone}</div>` : ''}
        ${distanceInfo}
        ${hasUrl}
      `;
      grid.appendChild(el);
    });
  } catch (err) {
    grid.innerHTML = `<div class="loading-state" style="color:var(--red)">⚠ ${err.message}</div>`;
  }
}

// Store filter chips
$$('[data-sfilter]').forEach(chip => {
  chip.addEventListener('click', () => {
    $$('[data-sfilter]').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    loadStoresView(chip.dataset.sfilter);
  });
});

// ── Haversine (client-side for store distance display) ───────────────────
function haversineKm(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.asin(Math.sqrt(a));
}

// ── Map / Branch Legend ──────────────────────────────────────────────────
function buildBranchLegend() {
  const list = $('branch-legend-list');
  if (!list) return;
  list.innerHTML = '';

  const branches = state.branches.length > 0 ? state.branches.filter(b => b.type === 'physical') : [];

  if (!branches.length) {
    list.innerHTML = '<p style="font-size:0.75rem;color:var(--muted)">Loading store locations...</p>';
    return;
  }

  branches.forEach((b, i) => {
    const item = document.createElement('div');
    item.className = 'branch-legend-item';
    item.innerHTML = `
      <div class="legend-dot" style="background:hsl(${(i * 25) % 360},80%,60%)"></div>
      <div>
        <div class="legend-name">${b.name}</div>
        <div class="legend-cats">${b.city}</div>
      </div>
    `;
    list.appendChild(item);
  });
}

window.initMap = function (realApi = true) {
  console.log('Map initialized via Google Embed.');
};

// ── Search ──────────────────────────────────────────────────────────────
$('btn-search')?.addEventListener('click', async () => {
  const query = $('inp-search').value.trim();
  if (!query) { toast('Please enter a search term', 'info'); return; }

  const btn = $('btn-search');
  const originalText = btn.innerHTML;
  btn.innerHTML = '<div class="spinner"></div>';
  btn.disabled = true;

  try {
    const r = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const data = await r.json();
    if (data.error) throw new Error(data.error);

    state.allProducts = data.products || [];
    state.catalogFilter = 'all';

    // Switch to catalog view
    const catalogBtn = [...$$('.nav-btn')].find(b => b.dataset.view === 'catalog');
    if (catalogBtn) {
      catalogBtn.click();
    }

    toast(`Found ${data.products.length} products for "${query}"`, 'success');
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
});

// Enter key search
$('inp-search')?.addEventListener('keydown', e => {
  if (e.key === 'Enter') $('btn-search')?.click();
});

// ── Sub-category hints ───────────────────────────────────────────────────
$$('.hint-tag').forEach(tag => {
  tag.addEventListener('click', () => {
    $('inp-search').value = tag.dataset.q;
    $('btn-search').click();
  });
});

// ── Utility ────────────────────────────────────────────────────────────────
function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// ── Init ───────────────────────────────────────────────────────────────────
(async function init() {
  // Preload branches for the legend
  try {
    const r = await fetch('/api/branches');
    const d = await r.json();
    state.branches = d.branches || [];
    buildBranchLegend();
  } catch (_) { }

  // Demo: Karachi
  $('inp-lat').value = '24.8607';
  $('inp-lon').value = '67.0011';
  state.userLat = 24.8607;
  state.userLon = 67.0011;
})();