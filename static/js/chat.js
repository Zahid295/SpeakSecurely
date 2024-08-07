$(document).ready(function() {
    // Connect to the SocketIO server
     // Correct protocol is used
     const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
     const socket = io(`${protocol}//${window.location.host}`, {
         transports: ['websocket', 'polling'],
         upgrade: false
     });
     // Handle contact click to populate recipient field
    $('#contacts').on('click', '.contact', function(e) {
        e.preventDefault();
        const username = $(this).data('username');
        const recipientId = $(this).data('id');
        $('#recipient').val(username);
        $('#recipient-id').val(recipientId);
        refreshMessages(recipientId); 
    });
    // Send message
    $('#message-form').submit(function(e) {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: `${window.location.protocol}//${window.location.host}/send`,// The route that will handle the post request
            data: {
                recipient: $('#recipient').val(),
                recipient_id: $('#recipient-id').val(), 
                message: $('#message').val()
            },
            success: function(response) {
                // Clear the message input field
                $('#message').val('');
                refreshMessages($('#recipient-id').val());
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
    function refreshMessages(recipientId) {
        $.ajax({
            type: 'GET',
            url: `${window.location.protocol}//${window.location.host}/messages/${recipientId}`, // The route that will handle the get request
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
        const currentRecipientId = $('#recipient-id').val();
        if (data.sender_id === currentRecipientId || data.recipient_id === currentRecipientId) {
        $('#messages').append('<p><strong>' + data.sender + '</strong>: ' + data.body + '</p>');
        }
    });

    // Refresh messages every 5 seconds
    setInterval(refreshMessages, 5000);
});
