# JARVIS Desktop AI - Architecture & Implementation Guide

## System Overview

JARVIS is a production-ready desktop AI assistant implementing a **hybrid architecture** that combines:
- **Local processing** for privacy, speed, and reliability
- **Cloud reasoning** for complex multi-step planning and deep understanding

This document provides a complete technical overview of the system.

---

## Architecture Layers

### 1. Input Layer
**Purpose**: Capture user intent from multiple sources

**Components**:
- `input/hotkeys.py` - Global keyboard shortcuts
- `input/audio_capture.py` - Microphone with VAD
- `mcu_bridge/serial_bridge.py` - ESP32 hardware communication

**Data Flow**: 
```
User → [Keyboard/Voice/Button] → Utterance object
```

**Key Features**:
- Voice Activity Detection (WebRTC VAD)
- Debounced hardware buttons
- Async audio processing

---

### 2. Speech-to-Text Layer
**Purpose**: Convert audio to text

**Components**:
- `stt/whisper_local.py` - Local Whisper model

**Models Supported**:
- Whisper tiny/base/small/medium/large
- GPU or CPU inference
- Multi-language support

**Performance**:
- Small model: ~2-3s on CPU, ~0.5s on GPU
- Streaming mode: Future enhancement

---

### 3. NLU & Routing Layer
**Purpose**: Understand intent and route to appropriate handler

**Components**:
- `router/intent_router.py` - Intent classification
- `router/routing_policy.yaml` - Routing rules

**Decision Logic**:
```python
if simple_toolable_task:
    → Local planner
elif needs_deep_reasoning:
    → Cloud planner
elif low_confidence:
    → Cloud fallback
```

**Intent Examples**:
- `open_app` → Local
- `search_files` → Local
- `complex_multi_step_workflow` → Cloud
- `write_email` → Cloud

---

### 4. Agent Layer
**Purpose**: Plan, orchestrate, and verify actions

**Components**:
- `agent/planner_local.py` - Template-based planning
- `agent/planner_cloud.py` - LLM-based planning
- `agent/policy_gate.py` - Permission system
- `agent/orchestrator.py` - Tool execution
- `agent/evaluator.py` - Postcondition verification

**Agent Loop**:
```
ParsedCommand → Planner → ActionPlan → PolicyGate
                                ↓
                           [Approved?]
                                ↓
                           Orchestrator → Tools
                                ↓
                           Evaluator → [Success?]
                                ↓
                      [Retry / Complete / Ask]
```

**Permission Tiers**:
1. **Allow**: Auto-execute (read-only ops)
2. **Ask**: Require confirmation (state-changing)
3. **Deny**: Block by default (dangerous ops)

---

### 5. Tools Layer
**Purpose**: Execute real-world actions

**Components**:
- `tools/os_powershell.py` - Windows OS automation
- `tools/windows_uia.py` - UI Automation (future)
- `tools/playwright_tool.py` - Browser automation
- `tools/pyautogui_fallback.py` - GUI fallback

**Tool Interface**:
```python
async def execute(action_type: str, params: dict) -> ExecutionResult:
    # Tool implementation
    return ExecutionResult(success=True, message="Done")
```

**Tool Categories**:
| Tool | Best For | Reliability |
|------|----------|-------------|
| PowerShell | System ops, file ops | ⭐⭐⭐⭐⭐ |
| UIA | Windows app control | ⭐⭐⭐⭐ |
| Playwright | Web automation | ⭐⭐⭐⭐⭐ |
| PyAutoGUI | GUI fallback | ⭐⭐⭐ |

---

### 6. Memory Layer
**Purpose**: Store and retrieve context

**Components**:
- `memory/embeddings.py` - sentence-transformers
- `memory/vectorstore.py` - Chroma vector DB
- `memory/relational.py` - SQLite metadata
- `memory/memory_policy.py` - What to save

**Memory Types**:
1. **Short-term** (in-memory): Current session context
2. **Long-term** (vector DB): Facts, preferences, notes
3. **Structured** (SQLite): Sessions, actions, audit logs

**RAG Pipeline**:
```
User query → Embedding → Vector search → Top-K results
                                  ↓
                         Inject into LLM prompt
```

---

### 7. Output Layer
**Purpose**: Respond to user

**Components**:
- `tts/tts_local.py` - Coqui TTS or pyttsx3
- `ui/tray_app.py` - System tray status
- `ui/action_preview.py` - Confirmation dialogs

**TTS Engines**:
- **Coqui**: High quality, slower
- **pyttsx3**: Fast, lower quality fallback

---

### 8. MCU Hardware (ESP32)
**Purpose**: Always-on physical interface

**Components**:
- `esp32_firmware/src/main.cpp` - Arduino firmware
- `mcu_bridge/serial_bridge.py` - PC communication

**Features**:
- Wake button (short press)
- Kill switch (long press 3s)
- Status LEDs (16 NeoPixels)
- Heartbeat monitoring
- JSON protocol over serial

---

## Data Schemas

All components communicate using Pydantic models defined in `utils/schemas.py`:

### Core Schema Types

**Utterance** (STT output):
```python
{
    "utterance_id": "uuid",
    "text": "open chrome",
    "stt_confidence": 0.95,
    "source": "microphone",
    ...
}
```

**ParsedCommand** (Router output):
```python
{
    "command_id": "uuid",
    "intent": "open_app",
    "slots": {"app_name": "chrome"},
    "provenance": {"cloud_required": false},
    ...
}
```

**ActionPlan** (Planner output):
```python
{
    "action_id": "uuid",
    "steps": [
        {
            "step_id": "s1",
            "tool": "os_adapter",
            "type": "open_app",
            "params": {"app_name": "chrome"},
            "permission_level": "allow",
            "postconditions": ["process_exists"]
        }
    ],
    ...
}
```

**ExecutionResult** (Tool output):
```python
{
    "success": true,
    "message": "Opened chrome",
    "data": {...},
    "artifacts": []
}
```

---

## Security Architecture

### Defense-in-Depth Layers

1. **Input Validation**: Sanitize all user inputs
2. **Permission Gating**: 3-tier approval system
3. **Tool Sandboxing**: Restrict tool capabilities
4. **Audit Logging**: Immutable action history
5. **Kill Switch**: Emergency stop (keyboard + hardware)
6. **Least Privilege**: Run as normal user

### Audit Trail

Every action logged to `logs/audit.log`:
```json
{
    "log_id": "uuid",
    "timestamp": "ISO-8601",
    "actor": "orchestrator_v1",
    "action": "os_adapter.open_app",
    "input": {"app_name": "chrome"},
    "result": {"success": true}
}
```

---

## Performance Characteristics

### Latency Budget (Typical)

| Stage | Local | Cloud |
|-------|-------|-------|
| Wake detection | 50ms | - |
| Audio capture | 1-3s | - |
| STT (Whisper small) | 2s CPU / 0.5s GPU | - |
| Intent routing | 50ms | - |
| Planning | 100ms | 1-3s |
| Tool execution | 0.5-5s | - |
| TTS | 1-2s | - |
| **Total** | **5-12s** | **7-15s** |

### Resource Usage

**RAM**:
- Base: ~500MB
- Whisper small: +1GB
- Embeddings: +200MB
- Vector DB: ~100MB (10k memories)

**VRAM**:
- Whisper small FP16: ~2GB
- (4GB VRAM is sufficient)

**CPU**:
- Idle: <1%
- Processing: 10-50% (depends on STT)

**Disk**:
- Models: ~2GB
- Vector DB: ~100MB per 10k memories
- Logs: ~10MB per day

---

## Extensibility Points

### Adding New Tools

1. Create `tools/my_tool.py`:
```python
class MyTool:
    async def execute(self, action_type, params):
        # Implement
        return ExecutionResult(success=True)
```

2. Register in `tool_manifest.json`
3. Add permission rules in `policy_gate.py`
4. Update planner templates if needed

### Adding New Intents

1. Add to `routing_policy.yaml`:
```yaml
intent_keywords:
  my_intent:
    - "trigger phrase"
```

2. Update slot extraction in `intent_router.py`
3. Add plan template in `planner_local.py`

### Custom Memory Types

Extend `MemoryNode` schema:
```python
{
    "type": "custom_type",
    "metadata": {"custom_field": "value"}
}
```

Update `memory_policy.py` for save rules.

---

## Testing Strategy

### Unit Tests (Future)
- Test each component in isolation
- Mock external dependencies
- Use pytest fixtures

### Integration Tests (Future)
- End-to-end voice command flow
- Tool execution verification
- Memory persistence

### Manual Testing
```bash
# Test voice input
Ctrl+Space → "Open Chrome" → Verify Chrome opens

# Test memory
"Remember my name is Alex"
"What's my name?"
→ Should recall "Alex"

# Test ESP32
Press button → LED green → Voice capture
```

---

## Deployment

### Development Setup
```bash
python app/main.py  # Run directly
```

### Production Deployment (Future)
- Package with PyInstaller
- Windows service integration
- Auto-start on login
- System tray app always visible

---

## Troubleshooting Guide

### Common Issues

**1. STT is slow**
- Solution: Use smaller model (`tiny` or `base`)
- Enable GPU: `stt.device: "cuda"`

**2. Cloud API errors**
- Check API key in `config.yaml`
- Verify billing/quota
- Test with `curl` to API endpoint

**3. ESP32 disconnects**
- Increase heartbeat interval
- Check USB cable quality
- Add reconnect logic (already implemented)

**4. Permission errors (PowerShell)**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**5. Playwright browser crashes**
```bash
playwright install --force chromium
```

---

## Future Enhancements

### Phase 2
- [ ] OpenWakeWord integration (always-on wake word)
- [ ] Streaming STT (lower latency)
- [ ] Multi-agent planning (AutoGen framework)
- [ ] Vision input (webcam + MediaPipe)

### Phase 3
- [ ] Knowledge graph (Neo4j)
- [ ] Voice biometrics (speaker ID)
- [ ] IoT integration (Home Assistant/MQTT)
- [ ] Mobile companion app

### Phase 4
- [ ] Screen understanding (OCR + element detection)
- [ ] Autonomous workflow learning
- [ ] Multi-device orchestration
- [ ] Enterprise features (SSO, RBAC)

---

## References

### Research Papers
- Whisper: "Robust Speech Recognition via Large-Scale Weak Supervision"
- sentence-transformers: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks"
- ReAct: "Synergizing Reasoning and Acting in Language Models"

### External Libraries
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Playwright](https://playwright.dev/)
- [Chroma](https://www.trychroma.com/)
- [FastLED](https://fastled.io/)

---

## License

MIT License - See `LICENSE` file

---

**Built with ❤️ by the JARVIS community**

*Last updated: 2024*
