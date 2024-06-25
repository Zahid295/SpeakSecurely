import React, { useState, useEffect } from 'react';

import io from 'socket.io-client';
 
const ChatComponent = () => {

  const [messages, setMessages] = useState([]);

  const [messageInput, setMessageInput] = useState('');

  const socket = io('http://localhost:5000'); // Replace with your server URL
 
  useEffect(() => {

    // Listen for the 'receive_message' event from the server

    socket.on('receive_message', (data) => {

      const receivedMessage = data.content;

      setMessages((prevMessages) => [...prevMessages, receivedMessage]);

    });
 
    // Clean up the socket connection when the component unmounts

    return () => {

      socket.disconnect();

    };

  }, []);
 
  const sendMessage = () => {

    socket.emit('send_message', { message: messageInput });

    setMessageInput('');

  };
 
  return (

    <div>

      <div>

        {messages.map((msg, index) => (

          <div key={index}>{msg}</div>

        ))}

      </div>

      <input

        type="text"

        value={messageInput}

        onChange={(e) => setMessageInput(e.target.value)}

      />

      <button onClick={sendMessage}>Send</button>

    </div>

  );

};
 
export default ChatComponent;
