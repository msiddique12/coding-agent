# Coding Agent CLI

An autonomous coding agent you can run locally against a repo. It uses an LLM to plan actions, then calls tools to inspect files, search code, edit files, run tests, and use git.

The project now includes:
- Autonomous ReAct-style orchestration (`run`)
- Tooling for file search, code search, edits, test runs, shell commands, git status/diff/add/commit
- Deterministic file tools (`read_file`, `replace_in_file`, `append_file`) for precise edits
- Semantic indexer (`index`) for local project indexing
- Multi-provider LLM support (`openai`, `nim`, `huggingface`, `dummy`)
- Config validation (`doctor`)
- Resilient tool loading (optional tools can fail without crashing the agent)

## Quick Start (Clone -> Add API Key -> Run)

1. Clone the repo and enter it

```sh
git clone <your-repo-url>
cd coding-agent
```

2. Create and activate a virtual environment

```sh
python -m venv .venv
source .venv/bin/activate
```

3. Install the project (includes a `coding-agent` command)

```sh
pip install -e .
```

4. Add your API key

```sh
cp .env.example .env
```

Then edit `.env` and set:

```env
OPENAI_API_KEY=your_key_here
```

5. Verify config

```sh
coding-agent doctor --provider openai
```

6. Run the autonomous agent on a goal

```sh
coding-agent run "Inspect this repo and improve the test reliability"
```

Use `--auto-approve` if you want the agent to execute dangerous tools (edit/shell/tests/git) without prompting:

```sh
coding-agent run --auto-approve "Fix failing tests and commit the changes"
```

## Most Useful Commands

```sh
# Autonomous run (alias: ask)
coding-agent run "Add a new CLI subcommand for X"

# Show tool availability (and missing optional dependencies)
coding-agent tools

# Check provider environment variables
coding-agent doctor --provider openai

# Build semantic index
coding-agent index

# Utility commands
coding-agent list-files
coding-agent summarize-readme
coding-agent summarize-file path/to/file.py
```

## Provider Setup

Recommended default:
- `openai` with `OPENAI_API_KEY`

Also supported:
- `nim` with `NIM_API_KEY`
- `huggingface` with `HUGGINGFACE_API_KEY`
- `dummy` for local testing without an API key

You can override the provider per command:

```sh
coding-agent run --provider nim "Refactor the CLI help output"
```

Or set it in `.env`:

```env
LLM_PROVIDER=openai
```

## Notes / Requirements

- `ripgrep` (`rg`) improves/ enables the `code_search` tool. If it is not installed, the agent still runs and marks the tool unavailable.
- Web search requires the Python dependency `duckduckgo-search` (included in the package dependencies).
- The agent logs prompts/responses to `logs/agent.log`.
- The orchestrator now prefers a safer edit loop: inspect with `read_file`, make exact edits with `replace_in_file` / `append_file`, then validate with tests/diff.

## Development

Run tests:

```sh
pytest -q
```

Run without installing the console script:

```sh
python cli.py run "Summarize the architecture of this repo"
```
