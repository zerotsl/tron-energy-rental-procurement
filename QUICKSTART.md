# 🚀 AI 代理支出控制与审计系统 - 快速开始指南

## 📥 第一步：下载项目

### 方法 A：Git 克隆（推荐）
如果你已安装 Git，打开命令行/终端执行：

```bash
git clone https://github.com/zerotsl/tron-energy-rental-procurement.git
cd tron-energy-rental-procurement
git checkout ai-agent-controls
```

### 方法 B：直接下载 ZIP（不需要 Git）
点击以下链接直接下载：

**🔗 [下载 ZIP 包](https://github.com/zerotsl/tron-energy-rental-procurement/archive/refs/heads/ai-agent-controls.zip)**

下载后解压到你的电脑。

---

## ⚙️ 第二步：检查 Python 环境

打开命令行/终端，运行：

```bash
python --version
```

或

```bash
python3 --version
```

需要 **Python 3.9 或更高版本**。如果没有安装，访问：
**🔗 [Python 官网](https://www.python.org/downloads/)**

---

## 📦 第三步：安装依赖

进入项目目录，运行：

```bash
pip install -r requirements.txt
```

这会自动安装：
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `jinja2` - 模板引擎
- `pydantic` - 数据验证
- `python-dotenv` - 环境变量

---

## 🚀 第四步：启动开发服务器

运行以下命令：

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

你会看到：

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

---

## 🌐 第五步：打开浏览器

在浏览器地址栏中输入：

```
http://127.0.0.1:8000
```

或点击这个链接：**[http://localhost:8000](http://127.0.0.1:8000)**

---

## 🎯 第六步：使用系统

系统打开后，你会看到 **4 个标签页**：

### 👔 1. 审批工作台
- **左侧：代理政策配置** - 设置预算、允许供应商、交付期限
- **右侧：当前政策** - 显示当前授权配置
- **下方左：采购需求** - 提交采购请求
- **下方右：代理决策结果** - 查看代理的批准/停止决策

**操作步骤：**
1. 设置预算上限为 $1,800
2. 允许供应商为 `energybridge-nodes`
3. 点击【💾 保存政策】
4. 在下方填写采购需求
5. 点击【🚀 提交给代理评估】
6. 查看代理决策结果

---

### 🎬 2. 停止示例演示
**三个场景自动触发代理停机事件：**

| 场景 | 触发条件 | 预期结果 |
|------|---------|--------|
| 📊 **预算超支** | 总成本 $1,952.45 > 预算 $1,800 | `status: stopped` |
| 🚫 **未授权供应商** | 选中 TronLease Pro（不在白名单） | `status: stopped` |
| ⏰ **交付超期** | 交付 3 天 > 最晚 2 天 | `status: stopped` |

**操作步骤：**
1. 点击任意【▶️ 运行演示】按钮
2. 查看返回结果（状态 + 停机原因）
3. 向下滚动查看【📢 演示结果汇总】

---

### 📋 3. 审计台账
**查看所有代理决策、停机事件、Kiln 调用的完整记录**

- 实时显示时间戳、事件类型、批准 ID、停机原因
- 支持按类型筛选：所有事件 / 停止事件 / 批准事件 / Kiln 调用
- 点击【🔄 刷新】获取最新日志

---

### ⛓️ 4. 链上账本
**查看所有已批准交易的区块链结算记录**

- 显示交易哈希、交易金额、收款地址、供应商名称
- 所有数据都链接到批准 ID
- 点击【🔄 刷新】获取最新交易

---

## 📊 实时查看原始数据

在另一个命令行窗口中（服务保持运行），查看：

### 查看审计日志
```bash
# Windows
type app\data\agent_audit.jsonl

# macOS / Linux
cat app/data/agent_audit.jsonl
```

### 格式化输出（需要 jq）
```bash
cat app/data/agent_audit.jsonl | jq
```

### 查看链上账本
```bash
# Windows
type app\data\testnet_settlements.jsonl

# macOS / Linux
cat app/data/testnet_settlements.jsonl
```

---

## 🔗 API 端点参考

如果你想用 curl 或 Postman 直接调用 API：

### 获取当前政策
```bash
curl http://127.0.0.1:8000/api/agent/policy
```

### 运行演示场景
```bash
curl -X POST http://127.0.0.1:8000/api/agent/demo \
  -H "Content-Type: application/json" \
  -d '{"scenario": "budget_overrun"}'
```

可选的场景：`budget_overrun` / `blocked_supplier` / `deadline_violation`

### 查看审计日志
```bash
curl http://127.0.0.1:8000/api/agent/audit
```

### 查看链上账本
```bash
curl http://127.0.0.1:8000/api/agent/ledger
```

---

## ✅ 验证成功标志

当你看到以下情况，说明系统已成功运行：

- ✓ 页面标题：**"AI 代理支出控制与审计系统"**
- ✓ 顶部状态：**"系统运行中"**（绿色）
- ✓ 4 个标签页正常显示
- ✓ 点击【▶️ 运行演示】后返回 `status="stopped"` + 停机原因
- ✓ 审计日志中显示时间戳 + 事件类型 + 批准 ID
- ✓ 数据文件中生成 JSON 记录

---

## 🛠️ 故障排除

### ❌ ModuleNotFoundError: No module named 'fastapi'
**解决：** 重新运行 `pip install -r requirements.txt`

### ❌ Port 8000 already in use
**解决：** 使用其他端口
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```
然后访问 `http://127.0.0.1:8001`

### ❌ 页面打开但按钮无响应
**原因：** JavaScript 还在加载
**解决：** 刷新页面或检查浏览器控制台是否有错误

### ❌ 查看不到审计日志
**解决：**
1. 确保已运行至少一个演示
2. 刷新页面
3. 检查 `app/data/agent_audit.jsonl` 是否存在

---

## 🎓 深入理解系统

### 架构概览
```
用户界面 (HTML/CSS/JS)
    ↓
FastAPI 后端 (app/main.py)
    ↓
    ├─ 代理政策检查 (agent_controls.py)
    ├─ Kiln LLM 调用 (kiln_client.py)
    ├─ 链上结算 (blockchain.py)
    └─ 审计记录 (audit_store.py)
    ↓
    ├─ app/data/agent_audit.jsonl （审计日志）
    └─ app/data/testnet_settlements.jsonl （链上账本）
```

### 核心概念

**代理政策（Policy）**
- 预算上限：代理不能超支
- 供应商白名单：代理只能选择授权的商户
- 交付期限：代理不能选择交付太慢的商户
- 收款地址：代理只能向授权的地址支付

**停止机制（Stop Mechanism）**
- 一旦代理触发任何边界，立即停机
- 不生成交易哈希
- 在审计日志中记录停机原因
- 硬停无法被人工覆盖

**审计链（Audit Chain）**
- 每个决策都有唯一的批准 ID
- 每个事件都有时间戳
- 所有数据追加到 JSONL 文件（不可覆盖）
- 任何人都可以用批准 ID 追溯整个决策过程

**链上结算（Blockchain Settlement）**
- 只有批准的交易才会生成交易哈希
- 交易哈希与批准 ID 关联
- 所有已批准的交易都记录在链上账本

---

## 📚 文档链接

| 文档 | 链接 |
|------|------|
| **完整项目说明** | [README.md](https://github.com/zerotsl/tron-energy-rental-procurement/blob/ai-agent-controls/README.md) |
| **项目仓库** | [GitHub](https://github.com/zerotsl/tron-energy-rental-procurement) |
| **当前分支** | [ai-agent-controls 分支](https://github.com/zerotsl/tron-energy-rental-procurement/tree/ai-agent-controls) |
| **下载 ZIP** | [ai-agent-controls.zip](https://github.com/zerotsl/tron-energy-rental-procurement/archive/refs/heads/ai-agent-controls.zip) |
| **查看提交** | [最新提交](https://github.com/zerotsl/tron-energy-rental-procurement/commits/ai-agent-controls) |

---

## 🎯 后续步骤

1. **本地测试完成后**，可以将其部署到云服务器（如 AWS、Heroku）
2. **集成真实 Kiln API**，替换演示 fallback
3. **连接真实 Tron 测试网**，生成可验证的交易
4. **添加多层审批流程**，支持初审→财务→CEO 的多级审核
5. **导出审计报告**，支持 PDF/Excel 格式

---

## 💡 常见问题

**Q: 这个系统是否支持真实的区块链交易？**
A: 当前是模拟的。可以配置真实 Tron Nile 测试网，详见 README.md。

**Q: Kiln API 密钥在哪里配置？**
A: 在 `.env` 文件中配置 `KILN_API_URL` 和 `KILN_API_KEY`。没有配置时会使用演示 fallback。

**Q: 如何清空审计日志？**
A: 删除 `app/data/agent_audit.jsonl` 和 `app/data/testnet_settlements.jsonl` 文件，重启服务。

**Q: 是否可以在生产环境运行？**
A: 当前是开发版本。生产环境需要添加认证、数据库、消息队列等。

---

## 🎉 开始测试！

现在你已准备好！执行以下命令：

```bash
# 1. 克隆项目
git clone https://github.com/zerotsl/tron-energy-rental-procurement.git
cd tron-energy-rental-procurement
git checkout ai-agent-controls

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 4. 打开浏览器
# 访问 http://127.0.0.1:8000
```

**祝你测试顺利！🚀**

---

## 📞 支持

如有问题，请查看：
- [项目 README](https://github.com/zerotsl/tron-energy-rental-procurement/blob/ai-agent-controls/README.md)
- [GitHub Issues](https://github.com/zerotsl/tron-energy-rental-procurement/issues)
- [GitHub Discussions](https://github.com/zerotsl/tron-energy-rental-procurement/discussions)
