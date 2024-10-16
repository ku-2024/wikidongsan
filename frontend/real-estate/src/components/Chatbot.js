import React, { useState, useEffect, useRef } from 'react';
import '../Chatbot.css';

const ChatbotPopup = ({apt_code}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const togglePopup = () => {
    setIsOpen(!isOpen);
  };

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
    adjustTextareaHeight();
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  };
  const typeMessage = (message, index) => {
    let i = 0;
    const typing = () => {
      if (i < message.length) {
        setMessages(prevMessages => 
          prevMessages.map((msg, idx) => 
            idx === index ? { ...msg, text: message.substring(0, i + 1), isTyping: true } : msg
          )
        );
        i++;
        setTimeout(typing, Math.random() * 30 + 20); // 20~50ms 사이의 랜덤한 간격
      } else {
        setMessages(prevMessages => 
          prevMessages.map((msg, idx) => 
            idx === index ? { ...msg, isTyping: false } : msg
          )
        );
      }
    };
    typing();
  };

  const handleSendMessage = async () => {
    if (inputValue.trim() === '') return;

    const messageToSend = inputValue;
    setInputValue('');
    setMessages(prevMessages => [...prevMessages, { text: messageToSend, sender: 'user' }]);
    setIsLoading(true);

    try {
      const response = await fetch(`/post/chatbot/?apt_code=${apt_code}&chat_input=${messageToSend}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageToSend }),
      });

      const data = await response.json();

      const newIndex = messages.length + 1;
      setMessages(prevMessages => [...prevMessages, { text: '', sender: 'bot', isTyping: true }]);
      
      typeMessage(data.data, newIndex);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prevMessages => [...prevMessages, { text: '죄송합니다. 오류가 발생했습니다.', sender: 'bot' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-icon" onClick={togglePopup}>
        <img src="/SolarLLM_Symbol_Color.png" alt="Chatbot Icon" />
      </div>

      {isOpen && (
        <div className="chatbot-popup">
          <div className="chatbot-header">
            <h3 className='text-white'>Chat</h3>
            <button className="close-btn" onClick={togglePopup}>
              <svg xmlns="http://www.w3.org/2000/svg" fill="#FFFFFF" viewBox="0 0 24 24" strokeWidth="1.5" stroke="#FFFFFF" className="size-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="chatbot-body">
            {messages.map((message, index) => (
              <div key={index} className={`flex items-start ${message.sender === 'user' ? 'justify-end' : 'justify-start gap-3'}`}>
                {message.sender === 'bot' && (
                  <img className="w-11 h-11 rounded-full" src="/SolarLLM_Symbol_Color.png" alt="Bot Avatar" />
                )}
                <div className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}>
                  {message.text}
                  {message.isTyping && <span className="typing-indicator"></span>}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
            {isLoading && (
              <div className="flex items-start loader">
                <img className="w-11 h-11 rounded-full" src="/SolarLLM_Symbol_Color.png" alt="Loading" />
              </div>
            )}
          </div>
          <div className="chatbot-input">
            <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={handleInputChange}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder="메시지를 입력하세요..."
                rows="1"
              />
            <button onClick={handleSendMessage}>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="size-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatbotPopup;