const $ = (id) => document.getElementById(id);
const money = (value) => new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'USD' }).format(value || 0);
const units = (value) => Number(value || 0).toLocaleString('en-US');

function renderSuppliers(suppliers) {
  $('supplier-list').innerHTML = suppliers.map((s) => `
    <div class="supplier">
      <div class="supplier-title"><strong>${s.supplier_name}</strong><span>${s.estimated_delivery_days} 天交付</span></div>
      <div class="muted">来源：${s.source_name}</div>
      <div class="supplier-facts">${s.rate_per_unit_per_day.toFixed(8)} USD / 能量 / 天 · 最小 ${units(s.min_order_units)} · 可用 ${units(s.available_energy_units)} · 周期 ${s.rental_period_days} 天</div>
      <a href="${s.source_url}" target="_blank" rel="noreferrer">查看报价来源</a>
    </div>`).join('');
}

function renderBreakdown(breakdown) {
  return Object.entries({
    '租赁费': breakdown.rental_fee,
    '服务费': breakdown.service_fee,
    '链上手续费': breakdown.chain_fee,
    '其他成本': breakdown.other_costs,
    '总计': breakdown.total,
  }).map(([label, value]) => `<div class="cost-line"><span>${label}</span><strong>${money(value)}</strong></div>`).join('');
}

function renderResults(data) {
  const selected = data.selected_plan || {};
  if (!data.options?.length) {
    $('summary-box').innerHTML = `<strong>无可行方案</strong><br>${selected.reason || '没有供应商同时满足能量、租期、交付或最小下单量约束。'}`;
    $('result-options').innerHTML = '';
    return;
  }
  $('summary-box').innerHTML = `<strong>推荐：${selected.plan_type === 'split_order' ? '多供应商拆单' : '单供应商采购'}</strong><br>供应商：${(selected.supplier_names || []).join(' + ')}<br>总成本：<strong>${money(selected.total_cost_usd)}</strong> · 预计交付：${selected.estimated_delivery_days} 天<br><span class="muted">推荐理由：在已接入且满足约束的方案中，总成本最低；计算范围与费用公式见下方说明。</span>`;
  $('result-options').innerHTML = data.options.map((option, index) => {
    const names = option.type === 'split_order' ? option.suppliers.map((s) => `${s.supplier_name}（${units(s.allocated_energy_units)}）`).join(' + ') : option.supplier_name;
    return `<article class="option ${index === 0 ? 'recommended' : ''}"><h3>${index === 0 ? '推荐方案 · ' : ''}${option.type === 'split_order' ? '拆单采购' : '单供应商采购'}</h3><p>${names}</p>${renderBreakdown(option.cost_breakdown)}<div class="muted">交付 ${option.estimated_delivery_days} 天 · ${option.source_name || '多来源组合'}</div></article>`;
  }).join('');
  $('result-options').insertAdjacentHTML('beforeend', `<div class="notes muted"><strong>计算说明</strong><br>${data.notes.map((note) => `• ${note}`).join('<br>')}</div>`);
}

$('compare-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  $('result-status').textContent = '正在查询…';
  const payload = {
    energy_units: Number($('energy_units').value),
    rental_days: Number($('rental_days').value),
    receiver_address: $('receiver_address').value.trim(),
    budget_usd: Number($('budget_usd').value),
    latest_delivery_days: Number($('latest_delivery_days').value),
    currency: 'USD',
  };
  try {
    const response = await fetch('/api/compare', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    renderResults(await response.json());
    $('result-status').textContent = '查询完成';
  } catch (error) {
    $('summary-box').textContent = `查询失败：${error.message}`;
    $('result-status').textContent = '失败';
  }
});

fetch('/api/suppliers').then((r) => r.json()).then(renderSuppliers).catch(() => { $('supplier-list').innerHTML = '<p class="muted">报价源加载失败。</p>'; });
