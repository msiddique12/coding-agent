# CLI Coding Agent

A lightweight, extensible CLI coding agent that uses large language models to analyze and summarize a codebase. The project provides a multi-provider LLM abstraction (NVIDIA NIM and HuggingFace scaffolding), basic CLI commands for quick introspection, and utilities to discover and read project files.

What exists so far: a multi-provider LLM abstraction, the core `CodingAgent` with querying, file-listing and summarization methods, a simple CLI (`ask`, `list-files`, `summarize-readme`, `summarize-file`), filesystem utilities, basic logging, a Dockerfile, and a smoke-test.

Quick start

1. Create a `.env` with necessary API keys (for example, `NIM_API_KEY=`).
2. Run a provider smoke test:

```sh
python tests/test_llm.py
```

Next goals
- Implement agent "tools" (file editor, git, test runner, safe shell) so the agent can apply, validate, and commit changes safely.
- Add semantic search / RAG retrieval (LangChain + local embeddings + Chroma) to enable context-aware queries across large codebases.
- Build automated feature creation: generate diffs from LLM outputs, preview and apply them, and run tests automatically.
- Packaging and UX: add a console entry point so the agent can be installed as a global CLI, and add project-root detection and per-project config.

For more details, see the project source files and tests. Contributions and issues are welcome.