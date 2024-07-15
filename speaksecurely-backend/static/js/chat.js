const socket = io.connect('https://upgraded-space-tribble-7vvq9j4rgj5rfpxg4-5000.app.github.dev');

document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const messageArea = document.getElementById('message-area');

    sendButton.addEventListener('click', function() {
        const message = messageInput.value.trim();
        if(message) {
            // Emit the message to the server
            socket.emit('send_message', { message: message });

            // Clear the input field
            messageInput.value = '';
        }
    });

    // Listen for 'message_response' events from the server
    socket.on('message_response', function(data) {
        const newMessageDiv = document.createElement('div');
        newMessageDiv.textContent = data.message;
        messageArea.appendChild(newMessageDiv);

        // Scroll to the bottom of the message area
        messageArea.scrollTop = messageArea.scrollHeight;
    });
});

