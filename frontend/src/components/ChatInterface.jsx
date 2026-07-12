import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { sendMessage } from '../store/slices/chatSlice';

export default function ChatInterface() {
  const dispatch = useDispatch();
  const { messages, status } = useSelector((s) => s.chat);
  const { activeHcpId } = useSelector((s) => s.interactions);
  const [text, setText] = useState('');
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    if (!activeHcpId) return alert('Select an HCP first.');
    dispatch(sendMessage({ message: text, hcpId: activeHcpId }));
    setText('');
  };

  return (
    <div>
      <div className="chat-window">
        {messages.length === 0 && (
          <p style={{ color: '#9ca3af', fontSize: 13 }}>
            Try: "Met Dr. Sharma today, discussed the new cardiology drug, left 2 samples,
            she wants a follow up call next week" — the agent will call log_interaction.
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role}`}>
            {m.text}
            {m.toolUsed && <span className="tool-tag">tool used: {m.toolUsed}</span>}
          </div>
        ))}
        {status === 'loading' && <div className="chat-bubble agent">Thinking…</div>}
        <div ref={scrollRef} />
      </div>
      <form className="chat-input-row" onSubmit={handleSend}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type a message to the CRM agent…"
        />
        <button className="btn-primary" type="submit" disabled={status === 'loading'}>
          Send
        </button>
      </form>
    </div>
  );
}
