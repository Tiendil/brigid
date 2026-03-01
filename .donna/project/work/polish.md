# Polish Workflow

```toml donna
kind = "donna.lib.workflow"
start_operation_id = "run_tests"
```

Polish the repository by running tests, formatting checks, semantic checks, spelling checks, and runtime checks in the required order.

## Run tests

```toml donna
id = "run_tests"
kind = "donna.lib.run_script"
fsm_mode = "start"
save_stdout_to = "tests_output"
goto_on_success = "run_isort_check"
goto_on_failure = "fix_tests"
```

```bash donna script
#!/usr/bin/env bash

set -e

docker compose run --rm brigid poetry run pytest brigid
```

## Fix tests

```toml donna
id = "fix_tests"
kind = "donna.lib.request_action"
```

```
{{ donna.lib.task_variable("tests_output") }}
```

1. Fix test issues reported above.
2. `{{ donna.lib.goto("run_tests") }}`

## Run formatting checks: isort

```toml donna
id = "run_isort_check"
kind = "donna.lib.run_script"
save_stdout_to = "isort_output"
goto_on_success = "run_black_check"
goto_on_failure = "fix_isort_check"
```

```bash donna script
#!/usr/bin/env bash

set -e

docker compose run --rm brigid poetry run isort --check-only .
```

## Fix formatting checks: isort

```toml donna
id = "fix_isort_check"
kind = "donna.lib.request_action"
```

```
{{ donna.lib.task_variable("isort_output") }}
```

1. Fix isort issues reported above.
2. `{{ donna.lib.goto("run_isort_check") }}`

## Run formatting checks: black

```toml donna
id = "run_black_check"
kind = "donna.lib.run_script"
save_stdout_to = "black_output"
goto_on_success = "run_autoflake_check"
goto_on_failure = "fix_black_check"
```

```bash donna script
#!/usr/bin/env bash

set -e

docker compose run --rm brigid poetry run black --check .
```

## Fix formatting checks: black

```toml donna
id = "fix_black_check"
kind = "donna.lib.request_action"
```

```
{{ donna.lib.task_variable("black_output") }}
```

1. Fix black issues reported above.
2. `{{ donna.lib.goto("run_isort_check") }}`

## Run semantic checks: autoflake check

```toml donna
id = "run_autoflake_check"
kind = "donna.lib.run_script"
save_stdout_to = "autoflake_output"
goto_on_success = "run_flake8"
goto_on_failure = "fix_autoflake_check"
```

```bash donna script
#!/usr/bin/env bash

set -e

docker compose run --rm brigid poetry run autoflake --check --quiet .
```

## Fix semantic checks: autoflake check

```toml donna
id = "fix_autoflake_check"
kind = "donna.lib.request_action"
```

```
{{ donna.lib.task_variable("autoflake_output") }}
```

1. Fix autoflake issues reported above.
2. `{{ donna.lib.goto("run_isort_check") }}`

## Run semantic checks: flake8

```toml donna
id = "run_flake8"
kind = "donna.lib.run_script"
save_stdout_to = "flake8_output"
goto_on_success = "run_mypy"
goto_on_failure = "fix_flake8"
```

```bash donna script
#!/usr/bin/env bash

set -e

docker compose run --rm brigid poetry run flake8 .
```

## Fix semantic checks: flake8

```toml donna
id = "fix_flake8"
kind = "donna.lib.request_action"
```

```
{{ donna.lib.task_variable("flake8_output") }}
```

1. Fix flake8 issues reported above.
2. `{{ donna.lib.goto("run_isort_check") }}`

Instructions on fixing special cases:

- `E800 Found commented out code` — remove the commented out code.
- `CCR001 Cognitive complexity is too high` — ignore by adding `# noqa: CCR001` at the end of the line.
- `CCR002 Function "x" has N arguments that exceeds max allowed M` — ignore by adding `# noqa: CCR002` at the end of the line.
- `F821 undefined name` when there are missing imports — add the necessary import statements at the top of the file.
- `F821 undefined name` in all other cases — ask the developer to fix it manually.

## Run semantic checks: mypy

```toml donna
id = "run_mypy"
kind = "donna.lib.run_script"
save_stdout_to = "mypy_output"
goto_on_success = "run_poetry_check"
goto_on_failure = "fix_mypy"
```

```bash donna script
#!/usr/bin/env bash

set -e

docker compose run --rm brigid poetry run mypy --show-traceback .
```

## Fix semantic checks: mypy

```toml donna
id = "fix_mypy"
kind = "donna.lib.request_action"
```

```
{{ donna.lib.task_variable("mypy_output") }}
```

1. Fix mypy issues reported above that you are allowed to fix.
2. Ask the developer to fix any remaining issues manually.
3. `{{ donna.lib.goto("run_isort_check") }}`

Issues you are allowed to fix:

- No type annotation in the code — add type annotations based on the code context.
- Mismatched type annotations that are trivial to fix — fix them.
- Type conversion issues when there are explicit type conversion functions implied in the code — fix them.
- Type conversion issues when the data is received from external sources (like database) and the type is known to be correct.

Instructions on fixing special cases:

- "variable can be None" when None is not allowed — add `assert variable is not None` if that explicitly makes sense from the code flow.

Changes you are not allowed to make:

- Introducing new types.
- Introducing new protocols.
- Adding `type: ignore[import-untyped]`. If you need to use it, ask the developer to install the missing types first or to fix the issue manually.
- Adding or removing attributes to classes. If you need to do it, ask the developer to fix the problem manually.

## Run semantic checks: poetry check

```toml donna
id = "run_poetry_check"
kind = "donna.lib.run_script"
save_stdout_to = "poetry_check_output"
goto_on_success = "run_codespell"
goto_on_failure = "fix_poetry_check"
```

```bash donna script
#!/usr/bin/env bash

set -e

docker compose run --rm brigid poetry check
```

## Fix semantic checks: poetry check

```toml donna
id = "fix_poetry_check"
kind = "donna.lib.request_action"
```

```
{{ donna.lib.task_variable("poetry_check_output") }}
```

1. Fix poetry-check issues reported above.
2. `{{ donna.lib.goto("run_isort_check") }}`

## Run spelling checks: codespell

```toml donna
id = "run_codespell"
kind = "donna.lib.run_script"
save_stdout_to = "codespell_output"
goto_on_success = "run_runtime_build_container"
goto_on_failure = "fix_codespell"
```

```bash donna script
#!/usr/bin/env bash

set -e

docker compose run --rm brigid poetry run codespell --toml pyproject.toml ./brigid ./README.md
```

## Fix spelling checks: codespell

```toml donna
id = "fix_codespell"
kind = "donna.lib.request_action"
```

```
{{ donna.lib.task_variable("codespell_output") }}
```

1. Fix codespell issues reported above.
2. `{{ donna.lib.goto("run_isort_check") }}`

## Build runtime container

```toml donna
id = "run_runtime_build_container"
kind = "donna.lib.run_script"
save_stdout_to = "runtime_build_output"
goto_on_success = "run_runtime_help"
goto_on_failure = "fix_runtime_build_container"
```

```bash donna script
#!/usr/bin/env bash

set -e

docker build -t brigid:check-runnable-in-prod -f ./docker/Dockerfile .
```

## Fix runtime container build

```toml donna
id = "fix_runtime_build_container"
kind = "donna.lib.request_action"
```

```
{{ donna.lib.task_variable("runtime_build_output") }}
```

1. Fix runtime container build issues reported above.
2. `{{ donna.lib.goto("run_isort_check") }}`

## Run runtime checks: help

```toml donna
id = "run_runtime_help"
kind = "donna.lib.run_script"
save_stdout_to = "runtime_help_output"
goto_on_success = "run_runtime_print_configs"
goto_on_failure = "fix_runtime_help"
```

```bash donna script
#!/usr/bin/env bash

set -e

docker run --rm brigid:check-runnable-in-prod brigid --help
```

## Fix runtime checks: help

```toml donna
id = "fix_runtime_help"
kind = "donna.lib.request_action"
```

```
{{ donna.lib.task_variable("runtime_help_output") }}
```

1. Fix runtime help-check issues reported above.
2. `{{ donna.lib.goto("run_isort_check") }}`

## Run runtime checks: print configs

```toml donna
id = "run_runtime_print_configs"
kind = "donna.lib.run_script"
save_stdout_to = "runtime_print_configs_output"
goto_on_success = "finish"
goto_on_failure = "fix_runtime_print_configs"
```

```bash donna script
#!/usr/bin/env bash

set -e

docker run --rm brigid:check-runnable-in-prod brigid print-configs
```

## Fix runtime checks: print configs

```toml donna
id = "fix_runtime_print_configs"
kind = "donna.lib.request_action"
```

```
{{ donna.lib.task_variable("runtime_print_configs_output") }}
```

1. Fix runtime print-configs issues reported above.
2. `{{ donna.lib.goto("run_isort_check") }}`

## Finish

```toml donna
id = "finish"
kind = "donna.lib.finish"
```

Polish workflow completed.
