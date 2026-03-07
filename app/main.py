"""
JARVIS Desktop AI Assistant - Main Entry Point
Hybrid architecture: Local routing + Cloud reasoning
"""

import asyncio
import sys
import signal
import structlog
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import Config
from utils.logger import setup_logging
from input.hotkeys import HotkeyManager
from input.audio_capture import AudioCapture
from stt.whisper_local import WhisperSTT
from router.intent_router import IntentRouter
from agent.orchestrator import Orchestrator
from agent.policy_gate import PolicyGate
from agent.evaluator import Evaluator
from agent.planner_local import LocalPlanner
from agent.planner_cloud import CloudPlanner
from memory.vectorstore import VectorStore
from memory.relational import RelationalDB
from memory.embeddings import EmbeddingModel
from tts.tts_local import LocalTTS
from mcu_bridge.serial_bridge import SerialBridge
from ui.tray_app import TrayApp
from ui.action_preview import ActionPreviewManager

logger = structlog.get_logger()


class JarvisCore:
    """Main JARVIS application orchestrator"""
    
    def __init__(self, config_path: str = "app/config.yaml"):
        self.config = Config(config_path)
        setup_logging(self.config)
        
        self.logger = structlog.get_logger(__name__)
        self.running = False
        self.session_id = None
        
        # Initialize components
        self._init_components()
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _init_components(self):
        """Initialize all JARVIS components"""
        self.logger.info("Initializing JARVIS components...")
        
        # Memory layer
        self.logger.info("Loading memory systems...")
        self.embedding_model = EmbeddingModel(self.config)
        self.vector_store = VectorStore(self.config, self.embedding_model)
        self.relational_db = RelationalDB(self.config)
        
        # Input layer
        self.logger.info("Setting up input systems...")
        self.audio_capture = AudioCapture(self.config)
        self.hotkey_manager = HotkeyManager(self.config, self.on_hotkey)
        
        # STT
        self.logger.info("Loading speech-to-text model...")
        self.stt = WhisperSTT(self.config)
        
        # Router & NLU
        self.logger.info("Initializing router...")
        self.intent_router = IntentRouter(self.config)
        
        # Agent layer
        self.logger.info("Setting up agent systems...")
        self.policy_gate = PolicyGate(self.config)
        self.evaluator = Evaluator(self.config)
        self.local_planner = LocalPlanner(self.config)
        self.cloud_planner = CloudPlanner(self.config)
        self.orchestrator = Orchestrator(
            self.config,
            self.policy_gate,
            self.evaluator,
            self.relational_db
        )
        
        # TTS
        self.logger.info("Loading text-to-speech...")
        self.tts = LocalTTS(self.config)
        
        # MCU Bridge
        if self.config.get("mcu.enabled"):
            self.logger.info("Connecting to ESP32...")
            self.serial_bridge = SerialBridge(self.config, self.on_mcu_event)
        else:
            self.serial_bridge = None
            
        # UI
        self.logger.info("Starting UI...")
        self.action_preview = ActionPreviewManager(self.config)
        self.tray_app = TrayApp(self.config, self.on_tray_action)
        
        self.logger.info("✓ All components initialized")
        
    async def start(self):
        """Start JARVIS main loop"""
        self.running = True
        self.session_id = self._generate_session_id()
        
        self.logger.info("🤖 JARVIS online", session_id=self.session_id)
        
        # Start subsystems
        tasks = []
        
        # Start hotkey listener
        self.hotkey_manager.start()
        
        # Start MCU bridge
        if self.serial_bridge:
            tasks.append(asyncio.create_task(self.serial_bridge.start()))
            
        # Start tray app (blocking on main thread)
        # Run in executor to not block async loop
        loop = asyncio.get_event_loop()
        tasks.append(loop.run_in_executor(None, self.tray_app.run))
        
        # Keep running
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            self.logger.info("Shutting down...")
            
    async def stop(self):
        """Graceful shutdown"""
        self.logger.info("Stopping JARVIS...")
        self.running = False
        
        # Stop subsystems
        self.hotkey_manager.stop()
        
        if self.serial_bridge:
            await self.serial_bridge.stop()
            
        self.tray_app.stop()
        
        # Save state
        await self._save_session_state()
        
        self.logger.info("✓ JARVIS offline")
        
    async def on_hotkey(self, key_name: str):
        """Handle hotkey events"""
        self.logger.info("Hotkey pressed", key=key_name)
        
        if key_name == "push_to_talk":
            await self.handle_voice_input()
            
        elif key_name == "kill_switch":
            await self.emergency_stop()
            
        elif key_name == "open_console":
            self.show_console()
            
        elif key_name == "mute_toggle":
            self.toggle_mute()
            
    async def on_mcu_event(self, event_type: str, data: dict):
        """Handle ESP32 events"""
        self.logger.info("MCU event", event=event_type, data=data)
        
        if event_type == "WAKE_BUTTON":
            await self.handle_voice_input()
            
        elif event_type == "KILL_SWITCH":
            await self.emergency_stop()
            
        elif event_type == "MUTE_TOGGLE":
            self.toggle_mute()
            
    def on_tray_action(self, action: str):
        """Handle tray menu actions"""
        if action == "exit":
            asyncio.create_task(self.stop())
        elif action == "open_console":
            self.show_console()
        elif action == "settings":
            self.show_settings()
            
    async def handle_voice_input(self):
        """Main voice command pipeline"""
        try:
            # Update status
            self._set_status("listening")
            
            # Capture audio
            self.logger.info("Listening...")
            audio_data = await self.audio_capture.record_until_silence()
            
            if not audio_data:
                self.logger.warning("No speech detected")
                self._set_status("idle")
                return
                
            # Transcribe
            self._set_status("thinking")
            self.logger.info("Transcribing...")
            utterance = await self.stt.transcribe(audio_data)
            
            if not utterance or utterance.text.strip() == "":
                self.logger.warning("Empty transcription")
                self._set_status("idle")
                return
                
            self.logger.info("Heard", text=utterance.text)
            
            # Process command
            await self.process_utterance(utterance)
            
        except Exception as e:
            self.logger.error("Voice input error", error=str(e), exc_info=True)
            await self.tts.speak("Sorry, I encountered an error processing that.")
            self._set_status("error")
            
        finally:
            self._set_status("idle")
            
    async def process_utterance(self, utterance):
        """Process transcribed utterance through full pipeline"""
        
        # Route intent
        parsed_command = await self.intent_router.route(utterance, self.vector_store)
        
        self.logger.info(
            "Intent routed",
            intent=parsed_command.intent,
            confidence=parsed_command.intent_confidence,
            use_cloud=parsed_command.provenance.get("cloud_used", False)
        )
        
        # Check if simple response (no tools)
        if parsed_command.intent == "simple_qa":
            response = await self._handle_simple_qa(parsed_command)
            await self.respond(response)
            return
            
        # Plan actions
        if parsed_command.provenance.get("cloud_required", False):
            # Complex reasoning needed
            action_plan = await self.cloud_planner.plan(parsed_command, self.vector_store)
        else:
            # Simple local planning
            action_plan = await self.local_planner.plan(parsed_command)
            
        if not action_plan or not action_plan.steps:
            await self.respond("I'm not sure how to do that yet.")
            return
            
        # Execute plan
        self._set_status("thinking")
        execution_result = await self.orchestrator.execute(action_plan, self.action_preview)
        
        # Generate response
        response = self._generate_response(execution_result)
        await self.respond(response)
        
        # Update memory if needed
        if execution_result.success and parsed_command.intent == "remember_fact":
            await self._save_to_memory(parsed_command, execution_result)
            
    async def _handle_simple_qa(self, command):
        """Handle simple question-answering"""
        # Try memory retrieval first
        memories = await self.vector_store.query(command.text, top_k=3)
        
        if memories:
            # Found relevant memories
            context = "\n".join([m["text"] for m in memories])
            return f"Based on what I know: {context}"
        
        # Fallback to cloud for general knowledge
        return await self.cloud_planner.simple_answer(command.text)
        
    async def respond(self, text: str):
        """Send response via TTS"""
        self._set_status("speaking")
        await self.tts.speak(text)
        self._set_status("idle")
        
    async def _save_to_memory(self, command, result):
        """Save fact to long-term memory"""
        fact_text = command.slots.get("fact", "")
        if fact_text:
            await self.vector_store.add_memory(
                text=fact_text,
                metadata={
                    "type": "user_fact",
                    "command_id": command.command_id,
                    "timestamp": command.timestamp
                }
            )
            self.logger.info("Saved to memory", text=fact_text)
            
    def _set_status(self, status: str):
        """Update UI and MCU status"""
        # Update tray icon
        self.tray_app.set_status(status)
        
        # Update ESP32 LEDs
        if self.serial_bridge:
            asyncio.create_task(
                self.serial_bridge.send_command("LED", {"state": status.upper()})
            )
            
    async def emergency_stop(self):
        """Kill switch - stop all actions immediately"""
        self.logger.warning("⚠️ EMERGENCY STOP ACTIVATED")
        
        # Cancel all running tools
        await self.orchestrator.cancel_all()
        
        # Stop audio
        self.audio_capture.stop()
        
        # Update status
        self._set_status("error")
        await self.tts.speak("All actions stopped.")
        self._set_status("idle")
        
    def toggle_mute(self):
        """Toggle microphone mute"""
        self.audio_capture.toggle_mute()
        status = "muted" if self.audio_capture.is_muted else "unmuted"
        self.logger.info(f"Audio {status}")
        
    def show_console(self):
        """Open console window"""
        # TODO: implement console UI
        self.logger.info("Console requested (not implemented)")
        
    def show_settings(self):
        """Open settings window"""
        # TODO: implement settings UI
        self.logger.info("Settings requested (not implemented)")
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())
        
    async def _save_session_state(self):
        """Save current session state"""
        # TODO: implement session persistence
        pass
        
    def _signal_handler(self, sig, frame):
        """Handle interrupt signals"""
        self.logger.info("Interrupt received", signal=sig)
        asyncio.create_task(self.stop())
        
    def _generate_response(self, execution_result) -> str:
        """Generate natural language response from execution result"""
        if execution_result.success:
            return execution_result.message or "Done."
        else:
            return f"Sorry, I couldn't complete that. {execution_result.error or ''}"


async def main():
    """Main entry point"""
    try:
        jarvis = JarvisCore()
        await jarvis.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error("Fatal error", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
