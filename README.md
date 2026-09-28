const form = document.getElementById('compare-form');
const supplierList = document.getElementById('supplier-list');
const summaryBox = document.getElementById('summary-box');
const resultOptions = document.getElementById('result-options');

function renderSuppliers(list) {
  supplierList.innerHTML = list
    .map(
      (supplier) => `
        <article class="supplier-card">
          <h3>${supplier.supplier_name}</h3>
          <div class="meta">
            <div>Source: ${supplier.source_name}</div>
            <div>Unit price: $${supplier.rate_per_unit_per_day.toFixed(8)} / unit / day</div>
            <div>Min order: ${supplier.min_order_units.toLocaleString()} units</div>
            <div>Capacity: ${supplier.available_energy_units.toLocaleString()} units</div>
            <div>Rental period: ${supplier.rental_period_days} days</div>
            <div>Delivery: ${supplier.estimated_delivery_days} days</div>
            <div>URL: ${supplier.source_url}</div>
          </div>
        </article>
      `
    )
    .join('');
}

function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function renderResults(res) {
  const { selected_plan, options, notes } = res;

  if (!options || options.length === 0) {
    summaryBox.innerHTML = `<strong>No feasible plan</strong><br />${res.selected_plan?.reason || 'No available supplier satisfies the request.'}`;
    resultOptions.innerHTML = '';
    return;
  }

  const selected = selected_plan || options[0];
  summaryBox.innerHTML = `
    <strong>Recommended plan:</strong> ${selected.plan_type === 'split_order' ? 'Split-order procurement' : 'Single-supplier procurement'}<br />
    <strong>Total cost:</strong> ${formatCurrency(selected.total_cost_usd)}<br />
    <strong>Suppliers:</strong> ${(selected.supplier_names || []).join(', ') || 'N/A'}<br />
    <strong>Delivery estimate:</strong> ${selected.estimated_delivery_days ?? 'N/A'} days
  `;

  const cards = options
    .slice(0, 4)
    .map((option) => {
      const isSelected = option.total_cost_usd === selected.total_cost_usd && option.type === selected.plan_type;
      const supplierNames = option.type === 'split_order'
        ? option.suppliers.map((item) => item.supplier_name).join(' + ')
        : option.supplier_name;

      return `
        <article class="result-card">
          <h3>${option.type === 'split_order' ? 'Split-order plan' : 'Single-supplier plan'} ${isSelected ? '<span class="badge-success">Recommended</span>' : ''}</h3>
          <p><strong>Suppliers:</strong> ${supplierNames}</p>
          <div class="cost-line"><span>Rental fee</span><strong>${formatCurrency(option.cost_breakdown?.rental_fee ?? 0)}</strong></div>
          <div class="cost-line"><span>Service fee</span><strong>${formatCurrency(option.cost_breakdown?.service_fee ?? 0)}</strong></div>
          <div class="cost-line"><span>Chain fee</span><strong>${formatCurrency(option.cost_breakdown?.chain_fee ?? 0)}</strong></div>
          <div class="cost-line"><span>Other costs</span><strong>${formatCurrency(option.cost_breakdown?.other_costs ?? 0)}</strong></div>
          <div class="cost-line"><span>Total</span><strong>${formatCurrency(option.total_cost_usd)}</strong></div>
          <p class="meta">Delivery: ${option.estimated_delivery_days ?? 'N/A'} days</p>
        </article>
      `;
    })
    .join('');

  resultOptions.innerHTML = cards + notes
    .map((note) => `<p class="meta">• ${note}</p>`)
    .join('');
}

function loadSuppliers() {
  fetch('/api/suppliers')
    .then((response) => response.json())
    .then((data) => renderSuppliers(data))
    .catch(() => {
      supplierList.innerHTML = '<p class="meta">Unable to load supplier catalog.</p>';
    });
}

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const payload = {
    energy_units: Number(document.getElementById('energy_units').value),
    rental_days: Number(document.getElementById('rental_days').value),
    receiver_address: document.getElementById('receiver_address').value,
    budget_usd: Number(document.getElementById('budget_usd').value),
    latest_delivery_days: Number(document.getElementById('latest_delivery_days').value),
    currency: 'USD',
  };

  fetch('/api/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((data) => renderResults(data))
    .catch((error) => {
      summaryBox.innerHTML = 'Error while comparing supplier plans.';
      console.error(error);
    });
});

loadSuppliers();
fetch('/api/compare', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    energy_units: 1200000,
    rental_days: 30,
    receiver_address: 'TQjv4K2x4MVpVZQF1eYdqmYJd1hVGa6KZQ',
    budget_usd: 5000,
    latest_delivery_days: 7,
    currency: 'USD',
  }),
})
  .then((response) => response.json())
  .then((data) => renderResults(data))
  .catch((error) => console.error(error));
