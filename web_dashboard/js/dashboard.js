// JARVIS Dashboard - Main JavaScript

class JarvisDashboard {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.isListening = false;
        this.recognition = null;
        
        this.init();
    }
    
    init() {
        this.setupNavigation();
        this.setupWebSocket();
        this.setupCommandInterface();
        this.setupQuickActions();
        this.setupVoiceInput();
        this.startUptime();
        this.simulateActivity(); // For demo purposes
    }
    
    // Navigation
    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        const pages = document.querySelectorAll('.page');
        
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const targetPage = item.dataset.page;
                
                // Update active nav item
                navItems.forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
                
                // Show target page
                pages.forEach(page => page.classList.remove('active'));
                document.getElementById(`${targetPage}-page`).classList.add('active');
            });
        });
        
        // Settings button
        document.getElementById('settings-btn').addEventListener('click', () => {
            this.showToast('Settings panel coming soon!', 'info');
        });
        
        // Fullscreen button
        document.getElementById('fullscreen-btn').addEventListener('click', () => {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        });
    }
    
    // WebSocket Connection
    setupWebSocket() {
        this.connectWebSocket();
    }
    
    connectWebSocket() {
        const wsUrl = 'ws://localhost:8765'; // JARVIS WebSocket server
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('Connected to JARVIS backend');
                this.updateConnectionStatus('online');
                this.reconnectAttempts = 0;
                this.showToast('Connected to JARVIS', 'success');
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('error');
            };
            
            this.ws.onclose = () => {
                console.log('Disconnected from JARVIS backend');
                this.updateConnectionStatus('offline');
                this.attemptReconnect();
            };
            
        } catch (error) {
            console.error('Failed to connect:', error);
            this.updateConnectionStatus('offline');
            this.attemptReconnect();
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            this.showToast(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`, 'warning');
            
            setTimeout(() => {
                this.connectWebSocket();
            }, this.reconnectDelay);
        } else {
            this.showToast('Failed to connect. Please check if JARVIS backend is running.', 'error');
        }
    }
    
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('system-status');
        const indicator = statusElement.querySelector('.status-indicator');
        const text = statusElement.querySelector('span');
        
        indicator.classList.remove('offline');
        
        switch (status) {
            case 'online':
                text.textContent = 'Online';
                indicator.style.color = 'var(--success-color)';
                break;
            case 'offline':
                text.textContent = 'Offline';
                indicator.classList.add('offline');
                indicator.style.color = 'var(--danger-color)';
                break;
            case 'error':
                text.textContent = 'Error';
                indicator.style.color = 'var(--warning-color)';
                break;
        }
    }
    
    handleWebSocketMessage(data) {
        console.log('Received:', data);
        
        switch (data.type) {
            case 'activity':
                this.addActivity(data.message, data.icon || 'fa-info-circle');
                break;
            case 'command_response':
                this.handleCommandResponse(data);
                break;
            case 'system_stats':
                this.updateSystemStats(data.stats);
                break;
            case 'memory_update':
                this.updateMemoryCount(data.count);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }
    
    sendCommand(command) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'command',
                command: command,
                timestamp: Date.now()
            }));
            
            this.addActivity(`Executing: ${command}`, 'fa-terminal');
            return true;
        } else {
            this.showToast('Not connected to JARVIS backend', 'error');
            return false;
        }
    }
    
    // Command Interface
    setupCommandInterface() {
        const input = document.getElementById('command-input');
        const sendBtn = document.getElementById('send-command-btn');
        const clearBtn = document.getElementById('clear-history');
        
        const executeCommand = () => {
            const command = input.value.trim();
            if (command) {
                this.executeCommand(command);
                input.value = '';
            }
        };
        
        sendBtn.addEventListener('click', executeCommand);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                executeCommand();
            }
        });
        
        clearBtn.addEventListener('click', () => {
            document.getElementById('command-history').innerHTML = '';
            this.showToast('Command history cleared', 'info');
        });
        
        // Clear activity button
        document.getElementById('clear-activity').addEventListener('click', () => {
            document.getElementById('activity-feed').innerHTML = '';
            this.showToast('Activity feed cleared', 'info');
        });
    }
    
    executeCommand(command) {
        this.addCommandToHistory(command, 'Processing...');
        
        if (this.sendCommand(command)) {
            document.getElementById('input-status').textContent = `Processing: "${command}"`;
        } else {
            document.getElementById('input-status').textContent = 'Error: Not connected';
        }
    }
    
    addCommandToHistory(command, response) {
        const history = document.getElementById('command-history');
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
            <div class="history-command">
                <i class="fas fa-user"></i>
                <span>${this.escapeHtml(command)}</span>
            </div>
            <div class="history-response">
                <i class="fas fa-robot"></i>
                <span>${this.escapeHtml(response)}</span>
            </div>
            <div class="history-time">Just now</div>
        `;
        history.insertBefore(item, history.firstChild);
    }
    
    handleCommandResponse(data) {
        const history = document.getElementById('command-history');
        const latestItem = history.querySelector('.history-item');
        
        if (latestItem) {
            const responseElement = latestItem.querySelector('.history-response span');
            responseElement.textContent = data.response || 'Command executed';
        }
        
        document.getElementById('input-status').textContent = 'Ready to receive commands';
        
        if (data.success) {
            this.showToast('Command executed successfully', 'success');
        } else {
            this.showToast('Command failed', 'error');
        }
    }
    
    // Quick Actions
    setupQuickActions() {
        const actionButtons = document.querySelectorAll('.action-btn');
        
        actionButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const command = btn.dataset.command;
                this.executeCommand(command);
            });
        });
    }
    
    // Voice Input
    setupVoiceInput() {
        const voiceBtn = document.getElementById('voice-input-btn');
        
        // Check for browser support
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onstart = () => {
                this.isListening = true;
                voiceBtn.classList.add('listening');
                document.getElementById('input-status').textContent = 'Listening...';
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('command-input').value = transcript;
                document.getElementById('input-status').textContent = `Heard: "${transcript}"`;
                this.executeCommand(transcript);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.showToast(`Voice input error: ${event.error}`, 'error');
                document.getElementById('input-status').textContent = 'Voice input error';
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                voiceBtn.classList.remove('listening');
            };
            
            voiceBtn.addEventListener('click', () => {
                if (this.isListening) {
                    this.recognition.stop();
                } else {
                    this.recognition.start();
                }
            });
        } else {
            voiceBtn.disabled = true;
            voiceBtn.title = 'Voice input not supported in this browser';
            console.warn('Speech recognition not supported');
        }
    }
    
    // Activity Feed
    addActivity(message, icon = 'fa-info-circle') {
        const feed = document.getElementById('activity-feed');
        const item = document.createElement('div');
        item.className = 'activity-item';
        item.innerHTML = `
            <i class="fas ${icon}"></i>
            <div class="activity-content">
                <span class="activity-title">${this.escapeHtml(message)}</span>
                <span class="activity-time">Just now</span>
            </div>
        `;
        feed.insertBefore(item, feed.firstChild);
        
        // Keep only last 50 items
        while (feed.children.length > 50) {
            feed.removeChild(feed.lastChild);
        }
    }
    
    // System Stats
    updateSystemStats(stats) {
        if (stats.cpu !== undefined) {
            document.getElementById('cpu-usage').textContent = `${stats.cpu}%`;
            document.querySelector('.progress-fill.blue').style.width = `${stats.cpu}%`;
        }
        
        if (stats.memory !== undefined) {
            document.getElementById('memory-usage').textContent = stats.memory;
            const memPercent = parseInt(stats.memory) / 16 * 100; // Assuming 16GB total
            document.querySelector('.progress-fill.green').style.width = `${memPercent}%`;
        }
        
        if (stats.gpu !== undefined) {
            document.getElementById('gpu-usage').textContent = `${stats.gpu}%`;
            document.querySelector('.progress-fill.purple').style.width = `${stats.gpu}%`;
        }
    }
    
    updateMemoryCount(count) {
        document.getElementById('memory-items').textContent = count;
    }
    
    // Uptime Counter
    startUptime() {
        const startTime = Date.now();
        
        setInterval(() => {
            const elapsed = Date.now() - startTime;
            const hours = Math.floor(elapsed / 3600000);
            const minutes = Math.floor((elapsed % 3600000) / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            
            const uptime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            document.getElementById('uptime').textContent = uptime;
        }, 1000);
    }
    
    // Toast Notifications
    showToast(message, type = 'info') {
        const toast = document.getElementById('connection-toast');
        const icon = toast.querySelector('i');
        const text = toast.querySelector('span');
        
        // Set icon based on type
        icon.className = 'fas ';
        switch (type) {
            case 'success':
                icon.className += 'fa-check-circle';
                break;
            case 'error':
                icon.className += 'fa-exclamation-circle';
                break;
            case 'warning':
                icon.className += 'fa-exclamation-triangle';
                break;
            default:
                icon.className += 'fa-info-circle';
        }
        
        text.textContent = message;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
    
    // Demo Data (Remove when connected to real backend)
    simulateActivity() {
        // Simulate some initial activity
        setTimeout(() => {
            this.addActivity('System initialized successfully', 'fa-check-circle');
        }, 1000);
        
        setTimeout(() => {
            this.addActivity('Voice recognition ready', 'fa-microphone');
        }, 2000);
        
        setTimeout(() => {
            this.addActivity('All tools loaded', 'fa-tools');
        }, 3000);
        
        // Simulate periodic stats updates
        setInterval(() => {
            this.updateSystemStats({
                cpu: Math.floor(Math.random() * 30) + 20,
                gpu: Math.floor(Math.random() * 20) + 10
            });
        }, 5000);
    }
    
    // Utility
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.jarvisDashboard = new JarvisDashboard();
});

// Handle mobile menu toggle
if (window.innerWidth <= 768) {
    const menuToggle = document.createElement('button');
    menuToggle.className = 'btn-icon menu-toggle';
    menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
    menuToggle.style.position = 'fixed';
    menuToggle.style.bottom = '2rem';
    menuToggle.style.left = '2rem';
    menuToggle.style.zIndex = '101';
    
    document.body.appendChild(menuToggle);
    
    menuToggle.addEventListener('click', () => {
        document.querySelector('.sidebar').classList.toggle('open');
    });
}
