# pytest-automation

企业级接口自动化测试框架（pytest + requests），基准项目 [testing-online](https://testing.yychuiyan.com)。

## 技术栈

- **Python 3.11** + uv（版本/依赖管理，uv.lock 锁版本）
- **pytest** + pytest-cov（覆盖率）+ pytest-xdist（并行）+ pytest-rerunfailures（失败重跑）
- **requests**（HTTP）+ pydantic（数据校验）+ loguru（日志）+ PyYAML（数据驱动）
- **ruff + mypy + pre-commit**（代码质量卡点）
- **Allure / pytest-html / JUnit**（测试报告）

## 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 配置环境（填 BASE_URL、账号密码）
cp .env.example .env.test
# 编辑 .env.test，填 BASE_URL=https://testing.yychuiyan.com 等

# 3. 跑测试
make test        # 全量测试
make smoke       # 冒烟测试（P0）
```

## 常用命令

```bash
make test          # 全量测试（unit + contract + integration）
make unit          # 单元测试
make contract      # 契约测试（单接口）
make integration   # 集成测试（跨接口流程）
make smoke         # 冒烟（P0，每次提交必跑）
make regression    # 回归（P0+P1）
make lint          # ruff 代码检查
make format        # ruff 格式化
make type          # mypy 类型检查
```

## ⚠️ 批量执行与限流

基准项目 testing-online 是公开练习环境，**写接口（注册 / 新增 / 编辑 / 删除）有服务端限流**：短时间内集中创建用户、商品等会触发 `429 Too Many Requests`。

- 全量 `make test` 一次性跑 100+ 用例时，写操作用例可能集中触发限流。
- 脚本已对写用例做兼容：遇 `429` 会 `pytest.skip`（记为跳过，不判失败），并在 `logs/` 留下 `<-429` 日志。
- **建议**：
  - 日常先跑 `make smoke`（只读为主，几乎不限流），再按需 `make regression`。
  - 若出现 `429 skipped`，等几分钟让限流窗口恢复后重跑即可，无需改脚本。
  - 不要在极短时间内反复执行 `make test`；连续跑会累积触发限流。
  - CI 里如需跑全量，建议在写用例之间加间隔或分批执行。

## 测试覆盖

三层用例组织：

| 层 | 目录 | 测什么 |
| --- | --- | --- |
| unit | `tests/unit/` | 纯函数（断言器/加密/数据生成） |
| contract | `tests/contract/` | 单接口契约（状态码/业务码/schema） |
| integration | `tests/integration/` | 跨接口流程（登录→me→列表） |

```bash
# 接口覆盖率（度量「封装的接口被测试覆盖了多少」）
.venv/bin/python -m pytest --cov=apis --cov=schemas --cov-report=term-missing
```

## 测试报告

跑完测试，报告生成在 `reports/`：

- **Allure**：`reports/allure-results/`（可视化最强）
- **HTML**：`reports/pytest-html/report.html`（单文件，直接开）
- **JUnit**：`reports/junit.xml`（给 Jenkins 吃）

## 目录结构

```
core/      框架核心（配置/日志/HTTP/断言/加密/数据生成）
apis/      接口封装（按业务模块，BaseApi 基类 + 各模块）
schemas/   pydantic 响应模型
tests/     unit / contract / integration 三层用例
data/      测试数据（不提交 git，只提交 *.example 模板）
reports/   报告产物（不提交）
logs/      运行日志（不提交）
```

## 多环境

```bash
APP_ENV=test pytest -m smoke     # 读 .env.test
APP_ENV=prod pytest -m smoke     # 读 .env.prod
```

`.env.{APP_ENV}` 存环境专属配置，`.env.example` 是模板（进 git），真实凭据不进库。

## 代码质量

提交前自动质检（先执行一次 `pre-commit install`）：

- **ruff**：代码检查 + 格式化（含安全规则 S）
- **mypy**：类型检查
- **pip-audit**：依赖漏洞扫描

## CI

- `Dockerfile`：构建测试镜像（依赖提前打进镜像）
- `Jenkinsfile`：流水线（smoke/regression/all 三档）

## 基准项目

[testing-online](https://testing.yychuiyan.com) 是专为自动化测试练习设计的网站，演示账号（公开）：

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | 炊烟1号 | admin123 |
| 普通用户 | 炊烟2号 | user123 |

接口清单见 `docs/6.接口封装与数据模型.md`（约 37 个接口），实战时按「封装 → 契约用例 → make test」的循环逐个覆盖。
