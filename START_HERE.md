# Start Here — JARVIS Repository

This repository is a **desktop-automation and AI-systems experimentation project**, not a production-ready JARVIS or AGI implementation.

## Fastest path

If you want to understand the project quickly:

1. Read [`README.md`](README.md) for the current scope and evidence standard.
2. Inspect [`simple_voice_assistant.py`](simple_voice_assistant.py) for the smallest concrete automation implementation.
3. Use [`GETTING_STARTED.md`](GETTING_STARTED.md) if you want to experiment with the broader stack.
4. Read [`ARCHITECTURE.md`](ARCHITECTURE.md) as a systems-design exploration, not as proof that every subsystem is fully integrated.
5. Read [`HONEST_README.md`](HONEST_README.md) for the project retrospective and lessons learned.

## Repository layers

### Practical automation

`simple_voice_assistant.py` demonstrates an explicit speech/keyword-to-action workflow for Windows desktop tasks.

### Architecture experiments

The larger application explores routing, planners, tools, memory, dashboards, permissions and MCU integration. Maturity varies across these modules.

### Learning/research notes

The AGI/AI roadmap documents are study material and research directions. They are not product capability claims.

## Evidence rule

When evaluating this repository, distinguish between:

- code that exists;
- code that has automated tests;
- functionality that has been manually demonstrated;
- functionality that has been operated reliably over time.

Future documentation should state which level supports each significant claim.
