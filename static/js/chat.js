document.addEventListener('DOMContentLoaded', () => {
    const chatBubble = document.getElementById('chat-bubble');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    // Restore chat history and open state using localStorage for better persistence
    const savedHistory = localStorage.getItem('chatHistory');
    if (savedHistory) {
        chatMessages.innerHTML = savedHistory;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    const isChatOpen = localStorage.getItem('chatOpen');
    if (isChatOpen === 'true') {
        chatWindow.classList.add('active');
    }

    chatBubble.addEventListener('click', () => {
        chatWindow.classList.toggle('active');
        localStorage.setItem('chatOpen', chatWindow.classList.contains('active'));
        if (chatWindow.classList.contains('active')) {
            chatInput.focus();
        }
    });

    closeChat.addEventListener('click', () => {
        chatWindow.classList.remove('active');
        localStorage.setItem('chatOpen', 'false');
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        chatInput.value = '';

        // Add typing indicator
        const typing = document.createElement('div');
        typing.className = 'message bot typing-message';
        typing.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
        chatMessages.appendChild(typing);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            const data = await response.json();

            // Remove typing indicator
            if (typing.parentNode) {
                chatMessages.removeChild(typing);
            }

            // Add bot response
            addMessage(data.response, 'bot', data.action);
        } catch (error) {
            if (typing.parentNode) {
                chatMessages.removeChild(typing);
            }
            addMessage("Lo siento, something went wrong. Please try again.", 'bot');
        }
    });

    function addMessage(text, sender, action = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;

        let content = text;
        if (action && action.type === 'link') {
            const label = action.label || "View Results";
            content += `<br><a href="${action.url}" class="btn-primary" style="margin-top: 0.5rem; display: inline-block; padding: 0.25rem 0.75rem; font-size: 0.75rem; text-decoration: none; border-radius: 4px;">${label}</a>`;
        }

        msgDiv.innerHTML = content;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Save history after each message
        localStorage.setItem('chatHistory', chatMessages.innerHTML);
    }
});
