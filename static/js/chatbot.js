/**
 * Chatbot JavaScript for BookSage
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendMessageBtn = document.getElementById('sendMessage');
    const clearChatBtn = document.getElementById('clearChat');
    const saveChatBtn = document.getElementById('saveChat');
    const suggestedQuestions = document.querySelectorAll('.suggested-question');
    const bookContext = document.getElementById('bookContext');
    
    // Check if we're on the chatbot page
    if (!chatMessages || !messageInput || !sendMessageBtn) {
        return;
    }
    
    // Load chat history from localStorage
    loadChatHistory();
    
    // Scroll to bottom of chat
    scrollToBottom();
    
    // Send message when button is clicked
    sendMessageBtn.addEventListener('click', sendMessage);
    
    // Send message when Enter key is pressed
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Clear chat
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to clear the chat history?')) {
                chatMessages.innerHTML = '';
                localStorage.removeItem('chatHistory');
                
                // Add initial welcome message
                addMessage('👋 Hello! I\'m BookSage, your AI book assistant. How can I help you with books today?', 'bot');
            }
        });
    }
    
    // Save chat
    if (saveChatBtn) {
        saveChatBtn.addEventListener('click', function() {
            const chatContent = document.createElement('div');
            
            // Add title
            const title = document.createElement('h1');
            title.textContent = 'BookSage Chat History';
            chatContent.appendChild(title);
            
            // Add timestamp
            const timestamp = document.createElement('p');
            timestamp.textContent = 'Exported on: ' + new Date().toLocaleString();
            chatContent.appendChild(timestamp);
            
            // Add messages
            const messagesContainer = document.createElement('div');
            messagesContainer.innerHTML = chatMessages.innerHTML;
            chatContent.appendChild(messagesContainer);
            
            // Create and download HTML file
            const htmlContent = `
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>BookSage Chat History</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            max-width: 800px;
                            margin: 0 auto;
                            padding: 20px;
                        }
                        .message {
                            margin-bottom: 15px;
                            padding: 10px;
                            border-radius: 5px;
                        }
                        .user {
                            background-color: #e6f7ff;
                            margin-left: 50px;
                        }
                        .bot {
                            background-color: #f0f0f0;
                            margin-right: 50px;
                        }
                        .message-time {
                            font-size: 12px;
                            color: #888;
                            text-align: right;
                        }
                    </style>
                </head>
                <body>
                    ${chatContent.innerHTML}
                </body>
                </html>
            `;
            
            const blob = new Blob([htmlContent], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            
            a.href = url;
            a.download = 'booksage-chat-' + new Date().toISOString().slice(0, 10) + '.html';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
    }
    
    // Suggested questions
    if (suggestedQuestions.length > 0) {
        suggestedQuestions.forEach(question => {
            question.addEventListener('click', function() {
                messageInput.value = this.textContent.trim();
                sendMessage();
            });
        });
    }
    
    function sendMessage() {
        const message = messageInput.value.trim();
        
        if (message) {
            // Clear input
            messageInput.value = '';
            
            // Add user message to chat
            addMessage(message, 'user');
            
            // Show typing indicator
            addTypingIndicator();
            
            // Get book context if available
            let bookId = null;
            if (bookContext) {
                bookId = bookContext.dataset.bookId;
            }
            
            // Send message to backend
            fetch('/api/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    message: message,
                    book_id: bookId
                })
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                removeTypingIndicator();
                
                // Add bot response to chat
                addMessage(data.response, 'bot');
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Remove typing indicator
                removeTypingIndicator();
                
                // Add error message
                addMessage('Sorry, there was an error processing your request. Please try again.', 'bot');
            });
        }
    }
    
    function addMessage(text, sender) {
        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        // Create message bubble
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        
        // Format links in the text
        const formattedText = formatText(text);
        
        // Set message content
        bubbleDiv.innerHTML = `<p class="mb-0">${formattedText}</p>`;
        
        // Create time element
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = getTimeString();
        
        // Append elements
        messageDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(timeDiv);
        
        // Add to chat
        chatMessages.appendChild(messageDiv);
        
        // Save chat history
        saveChatHistory();
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    function addTypingIndicator() {
        // Create typing indicator
        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'message bot typing-indicator-container';
        indicatorDiv.id = 'typingIndicator';
        
        // Create indicator bubble
        const indicatorBubble = document.createElement('div');
        indicatorBubble.className = 'typing-indicator';
        indicatorBubble.innerHTML = '<span></span><span></span><span></span>';
        
        // Append elements
        indicatorDiv.appendChild(indicatorBubble);
        
        // Add to chat
        chatMessages.appendChild(indicatorDiv);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    function removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    function formatText(text) {
        // Convert URLs to links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        text = text.replace(urlRegex, url => `<a href="${url}" target="_blank">${url}</a>`);
        
        // Convert book titles with quotes to bold
        const bookTitleRegex = /"([^"]+)"/g;
        text = text.replace(bookTitleRegex, (match, title) => `"<strong>${title}</strong>"`);
        
        // Convert newlines to <br>
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }
    
    function getTimeString() {
        const now = new Date();
        let hours = now.getHours();
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        
        hours = hours % 12;
        hours = hours ? hours : 12; // Convert 0 to 12
        
        return `${hours}:${minutes} ${ampm}`;
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function saveChatHistory() {
        localStorage.setItem('chatHistory', chatMessages.innerHTML);
    }
    
    function loadChatHistory() {
        const history = localStorage.getItem('chatHistory');
        if (history) {
            chatMessages.innerHTML = history;
        }
    }
});
