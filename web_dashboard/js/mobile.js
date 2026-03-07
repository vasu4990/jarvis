// JARVIS Mobile - JavaScript Controller

class JarvisMobile {
    constructor() {
        this.ws = null;
        this.recognition = null;
        this.isListening = false;
        this.serverAddress = localStorage.getItem('serverAddress') || 'localhost:8765';
        this.settings = {
            voiceLanguage: localStorage.getItem('voiceLanguage') || 'en-US',
            autoSpeak: localStorage.getItem('autoSpeak') !== 'false',
            vibration: localStorage.getItem('vibration') !== 'false'
        };
        
        this.init();
    }
    
    init() {
        this.setupWebSocket();
        this.setupVoiceInput();
        this.setupTextInput();
        this.setupQuickCommands();
        this.setupNavigation();
        this.setupSettings();
        this.setupModal();
    }
    
    // WebSocket Connection
    setupWebSocket() {
        this.connectWebSocket();
    }
    
    connectWebSocket() {
        const wsUrl = `ws://${this.serverAddress}`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('Connected to JARVIS');
                this.updateConnectionStatus(true);
                this.addActivity('Connected to JARVIS', 'fa-check-circle');
                this.vibrate(50);
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };
            
            this.ws.onclose = () => {
                console.log('Disconnected from JARVIS');
                this.updateConnectionStatus(false);
                this.addActivity('Connection lost, retrying...', 'fa-exclamation-circle');
                
                // Auto reconnect
                setTimeout(() => this.connectWebSocket(), 3000);
            };
            
        } catch (error) {
            console.error('Failed to connect:', error);
            this.updateConnectionStatus(false);
            setTimeout(() => this.connectWebSocket(), 3000);
        }
    }
    
    updateConnectionStatus(connected) {
        const status = document.getElementById('connection-status');
        if (connected) {
            status.classList.remove('offline');
        } else {
            status.classList.add('offline');
        }
    }
    
    sendCommand(command) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'command',
                command: command,
                source: 'mobile',
                timestamp: Date.now()
            }));
            return true;
        }
        return false;
    }
    
    handleMessage(data) {
        console.log('Received:', data);
        
        switch (data.type) {
            case 'command_response':
                this.handleCommandResponse(data);
                break;
            case 'activity':
                this.addActivity(data.message, data.icon || 'fa-info-circle');
                break;
            default:
                console.log('Unknown message:', data);
        }
    }
    
    handleCommandResponse(data) {
        this.showResponse(data.response || 'Command executed');
        this.addActivity(data.response || 'Command completed', 'fa-check');
        
        if (this.settings.autoSpeak && 'speechSynthesis' in window) {
            this.speak(data.response);
        }
        
        this.vibrate(100);
    }
    
    // Voice Input
    setupVoiceInput() {
        const voiceButton = document.getElementById('voice-button');
        const voiceStatus = document.getElementById('voice-status');
        
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = this.settings.voiceLanguage;
            
            this.recognition.onstart = () => {
                this.isListening = true;
                voiceButton.classList.add('listening');
                voiceStatus.querySelector('.status-text').textContent = 'Listening...';
                voiceStatus.querySelector('.status-text').classList.add('listening');
                this.vibrate(50);
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                console.log('Voice input:', transcript);
                this.executeCommand(transcript);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.addActivity(`Voice error: ${event.error}`, 'fa-exclamation-triangle');
                this.vibrate([100, 50, 100]);
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                voiceButton.classList.remove('listening');
                voiceStatus.querySelector('.status-text').textContent = 'Tap to speak';
                voiceStatus.querySelector('.status-text').classList.remove('listening');
            };
            
            voiceButton.addEventListener('click', () => {
                if (this.isListening) {
                    this.recognition.stop();
                } else {
                    this.recognition.start();
                }
            });
        } else {
            voiceButton.disabled = true;
            voiceStatus.querySelector('.status-subtext').textContent = 'Voice input not supported';
            console.warn('Speech recognition not supported');
        }
    }
    
    // Text Input
    setupTextInput() {
        const input = document.getElementById('text-input');
        const sendButton = document.getElementById('send-button');
        
        const send = () => {
            const command = input.value.trim();
            if (command) {
                this.executeCommand(command);
                input.value = '';
            }
        };
        
        sendButton.addEventListener('click', send);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                send();
            }
        });
    }
    
    // Execute Command
    executeCommand(command) {
        console.log('Executing command:', command);
        this.addActivity(`You: ${command}`, 'fa-user');
        
        if (this.sendCommand(command)) {
            this.vibrate(30);
            document.getElementById('voice-status').querySelector('.status-text').textContent = 'Processing...';
        } else {
            this.addActivity('Error: Not connected', 'fa-exclamation-circle');
            this.vibrate([100, 50, 100]);
        }
    }
    
    // Quick Commands
    setupQuickCommands() {
        const commandCards = document.querySelectorAll('.command-card');
        
        commandCards.forEach(card => {
            card.addEventListener('click', () => {
                const command = card.dataset.command;
                this.executeCommand(command);
            });
        });
    }
    
    // Activity Feed
    addActivity(text, icon = 'fa-info-circle') {
        const activityList = document.getElementById('activity-list');
        const item = document.createElement('div');
        item.className = 'activity-item';
        item.innerHTML = `
            <i class="fas ${icon}"></i>
            <div class="activity-content">
                <span class="activity-text">${this.escapeHtml(text)}</span>
                <span class="activity-time">Just now</span>
            </div>
        `;
        
        activityList.insertBefore(item, activityList.firstChild);
        
        // Keep only last 20 items
        while (activityList.children.length > 20) {
            activityList.removeChild(activityList.lastChild);
        }
    }
    
    // Clear Activity
    setupNavigation() {
        document.getElementById('clear-activity').addEventListener('click', () => {
            document.getElementById('activity-list').innerHTML = '';
            this.addActivity('Activity cleared', 'fa-trash');
        });
        
        // Bottom navigation
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const view = btn.dataset.view;
                
                // Update active state
                navButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Handle view changes
                if (view === 'dashboard') {
                    window.location.href = 'index.html';
                } else if (view === 'settings') {
                    document.getElementById('settings-panel').classList.add('show');
                }
            });
        });
    }
    
    // Settings
    setupSettings() {
        const settingsPanel = document.getElementById('settings-panel');
        const closeBtn = document.getElementById('close-settings');
        const saveBtn = document.getElementById('save-settings');
        
        // Load saved settings
        document.getElementById('server-address').value = this.serverAddress;
        document.getElementById('voice-language').value = this.settings.voiceLanguage;
        document.getElementById('auto-speak').checked = this.settings.autoSpeak;
        document.getElementById('vibration').checked = this.settings.vibration;
        
        closeBtn.addEventListener('click', () => {
            settingsPanel.classList.remove('show');
        });
        
        saveBtn.addEventListener('click', () => {
            // Save settings
            this.serverAddress = document.getElementById('server-address').value;
            this.settings.voiceLanguage = document.getElementById('voice-language').value;
            this.settings.autoSpeak = document.getElementById('auto-speak').checked;
            this.settings.vibration = document.getElementById('vibration').checked;
            
            // Persist to localStorage
            localStorage.setItem('serverAddress', this.serverAddress);
            localStorage.setItem('voiceLanguage', this.settings.voiceLanguage);
            localStorage.setItem('autoSpeak', this.settings.autoSpeak);
            localStorage.setItem('vibration', this.settings.vibration);
            
            // Update recognition language
            if (this.recognition) {
                this.recognition.lang = this.settings.voiceLanguage;
            }
            
            this.addActivity('Settings saved', 'fa-check');
            this.vibrate(50);
            settingsPanel.classList.remove('show');
            
            // Reconnect with new server address
            if (this.ws) {
                this.ws.close();
            }
            this.connectWebSocket();
        });
    }
    
    // Response Modal
    setupModal() {
        const modal = document.getElementById('response-modal');
        const closeBtn = document.getElementById('close-modal');
        
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('show');
        });
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        });
    }
    
    showResponse(text) {
        const modal = document.getElementById('response-modal');
        const body = document.getElementById('modal-body');
        
        body.innerHTML = `<p>${this.escapeHtml(text)}</p>`;
        modal.classList.add('show');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            modal.classList.remove('show');
        }, 5000);
    }
    
    // Text to Speech
    speak(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = this.settings.voiceLanguage;
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    }
    
    // Vibration
    vibrate(pattern) {
        if (this.settings.vibration && 'vibrate' in navigator) {
            navigator.vibrate(pattern);
        }
    }
    
    // Utility
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.jarvisMobile = new JarvisMobile();
});

// Handle page visibility for reconnection
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.jarvisMobile) {
        // Page became visible, check connection
        if (!window.jarvisMobile.ws || window.jarvisMobile.ws.readyState !== WebSocket.OPEN) {
            window.jarvisMobile.connectWebSocket();
        }
    }
});

// Prevent zoom on double-tap
let lastTouchEnd = 0;
document.addEventListener('touchend', (event) => {
    const now = Date.now();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);
