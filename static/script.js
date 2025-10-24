// NEOC AI Assistant Frontend
class NEOCAIAssistant {
    constructor() {
        this.apiBase = window.location.protocol + '//' + window.location.hostname + ':8000';
        this.conversationId = this.generateConversationId();
        this.isLoading = false;

        this.initializeElements();
        this.attachEventListeners();
        this.updateSendButtonState();
        this.loadConversationHistory();
    }

    initializeElements() {
        console.log('Initializing elements...');

        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.inputStatus = document.getElementById('inputStatus');
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.welcomeMessage = document.querySelector('.welcome-message');

        console.log('Elements initialized:', {
            chatMessages: !!this.chatMessages,
            messageInput: !!this.messageInput,
            sendButton: !!this.sendButton,
            inputStatus: !!this.inputStatus
        });

        // Test input field
        if (this.messageInput) {
            this.messageInput.disabled = false; // Ensure input is enabled
            this.messageInput.value = 'Test input working';
            setTimeout(() => {
                this.messageInput.value = '';
                console.log('Input field test completed');
            }, 1000);
        }
    }

    attachEventListeners() {
        console.log('Attaching event listeners...');

        // Send button click
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => {
                console.log('Send button clicked');
                this.sendMessage();
            });
            console.log('Send button event listener attached');
        }

        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => {
                console.log('Send button clicked');
                this.sendMessage();
            });
            console.log('Send button event listener attached');
        }

        // Input handling
        if (this.messageInput) {
            this.messageInput.addEventListener('input', (e) => {
                console.log('Input event fired, value:', e.target.value);
                this.updateInputHeight();
                this.updateSendButtonState();
            });

            this.messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    console.log('Enter key pressed, sending message');
                    this.sendMessage();
                }
            });

            // Focus management
            this.messageInput.addEventListener('focus', () => {
                this.messageInput.setAttribute('aria-expanded', 'true');
            });

            this.messageInput.addEventListener('blur', () => {
                this.messageInput.setAttribute('aria-expanded', 'false');
            });

            console.log('Input event listeners attached');
        } else {
            console.error('Message input not found');
        }

        // Sidebar toggle
        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        // New chat
        if (this.newChatBtn) {
            this.newChatBtn.addEventListener('click', () => this.startNewChat());
        }

        // Suggestion chips
        document.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                const prompt = e.target.dataset.prompt;
                if (prompt) {
                    console.log('Chip clicked:', prompt);
                    this.messageInput.value = prompt;
                    this.updateInputHeight();
                    this.updateSendButtonState();
                    this.messageInput.focus();
                }
            });
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 &&
                !this.sidebar.contains(e.target) &&
                !this.sidebarToggle.contains(e.target) &&
                this.sidebar.classList.contains('open')) {
                this.toggleSidebar();
            }
        });

        console.log('All event listeners attached');
    }

    generateConversationId() {
        return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    updateInputHeight() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    updateSendButtonState() {
        if (!this.messageInput || !this.sendButton) {
            console.error('Message input or send button not found');
            return;
        }

        const hasText = this.messageInput.value.trim().length > 0;
        console.log('Updating send button state:', hasText);
        this.sendButton.disabled = !hasText;
        this.sendButton.setAttribute('aria-label', hasText ? 'Send message' : 'Type a message to send');
    }

    toggleSidebar() {
        this.sidebar.classList.toggle('open');
        const isOpen = this.sidebar.classList.contains('open');
        this.sidebarToggle.setAttribute('aria-expanded', isOpen.toString());
        this.announceToScreenReader(isOpen ? 'Sidebar opened' : 'Sidebar closed');
    }

    startNewChat() {
        // Clear current conversation
        this.conversationId = this.generateConversationId();

        // Clear messages except welcome
        const messages = this.chatMessages.querySelectorAll('.message');
        messages.forEach(msg => {
            if (!msg.querySelector('.assistant')) {
                msg.remove();
            }
        });

        // Show welcome message
        if (this.welcomeMessage) {
            this.welcomeMessage.style.display = 'block';
        }

        // Reset input
        this.messageInput.value = '';
        this.updateInputHeight();
        this.updateSendButtonState();

        // Focus input
        this.messageInput.focus();

        this.announceToScreenReader('Started new conversation');
    }

    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'assertive');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;

        document.body.appendChild(announcement);

        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;

        // Hide welcome message on first message
        if (this.welcomeMessage && this.welcomeMessage.style.display !== 'none') {
            this.welcomeMessage.style.display = 'none';
        }

        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.updateInputHeight();
        this.updateSendButtonState();
        this.setLoading(true);

        // Announce to screen readers
        this.announceToScreenReader('Sending message...');

        try {
            const response = await this.callChatAPI(message);
            this.addMessage(response.response, 'assistant', response.sources);
            this.announceToScreenReader('Response received');
        } catch (error) {
            console.error('Error sending message:', error);

            // Handle specific error types
            if (error.message && error.message.includes('503')) {
                this.addMessage('🤖 AI Service Unavailable\n\nThe AI assistant is currently experiencing high demand or requires more system resources. Please try again in a few moments, or contact support if the issue persists.', 'assistant');
                this.announceToScreenReader('AI service is currently unavailable');
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
                this.announceToScreenReader('Error sending message');
            }
        } finally {
            this.setLoading(false);
        }
    }

    async callChatAPI(message) {
        const response = await fetch(`${this.apiBase}/api/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_id: this.conversationId
            })
        });

        if (!response.ok) {
            // Try to get error details from response
            let errorMessage = `API call failed: ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (e) {
                // Ignore JSON parsing errors
            }
            throw new Error(`${response.status}: ${errorMessage}`);
        }

        return await response.json();
    }

    async loadConversationHistory() {
        try {
            const response = await fetch(`${this.apiBase}/api/chat/history/${this.conversationId}`);
            if (response.ok) {
                const data = await response.json();
                this.displayConversationHistory(data.messages);
            }
        } catch (error) {
            console.log('No existing conversation history found');
        }
    }

    displayConversationHistory(messages) {
        // Clear existing messages except the welcome message
        const welcomeMessage = this.chatMessages.querySelector('.message.assistant');
        this.chatMessages.innerHTML = '';
        if (welcomeMessage) {
            this.chatMessages.appendChild(welcomeMessage);
        }

        // Add historical messages
        messages.forEach(msg => {
            this.addMessage(msg.content, msg.role, [], false);
        });
    }

    addMessage(content, sender, sources = [], animate = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender} ${animate ? 'fade-in' : ''}`;
        messageDiv.setAttribute('role', 'article');
        messageDiv.setAttribute('aria-label', `${sender} message`);

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const textP = document.createElement('p');
        textP.textContent = content;
        contentDiv.appendChild(textP);

        // Add sources if available
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'sources';
            sourcesDiv.setAttribute('aria-label', 'Source references');
            sourcesDiv.textContent = `Sources: ${sources.join(', ')}`;
            contentDiv.appendChild(sourcesDiv);
        }

        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        this.scrollToBottom();

        // Announce new message to screen readers
        this.announceToScreenReader(`New ${sender} message: ${content.substring(0, 100)}${content.length > 100 ? '...' : ''}`);
    }

    setLoading(loading) {
        this.isLoading = loading;

        if (loading) {
            this.sendButton.disabled = true;
            this.messageInput.disabled = true;
            this.messageInput.setAttribute('aria-label', 'Input disabled while processing');
            this.inputStatus.textContent = 'AI is thinking...';
            this.inputStatus.setAttribute('aria-live', 'polite');
            this.showTypingIndicator();
        } else {
            this.sendButton.disabled = !this.messageInput.value.trim();
            this.messageInput.disabled = false; // Ensure input is always enabled when not loading
            this.messageInput.setAttribute('aria-label', 'Type your message');
            this.inputStatus.textContent = 'Ready';
            this.inputStatus.setAttribute('aria-live', 'polite');
            this.hideTypingIndicator();
            this.messageInput.focus();
        }
    }

    showTypingIndicator() {
        // Remove existing typing indicator
        this.hideTypingIndicator();

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant';
        typingDiv.id = 'typingIndicator';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';

        contentDiv.appendChild(typingIndicator);
        typingDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    // Utility method to check server health
    async checkServerHealth() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);

            const response = await fetch(`${this.apiBase}/health`, {
                signal: controller.signal,
                headers: {
                    'Cache-Control': 'no-cache'
                }
            });

            clearTimeout(timeoutId);
            return response.ok;
        } catch (error) {
            if (error.name === 'AbortError') {
                console.warn('Health check timed out');
            }
            return false;
        }
    }

    updateConnectionStatus(connected) {
        const statusDot = this.connectionStatus.querySelector('.status-dot');
        const statusText = this.connectionStatus.querySelector('span');

        if (statusDot) {
            statusDot.style.background = connected ? 'var(--accent-green)' : 'var(--error-red)';
        }

        if (statusText) {
            statusText.textContent = connected ? 'Online' : 'Offline';
        }

        this.connectionStatus.setAttribute('aria-label',
            connected ? 'Server connected' : 'Server disconnected'
        );
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded, initializing NEOC AI Assistant...');

    try {
        const assistant = new NEOCAIAssistant();
        console.log('Assistant initialized successfully');

        // Check server health on load
        const healthy = await assistant.checkServerHealth();
        console.log('Server health check result:', healthy);
        assistant.updateConnectionStatus(healthy);

        if (!healthy) {
            assistant.inputStatus.textContent = '⚠️ Server connection failed. Please ensure the backend is running.';
            assistant.messageInput.disabled = true;
            assistant.sendButton.disabled = true;
        } else {
            console.log('Server is healthy, enabling input');
            assistant.messageInput.disabled = false;
            assistant.updateSendButtonState();
        }

        // Make assistant available globally for debugging
        window.neocAssistant = assistant;
        console.log('NEOC AI Assistant ready');
    } catch (error) {
        console.error('Error initializing NEOC AI Assistant:', error);
    }
});

// Handle page visibility changes to maintain connection
document.addEventListener('visibilitychange', async () => {
    if (!document.hidden && window.neocAssistant) {
        const healthy = await window.neocAssistant.checkServerHealth();
        window.neocAssistant.updateConnectionStatus(healthy);

        if (!healthy) {
            window.neocAssistant.inputStatus.textContent = '⚠️ Connection lost. Attempting to reconnect...';
            window.neocAssistant.messageInput.disabled = true;
            window.neocAssistant.sendButton.disabled = true;

            // Try to reconnect after 3 seconds
            setTimeout(async () => {
                const reconnected = await window.neocAssistant.checkServerHealth();
                window.neocAssistant.updateConnectionStatus(reconnected);

                if (reconnected) {
                    window.neocAssistant.inputStatus.textContent = '✅ Reconnected successfully';
                    window.neocAssistant.messageInput.disabled = false;
                    window.neocAssistant.updateSendButtonState();
                } else {
                    window.neocAssistant.inputStatus.textContent = '❌ Connection failed. Please refresh the page.';
                }
            }, 3000);
        } else {
            window.neocAssistant.inputStatus.textContent = '✅ Connection restored';
            window.neocAssistant.messageInput.disabled = false;
            window.neocAssistant.updateSendButtonState();
        }
    }
});