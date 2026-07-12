import React, { useState } from 'react';
import HcpSelector from './HcpSelector';
import StructuredForm from './StructuredForm';
import ChatInterface from './ChatInterface';

export default function LogInteractionScreen() {
  const [mode, setMode] = useState('form'); // 'form' | 'chat'

  return (
    <div className="card">
      <HcpSelector />

      <div className="tab-switch">
        <button className={mode === 'form' ? 'active' : ''} onClick={() => setMode('form')}>
          Structured Form
        </button>
        <button className={mode === 'chat' ? 'active' : ''} onClick={() => setMode('chat')}>
          Chat with Agent
        </button>
      </div>

      {mode === 'form' ? <StructuredForm /> : <ChatInterface />}
    </div>
  );
}
