[doc('All command information')]
default:
    @just --list --unsorted

src_dir_path := "src"
tests_dir_path := "tests"

[doc('Ruff check')]
[group('linter')]
lint:
    uv run ruff check --fix {{ src_dir_path }} {{ tests_dir_path }}

alias l := lint

[doc('Ruff format')]
[group('linter')]
formatter:
    uv run ruff format {{ src_dir_path }} {{ tests_dir_path }}

[doc('Mypy check types')]
[group('linter')]
check-types:
    uv run mypy {{ src_dir_path }} {{ tests_dir_path }}

[doc('Install backend')]
[group('infra')]
install:
    uv sync --frozen --all-groups

alias i := install

[doc('Upgrade packages')]
[group('infra')]
upgrade-packages:
    uv sync --upgrade --all-groups

[doc('Run all tests')]
[group('test')]
test:
    uv run pytest tests/ -v
