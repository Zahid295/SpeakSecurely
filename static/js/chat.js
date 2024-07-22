$(document).ready(function() {
    // Connect to the SocketIO server
    const socket = io(`${window.location.protocol}//${window.location.host}`);
    // Send message
    $('#message-form').submit(function(e) {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: `${window.location.protocol}//${window.location.host}/send`,// The route that will handle the post request
            data: {
                recipient: $('#recipient').val(),
                message: $('#message').val()
            },
            success: function(response) {
                // Clear the message input field
                $('#message').val('');
                // Optionally, you can add the new message to the chat window
            },
            error: function(error) {
                console.log("Error:", error);
                if (error.status === 401) {
                    window.location.href = '/login';
            }
        }

        });
    });

    // Function to refresh the messages
    function refreshMessages() {
        $.ajax({
            type: 'GET',
            url: `${window.location.protocol}//${window.location.host}/messages`, // The route that will handle the get request
            success: function(messages) {
                $('#messages').empty(); // Clear the messages div
                for (let i = 0; i < messages.length; i++) {
                    // Append each message to the messages div
                    $('#messages').append('<p><strong>' + (messages[i].sender || 'unknown') + '</strong>: ' + messages[i].body + '</p>');
                }
            },
            error: function(error) {
                console.log("Error:", error);
                if (error.status === 401) {
                    window.location.href = '/login';
                }
            }
        });
    }

    // Handle real-time message updates
    socket.on('message', function(data) {
        $('#messages').append('<p><strong>' + data.sender + '</strong>: ' + data.body + '</p>');
    });

    // Refresh messages every 5 seconds
    setInterval(refreshMessages, 5000);
});
