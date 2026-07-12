import React from 'react';
import LogInteractionScreen from './components/LogInteractionScreen';

export default function App() {
  return (
    <div className="app-shell">
      <div className="app-header">
        <h1>HCP Module — Log Interaction</h1>
        <p>Log a rep's interaction with a Healthcare Professional via form or chat, powered by a LangGraph agent.</p>
      </div>
      <LogInteractionScreen />
    </div>
  );
}
