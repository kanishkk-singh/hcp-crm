import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchHcps, setActiveHcp } from '../store/slices/interactionSlice';

export default function HcpSelector() {
  const dispatch = useDispatch();
  const { hcps, activeHcpId } = useSelector((s) => s.interactions);

  useEffect(() => {
    dispatch(fetchHcps());
  }, [dispatch]);

  return (
    <div className="hcp-select-row field">
      <label>Healthcare Professional</label>
      <select
        value={activeHcpId || ''}
        onChange={(e) => dispatch(setActiveHcp(e.target.value))}
      >
        <option value="" disabled>Select an HCP</option>
        {hcps.map((h) => (
          <option key={h.id} value={h.id}>
            {h.name} {h.specialty ? `— ${h.specialty}` : ''}
          </option>
        ))}
      </select>
      {hcps.length === 0 && (
        <p style={{ fontSize: 12, color: '#9ca3af', marginTop: 6 }}>
          No HCPs yet — create one via POST /api/hcps/ (see README) before logging interactions.
        </p>
      )}
    </div>
  );
}
