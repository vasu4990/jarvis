"""
Action preview dialog for user confirmation
"""

import asyncio
import structlog
import tkinter as tk
from tkinter import ttk
from typing import Optional
from utils.schemas import ActionPlan

logger = structlog.get_logger(__name__)


class ActionPreviewManager:
    """Shows action preview and requests user confirmation"""
    
    def __init__(self, config):
        self.config = config
        self.timeout = config.get("permissions.action_preview_timeout", 15)
        self.response = None
        
    async def show_preview(self, plan: ActionPlan, steps_requiring_confirmation: list) -> bool:
        """
        Show action preview dialog
        
        Returns: True if approved, False if rejected
        """
        logger.info("Showing action preview", steps=len(plan.steps))
        
        # Run dialog in thread
        self.response = None
        
        dialog_thread = threading.Thread(
            target=self._show_dialog_sync,
            args=(plan, steps_requiring_confirmation)
        )
        dialog_thread.start()
        
        # Wait for response with timeout
        start_time = asyncio.get_event_loop().time()
        
        while self.response is None:
            await asyncio.sleep(0.1)
            
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > self.timeout:
                logger.warning("Action preview timed out")
                self._close_dialog()
                return False
                
        return self.response
        
    def _show_dialog_sync(self, plan: ActionPlan, steps_requiring_confirmation: list):
        """Show Tkinter dialog (runs in separate thread)"""
        root = tk.Tk()
        root.title("JARVIS - Action Confirmation")
        root.geometry("500x400")
        root.resizable(False, False)
        
        # Make window always on top
        root.attributes('-topmost', True)
        
        # Header
        header = tk.Label(
            root,
            text="⚠️ JARVIS Action Confirmation",
            font=("Arial", 14, "bold"),
            bg="#FFB800",
            fg="black",
            pady=10
        )
        header.pack(fill=tk.X)
        
        # Info text
        info = tk.Label(
            root,
            text=f"JARVIS wants to perform {len(plan.steps)} action(s).\nPlease review and confirm:",
            font=("Arial", 10),
            pady=10
        )
        info.pack()
        
        # Scrollable step list
        frame = ttk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9),
            height=10
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate steps
        for i, step in enumerate(plan.steps, 1):
            requires_confirm = step.step_id in steps_requiring_confirmation
            marker = "🔒" if requires_confirm else "✓"
            listbox.insert(tk.END, f"{marker} Step {i}: {step.tool}.{step.type}")
            
            # Show params
            if step.params:
                params_str = ", ".join([f"{k}={v}" for k, v in step.params.items()])
                listbox.insert(tk.END, f"   → {params_str}")
                
        # Buttons
        button_frame = tk.Frame(root, pady=10)
        button_frame.pack()
        
        def on_approve():
            self.response = True
            root.destroy()
            
        def on_reject():
            self.response = False
            root.destroy()
            
        approve_btn = tk.Button(
            button_frame,
            text="✓ Approve",
            command=on_approve,
            bg="#50C878",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            height=2
        )
        approve_btn.pack(side=tk.LEFT, padx=10)
        
        reject_btn = tk.Button(
            button_frame,
            text="✗ Reject",
            command=on_reject,
            bg="#D32F2F",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            height=2
        )
        reject_btn.pack(side=tk.LEFT, padx=10)
        
        # Timer label
        timer_label = tk.Label(
            root,
            text=f"Auto-reject in {self.timeout}s",
            font=("Arial", 9),
            fg="gray"
        )
        timer_label.pack(pady=5)
        
        # Store root for potential early close
        self.dialog_root = root
        
        # Run dialog
        root.mainloop()
        
    def _close_dialog(self):
        """Force close dialog"""
        if hasattr(self, 'dialog_root'):
            try:
                self.dialog_root.destroy()
            except:
                pass


import threading
