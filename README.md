# JARVIS — Desktop Voice Automation & AI Systems Playground

A Windows-focused experimental repository for exploring **voice-driven desktop automation, tool orchestration, local/cloud AI components, memory systems, web control, and ESP32 integration**.

> **Project status:** research/learning prototype. This repository contains multiple experiments at different maturity levels. It is **not presented as an enterprise-grade assistant, AGI system, or production-ready autonomous agent**.

## Recruiter summary

The most concrete, minimal implementation in this repository is `simple_voice_assistant.py`: a speech/keyword-driven Windows automation utility using speech recognition, text-to-speech, and explicit command mappings.

The larger `app/`, `agent/`, `memory/`, `tools/`, `web_dashboard/`, and MCU directories are architecture experiments that explore how a more capable assistant could be structured. Their presence should not be interpreted as proof that every subsystem is fully integrated, production-tested, or deployed 24/7.

## What this repository demonstrates

- Python desktop automation and subprocess control
- voice input and text-to-speech integration
- intent/command routing experiments
- browser and GUI automation experiments
- SQLite/vector-memory prototypes
- WebSocket/dashboard experiments
- ESP32 integration concepts and firmware experiments
- permission, audit, and tool-orchestration architecture ideas
- extensive documentation exploring system-design trade-offs

## Minimal voice assistant

Install the lightweight dependencies and run:

```bash
pip install -r simple_requirements.txt
python simple_voice_assistant.py
```

The implementation uses explicit command mappings rather than pretending keyword automation is general intelligence.

Example command categories include:

- opening desktop applications
- system/time commands
- volume controls
- simple scripted actions

See [`simple_voice_assistant.py`](simple_voice_assistant.py) for the implementation.

## Larger architecture experiments

The repository also contains a broader modular design:

```text
app/              application entry points
input/            keyboard / microphone input experiments
stt/              speech-to-text integration
router/           intent-routing experiments
agent/            planner / policy / orchestration experiments
tools/            OS, browser and GUI automation tools
memory/           SQLite / vector-memory experiments
tts/              text-to-speech integration
mcu_bridge/       serial communication with microcontrollers
ui/               desktop UI experiments
web_dashboard/    browser/mobile control experiments
esp32_firmware/   ESP32 integration experiments
```

These modules are useful as a **systems-design and integration playground**, but maturity varies by subsystem.

## What is *not* claimed

This repository does **not** claim:

- artificial general intelligence
- human-level reasoning
- autonomous production reliability
- enterprise security certification
- verified 24/7 deployment
- complete hardware validation of every MCU concept
- that all documented architecture paths are integrated simultaneously

## Engineering lessons

The main lesson from this project is that assistant architecture can become complex much faster than the underlying task requires. A small explicit automation tool is often more useful and easier to verify than an oversized "agent" stack.

The repository is therefore intentionally kept as both:

1. a **minimal useful automation implementation**, and
2. a **record of larger architecture experiments and lessons learned**.

## Related documentation

- [`HONEST_README.md`](HONEST_README.md) — retrospective on what is practical vs over-engineered
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — broader system architecture experiment
- [`GETTING_STARTED.md`](GETTING_STARTED.md) — setup notes
- [`AGI_RESEARCH_PATH.md`](AGI_RESEARCH_PATH.md) — long-term learning/research notes, not product claims

## License

MIT — see [`LICENSE`](LICENSE).
