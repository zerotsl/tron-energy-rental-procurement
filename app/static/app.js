<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI 支出控制与审计代理</title>
  <link rel="stylesheet" href="/static/styles.css" />
</head>
<body>
  <main class="shell">
    <header class="hero">
      <div>
        <p class="eyebrow">AI SPEND GUARD</p>
        <h1>AI 代理支出控制与审计原型</h1>
        <p class="subtitle">预算，白名单供应商，交付窗口，链上交易和审批记录被捆绑在同一条控制链路中。</p>
      </div>
      <span class="status">Policy enforcement enabled</span>
    </header>

    <section class="grid top-grid">
      <article class="card">
        <h2>采购需求</h2>
        <form id="compare-form">
          <div class="form-grid">
            <label>所需能量<input id="energy_units" type="number" min="1" value="1200000" required /></label>
            <label>租赁时长（天）<input id="rental_days" type="number" min="1" value="30" required /></label>
            <label class="wide">收款地址<input id="receiver_address" minlength="10" value="TQjv4K2x4MVpVZQF1eYdqmYJd1hVGa6KZQ" required /></label>
            <label>预算（USD）<input id="budget_usd" type="number" min="0.01" step="0.01" value="5000" required /></label>
            <label>最晚交付（天）<input id="latest_delivery_days" type="number" min="1" value="7" required /></label>
          </div>
          <button type="submit">获取报价并比较方案</button>
        </form>
      </article>
      <article class="card">
        <h2>已接入报价源</h2>
        <div id="supplier-list"><p class="muted">加载中…</p></div>
      </article>
    </section>

    <section class="card results">
      <div class="section-heading"><h2>方案推荐与费用明细</h2><span id="result-status" class="muted"></span></div>
      <div id="summary-box" class="summary muted">提交需求后显示推荐方案。</div>
      <div id="result-options" class="result-grid"></div>
    </section>

    <section class="card results">
      <div class="section-heading"><h2>AI 代理控制面板</h2><span class="muted">预算与停机策略</span></div>
      <div class="form-grid">
        <label>预算上限（USD）<input id="agent_max_total_spend_usd" type="number" min="1" value="1800" /></label>
        <label>允许供应商ID<input id="agent_allowed_suppliers" type="text" value="energybridge-nodes" /></label>
        <label>最晚交付（天）<input id="agent_max_delivery_days" type="number" min="1" value="3" /></label>
        <label>接收地址前缀<input id="agent_receiver_prefix" type="text" value="TQjv4K2x4MVpVZQF1eYdqmYJd1hVGa6KZQ" /></label>
      </div>
      <div class="button-row">
        <button id="run-budget-demo" type="button">运行预算超支示例</button>
        <button id="run-supplier-demo" type="button">运行未授权商户示例</button>
        <button id="run-deadline-demo" type="button">运行交付超期示例</button>
      </div>
      <div id="agent-output" class="summary muted">未执行任何代理决策。</div>
      <div id="audit-log" class="muted"></div>
    </section>
  </main>
  <script src="/static/app.js"></script>
</body>
</html>
