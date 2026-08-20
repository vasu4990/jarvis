# JARVIS Documentation Index

Use this index to navigate the repository by **purpose and evidence level**, rather than by feature count.

## Start here

| Document | Purpose |
|---|---|
| [`README.md`](README.md) | current project scope, evidence standard and recruiter summary |
| [`START_HERE.md`](START_HERE.md) | shortest path through the repository |
| [`GETTING_STARTED.md`](GETTING_STARTED.md) | setup and experimentation notes |
| [`HONEST_README.md`](HONEST_README.md) | project retrospective and architecture lessons |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | broader modular assistant design experiment |

## Practical implementation

- [`simple_voice_assistant.py`](simple_voice_assistant.py) — minimal explicit voice-command automation.
- [`simple_requirements.txt`](simple_requirements.txt) — lightweight dependencies for that path.

## Broader systems experiments

- `app/` — application entry points.
- `input/` and `stt/` — input and speech-recognition experiments.
- `router/` and `agent/` — routing/planning/orchestration experiments.
- `tools/` — OS/browser/GUI automation utilities.
- `memory/` — persistence and retrieval experiments.
- `ui/` and `web_dashboard/` — desktop/web interface experiments.
- `mcu_bridge/`, `esp32_firmware/`, `esp32_firmware_advanced/` — MCU integration experiments.

## Setup and deployment notes

- [`SETUP_GUIDE.md`](SETUP_GUIDE.md)
- [`DEPLOYMENT.md`](DEPLOYMENT.md)
- [`config.example.yaml`](config.example.yaml)
- [`requirements.txt`](requirements.txt)

Deployment documentation describes possible setup paths; it should not be interpreted as proof of a long-running production deployment unless evidence is added.

## AI/ML research notes

- [`AGI_RESEARCH_PATH.md`](AGI_RESEARCH_PATH.md)
- [`AGI_IMPLEMENTATION_ROADMAP.md`](AGI_IMPLEMENTATION_ROADMAP.md)
- [`AGI_STARTER_KIT.md`](AGI_STARTER_KIT.md)

These are learning and research materials, not claims that the repository implements AGI.

## Hardware notes

- [`MCU_VERSIONS_GUIDE.md`](MCU_VERSIONS_GUIDE.md)
- [`MCU_JARVIS_ADVANCED.md`](MCU_JARVIS_ADVANCED.md)
- `esp32_firmware/`
- `esp32_firmware_advanced/`

Treat component lists and architecture suggestions as reference material until backed by a specific assembled-hardware revision and validation evidence.
