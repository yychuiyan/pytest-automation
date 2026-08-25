.PHONY: test unit contract integration smoke regression lint format format-check type

test: ## 全量测试
	.venv/bin/python -m pytest -q

unit: ## 单元测试
	.venv/bin/python -m pytest tests/unit/ -q

contract: ## 契约测试（单接口）
	.venv/bin/python -m pytest tests/contract/ -q

integration: ## 集成测试（跨接口流程）
	.venv/bin/python -m pytest tests/integration/ -q

smoke: ## 冒烟（P0，每次提交必跑）
	.venv/bin/python -m pytest -m smoke -q

regression: ## 回归（P0+P1，每日/发版前跑）
	.venv/bin/python -m pytest -m "smoke or regression" -q

lint: ## Ruff 检查
	.venv/bin/ruff check .

format: ## Ruff 格式化
	.venv/bin/ruff format .

format-check: ## 格式检查
	.venv/bin/ruff format --check .

type: ## mypy 类型检查
	.venv/bin/mypy core apis tests
