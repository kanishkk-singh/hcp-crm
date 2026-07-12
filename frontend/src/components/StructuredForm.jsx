import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { submitInteraction, clearLastResult } from '../store/slices/interactionSlice';

const INTERACTION_TYPES = ['visit', 'call', 'email', 'conference'];

export default function StructuredForm() {
  const dispatch = useDispatch();
  const { activeHcpId, submitStatus, lastResult } = useSelector((s) => s.interactions);

  const [mode, setMode] = useState('manual'); // 'manual' or 'assisted'
  const [form, setForm] = useState({
    interaction_type: 'visit',
    topics_discussed: '',
    samples_given: '',
    materials_shared: '',
    follow_up_required: false,
    follow_up_notes: '',
    raw_input: '',
  });

  const update = (field, value) => setForm((f) => ({ ...f, [field]: value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!activeHcpId) return alert('Select an HCP first.');
    dispatch(clearLastResult());

    const payload = { hcp_id: activeHcpId };
    if (mode === 'assisted') {
      payload.raw_input = form.raw_input;
    } else {
      payload.interaction_type = form.interaction_type;
      payload.topics_discussed = form.topics_discussed;
      payload.samples_given = form.samples_given;
      payload.materials_shared = form.materials_shared;
      payload.follow_up_required = form.follow_up_required;
      payload.follow_up_notes = form.follow_up_notes;
    }
    dispatch(submitInteraction(payload));
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="tab-switch" style={{ marginBottom: 20 }}>
        <button type="button" className={mode === 'manual' ? 'active' : ''} onClick={() => setMode('manual')}>
          Fill Fields Manually
        </button>
        <button type="button" className={mode === 'assisted' ? 'active' : ''} onClick={() => setMode('assisted')}>
          Describe It, Let AI Fill Fields
        </button>
      </div>

      {mode === 'assisted' ? (
        <div className="field">
          <label>Describe what happened</label>
          <textarea
            placeholder="e.g. Met Dr. Sharma at City Hospital, discussed the new cardiology drug, left 2 samples, she wants a follow-up call next week."
            value={form.raw_input}
            onChange={(e) => update('raw_input', e.target.value)}
            required
          />
          <p style={{ fontSize: 12, color: '#9ca3af', marginTop: 6 }}>
            This text is sent to the log_interaction LangGraph tool, which uses Groq
            (gemma2-9b-it) to extract type, topics, samples, sentiment, and follow-up.
          </p>
        </div>
      ) : (
        <>
          <div className="field">
            <label>Interaction Type</label>
            <select value={form.interaction_type} onChange={(e) => update('interaction_type', e.target.value)}>
              {INTERACTION_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Topics Discussed</label>
            <input value={form.topics_discussed} onChange={(e) => update('topics_discussed', e.target.value)} placeholder="e.g. New cardiology drug, dosage guidance" />
          </div>
          <div className="field">
            <label>Samples Given</label>
            <input value={form.samples_given} onChange={(e) => update('samples_given', e.target.value)} placeholder="e.g. 2x CardioPlus 10mg" />
          </div>
          <div className="field">
            <label>Materials Shared</label>
            <input value={form.materials_shared} onChange={(e) => update('materials_shared', e.target.value)} placeholder="e.g. Clinical study brochure" />
          </div>
          <div className="checkbox-row">
            <input
              type="checkbox"
              checked={form.follow_up_required}
              onChange={(e) => update('follow_up_required', e.target.checked)}
            />
            <label>Follow-up required</label>
          </div>
          {form.follow_up_required && (
            <div className="field">
              <label>Follow-up Notes</label>
              <input value={form.follow_up_notes} onChange={(e) => update('follow_up_notes', e.target.value)} placeholder="e.g. Call back next Monday with pediatric dosage data" />
            </div>
          )}
        </>
      )}

      <button className="btn-primary" type="submit" disabled={submitStatus === 'loading'}>
        {submitStatus === 'loading' ? 'Saving…' : 'Log Interaction'}
      </button>

      {lastResult && (
        <div className="result-banner">
          Saved successfully. {lastResult.result ? `(AI-enriched via log_interaction tool)` : `Interaction ID: ${lastResult.interaction_id}`}
        </div>
      )}
    </form>
  );
}
