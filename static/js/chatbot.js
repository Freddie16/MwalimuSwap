// static/js/chatbot.js
// This file is specifically for the AI Chatbot interactions.
// It is included in chatbot_ui.html via {% block extra_js %}.

// The core logic for the chatbot is now directly within chatbot_ui.html's <script> tag
// as it relies heavily on Django template variables (csrf_token, URLs).
// This file is kept here for completeness of the project structure,
// but its content is effectively merged into the template for direct access to context.

// If you were to externalize this, you'd need to pass CSRF token and URLs
// as data attributes or global JS variables from the Django template.

// Example of how you might structure it if externalized, requiring data from template:
/*
document.addEventListener('DOMContentLoaded', function() {
    const chatWindow = document.getElementById('chat-window');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('id_message');

    // These would need to be passed from Django template, e.g., via data attributes or a global object
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const chatUrl = chatForm.action; // Or a specific data attribute for the URL

    // Scroll to the bottom of the chat window on load
    chatWindow.scrollTop = chatWindow.scrollHeight;

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const userMessage = messageInput.value.trim();
        if (userMessage === '') {
            return;
        }

        appendMessage(userMessage, 'USER');
        messageInput.value = '';
        chatWindow.scrollTop = chatWindow.scrollHeight;

        const loadingIndicator = appendMessage('Typing...', 'AI loading');
        chatWindow.scrollTop = chatWindow.scrollHeight;

        fetch(chatUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            if (loadingIndicator && loadingIndicator.parentNode) {
                loadingIndicator.parentNode.removeChild(loadingIndicator);
            }
            appendMessage(data.message, 'AI');
            chatWindow.scrollTop = chatWindow.scrollHeight;
        })
        .catch(error => {
            console.error('Error sending message:', error);
            if (loadingIndicator && loadingIndicator.parentNode) {
                loadingIndicator.parentNode.removeChild(loadingIndicator);
            }
            appendMessage("Sorry, I'm having trouble connecting to the AI. Please try again.", 'AI');
            chatWindow.scrollTop = chatWindow.scrollHeight;
        });
    });

    function appendMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${type === 'USER' ? 'justify-end' : 'justify-start'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = `rounded-lg p-3 max-w-[70%] shadow-md ${
            type === 'USER' ? 'bg-indigo-500 text-white' :
            type === 'AI' ? 'bg-gray-200 text-gray-800' :
            'bg-gray-300 text-gray-600 italic'
        }`;
        contentDiv.textContent = text;
        
        messageDiv.appendChild(contentDiv);
        chatWindow.appendChild(messageDiv);

        return messageDiv;
    }
});
*/
