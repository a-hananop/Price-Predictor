'use strict';
/* ── Pakistan Electronics Intelligence — script.js ─────────────────────── */

// ── State ──────────────────────────────────────────────────────────────────
const state = {
  userLat: null,
  userLon: null,
  storeFilter: 'all',
  results: null,
  catalogFilter: 'all',
  allProducts: [],
  allStores: [],
  branches: [],
  leafletMap: null,
  mapMarkers: [],
  userMarker: null,
  mapInitialized: false,
  searchQuery: null,
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
  elements.forEach((el, i) => { el.style.animationDelay = `${i * delayMs}ms`; });
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
    if (view === 'map') {
      setTimeout(() => {
        if (!state.mapInitialized) initLeafletMap();
        else if (state.leafletMap) state.leafletMap.invalidateSize();
      }, 100);
    }
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
      updateUserMarker();
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
    // Re-render results if data exists
    if (state.results) renderResults(state.results);
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
    const query = state.searchQuery || $('inp-search').value.trim() || null;
    const data = await post('/api/optimize', { user_lat: lat, user_lon: lon, category: 'electronics', budget, priority, query });
    state.results = data;
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

  let options = data.all_options || [];

  // Apply store type filter
  if (state.storeFilter !== 'all') {
    options = options.filter(o => o.branch_type === state.storeFilter);
  }

  $('results-count').textContent = `${options.length} store${options.length !== 1 ? 's' : ''}`;
  $('results-title').textContent = `Results — Electronics`;

  const adviceBox = $('advice-box');
  adviceBox.innerHTML = (data.advice || []).map(a => `<p>${a}</p>`).join('');
  if (!data.advice?.length) adviceBox.style.display = 'none';
  else adviceBox.style.display = '';

  const grid = $('cards-grid');
  grid.innerHTML = '';

  if (options.length === 0) {
    grid.innerHTML = '<div class="loading-state"><span style="font-size:2rem">📭</span><p>No stores match the current filter.</p></div>';
  } else {
    options.forEach((opt, i) => {
      const card = buildResultCard(opt, i);
      grid.appendChild(card);
    });
    stagger(grid.querySelectorAll('.result-card'));
  }

  $('results-list').classList.remove('hidden');
  $('empty-state').classList.add('hidden');
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

    <div class="card-actions">
      ${storeType === 'physical' ? `<button class="btn btn-ghost btn-sm btn-view-map" data-lat="${opt.lat}" data-lon="${opt.lon}" data-name="${opt.branch_name}">📍 View on Map</button>` : ''}
      ${opt.branch_url ? `<a href="${opt.branch_url}" target="_blank" class="btn btn-ghost btn-sm">🌐 Website ↗</a>` : ''}
    </div>
  `;

  el.addEventListener('click', (e) => {
    if (e.target.closest('.btn-view-map') || e.target.closest('a')) return;
    openModal(opt);
  });

  // View on Map button
  const mapBtn = el.querySelector('.btn-view-map');
  if (mapBtn) {
    mapBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      flyToStoreOnMap(parseFloat(mapBtn.dataset.lat), parseFloat(mapBtn.dataset.lon), mapBtn.dataset.name);
    });
  }

  return el;
}

// ── Modal ─────────────────────────────────────────────────────────────────
function openModal(opt) {
  const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${opt.lat},${opt.lon}`;

  $('modal-body').innerHTML = `
    <div class="modal-branch-name">${opt.branch_name}</div>
    <div class="modal-address">📍 ${opt.address}</div>
    ${opt.phone ? `<div style="font-size:0.85rem;color:var(--muted);margin-bottom:0.5rem">📞 ${opt.phone}</div>` : ''}
    ${opt.branch_url ? `<a href="${opt.branch_url}" target="_blank" style="font-size:0.82rem;color:var(--accent);text-decoration:none;display:inline-block;margin-bottom:1rem">🌐 ${opt.branch_url} ↗</a>` : ''}

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

    <div class="modal-actions">
      <a href="${directionsUrl}" target="_blank" class="btn btn-primary" style="margin-top:1.25rem;text-decoration:none;font-size:0.85rem">
        🧭 Get Directions in Google Maps
      </a>
    </div>
  `;

  $('modal-backdrop').classList.remove('hidden');
}

$('modal-close').addEventListener('click', () => $('modal-backdrop').classList.add('hidden'));
$('modal-backdrop').addEventListener('click', e => {
  if (e.target === $('modal-backdrop')) $('modal-backdrop').classList.add('hidden');
});
// Escape key closes modal
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && !$('modal-backdrop').classList.contains('hidden')) {
    $('modal-backdrop').classList.add('hidden');
  }
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
        const fuelCost = Math.round(roadDist * 25);
        distanceInfo = `
          <div class="store-distance">
            <span>📏 ~${roadDist} km</span>
            <span>⛽ ~Rs. ${fmt(fuelCost)}</span>
          </div>
        `;
      }

      const viewMapBtn = s.type === 'physical'
        ? `<button class="btn btn-ghost btn-sm btn-view-map" data-lat="${s.lat}" data-lon="${s.lon}" data-name="${s.name}" style="margin-top:8px;font-size:0.75rem">📍 View on Map</button>`
        : '';

      el.innerHTML = `
        <div class="store-header">
          <div class="store-name">${s.name}</div>
          ${typeBadge}
        </div>
        <div class="store-city">📍 ${s.city} — ${s.address}</div>
        ${s.phone ? `<div class="store-phone">📞 ${s.phone}</div>` : ''}
        ${distanceInfo}
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
          ${hasUrl}
          ${viewMapBtn}
        </div>
      `;

      // Wire map button
      const mapBtnEl = el.querySelector('.btn-view-map');
      if (mapBtnEl) {
        mapBtnEl.addEventListener('click', () => {
          flyToStoreOnMap(parseFloat(mapBtnEl.dataset.lat), parseFloat(mapBtnEl.dataset.lon), mapBtnEl.dataset.name);
        });
      }

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

// ── City colors for markers ─────────────────────────────────────────────
const CITY_COLORS = {
  'Karachi': '#ff6b6b',
  'Lahore': '#51cf66',
  'Islamabad': '#339af0',
  'Rawalpindi': '#cc5de8',
  'Multan': '#ffd43b',
  'Online': '#868e96',
};

function getCityColor(city) {
  return CITY_COLORS[city] || '#20c997';
}

function createColoredIcon(color) {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      width:14px;height:14px;border-radius:50%;
      background:${color};
      border:3px solid rgba(255,255,255,0.9);
      box-shadow:0 2px 8px rgba(0,0,0,0.4);
    "></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
    popupAnchor: [0, -12],
  });
}

// ── Leaflet Map ─────────────────────────────────────────────────────────
function initLeafletMap() {
  if (state.mapInitialized) return;

  const map = L.map('leaflet-map', {
    center: [30.3753, 69.3451], // Pakistan center
    zoom: 5,
    zoomControl: true,
    scrollWheelZoom: true,
  });

  // Dark-themed tiles (CartoDB Dark Matter)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> © <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(map);

  state.leafletMap = map;
  state.mapInitialized = true;

  // Add store markers
  addStoreMarkers();

  // Add user marker if location is set
  if (state.userLat && state.userLon) {
    updateUserMarker();
  }
}

function addStoreMarkers() {
  if (!state.leafletMap) return;

  // Clear existing
  state.mapMarkers.forEach(m => state.leafletMap.removeLayer(m));
  state.mapMarkers = [];

  const physicalBranches = state.branches.filter(b => b.type === 'physical');

  physicalBranches.forEach(b => {
    const color = getCityColor(b.city);
    const icon = createColoredIcon(color);

    const popup = L.popup({ className: 'dark-popup' }).setContent(`
      <div class="map-popup-content">
        <div class="popup-name">${b.name}</div>
        <div class="popup-city">📍 ${b.city}</div>
        <div class="popup-address">${b.address}</div>
        ${b.phone ? `<div class="popup-phone">📞 ${b.phone}</div>` : ''}
        ${b.url ? `<a href="${b.url}" target="_blank" class="popup-link">Visit Website ↗</a>` : ''}
        ${state.userLat ? `<div class="popup-distance">📏 ~${(haversineKm(state.userLat, state.userLon, b.lat, b.lon) * 1.3).toFixed(1)} km away</div>` : ''}
      </div>
    `);

    const marker = L.marker([b.lat, b.lon], { icon }).addTo(state.leafletMap).bindPopup(popup);
    marker._storeData = b;
    state.mapMarkers.push(marker);
  });

  // Fit bounds if markers exist
  if (state.mapMarkers.length > 0) {
    const group = L.featureGroup(state.mapMarkers);
    state.leafletMap.fitBounds(group.getBounds().pad(0.1));
  }
}

function updateUserMarker() {
  if (!state.leafletMap || !state.userLat || !state.userLon) return;

  if (state.userMarker) {
    state.leafletMap.removeLayer(state.userMarker);
  }

  const userIcon = L.divIcon({
    className: 'user-marker',
    html: `<div style="
      width:18px;height:18px;border-radius:50%;
      background:#00d4ff;
      border:3px solid #fff;
      box-shadow:0 0 12px rgba(0,212,255,0.6), 0 2px 8px rgba(0,0,0,0.4);
      animation: userPulse 2s ease-in-out infinite;
    "></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -14],
  });

  state.userMarker = L.marker([state.userLat, state.userLon], { icon: userIcon, zIndexOffset: 1000 })
    .addTo(state.leafletMap)
    .bindPopup('<div class="map-popup-content"><div class="popup-name">📍 Your Location</div></div>');

  // Re-add store markers with updated distances
  addStoreMarkers();
}

function flyToStoreOnMap(lat, lon, name) {
  // Switch to map view
  const mapBtn = [...$$('.nav-btn')].find(b => b.dataset.view === 'map');
  if (mapBtn) mapBtn.click();

  setTimeout(() => {
    if (!state.mapInitialized) initLeafletMap();
    state.leafletMap.flyTo([lat, lon], 15, { duration: 1.5 });

    // Open the popup for this marker
    const marker = state.mapMarkers.find(m => {
      const pos = m.getLatLng();
      return Math.abs(pos.lat - lat) < 0.001 && Math.abs(pos.lng - lon) < 0.001;
    });
    if (marker) {
      setTimeout(() => marker.openPopup(), 1600);
    }
  }, 200);
}

// ── Map Legend ──────────────────────────────────────────────────────────
function buildBranchLegend() {
  const list = $('branch-legend-list');
  if (!list) return;
  list.innerHTML = '';

  const branches = state.branches.filter(b => b.type === 'physical');

  if (!branches.length) {
    list.innerHTML = '<p style="font-size:0.75rem;color:var(--muted)">Loading store locations...</p>';
    return;
  }

  // Group by city
  const cities = {};
  branches.forEach(b => {
    if (!cities[b.city]) cities[b.city] = [];
    cities[b.city].push(b);
  });

  Object.entries(cities).forEach(([city, stores]) => {
    const color = getCityColor(city);
    const cityHeader = document.createElement('div');
    cityHeader.className = 'legend-city-header';
    cityHeader.innerHTML = `<div class="legend-dot" style="background:${color}"></div> <strong>${city}</strong> <span style="color:var(--muted);font-size:0.7rem">(${stores.length})</span>`;
    list.appendChild(cityHeader);

    stores.forEach(b => {
      const item = document.createElement('div');
      item.className = 'branch-legend-item';
      item.innerHTML = `
        <div class="legend-dot" style="background:${color}"></div>
        <div>
          <div class="legend-name">${b.name}</div>
          <div class="legend-cats">${b.address}</div>
        </div>
      `;
      item.addEventListener('click', () => {
        flyToStoreOnMap(b.lat, b.lon, b.name);
      });
      list.appendChild(item);
    });
  });
}

// ── Search ──────────────────────────────────────────────────────────────
$('btn-search')?.addEventListener('click', async () => {
  const query = $('inp-search').value.trim();
  if (!query) { toast('Please enter a search term', 'info'); return; }

  const btn = $('btn-search');
  const originalText = btn.innerHTML;
  btn.innerHTML = '<div class="spinner"></div>';
  btn.disabled = true;

  // Save query so optimizer can use it
  state.searchQuery = query;

  try {
    const r = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const data = await r.json();
    if (data.error) throw new Error(data.error);

    state.allProducts = data.products || [];
    state.catalogFilter = 'all';

    toast(`Found ${data.products.length} products for "${query}". Click "Find Best Deal" to optimize!`, 'success');
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

// ── Init ───────────────────────────────────────────────────────────────────
(async function init() {
  // Preload branches for the legend and map
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