import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { listHcps, createInteraction, listInteractions } from '../../api/api';

export const fetchHcps = createAsyncThunk('interactions/fetchHcps', async () => {
  const res = await listHcps();
  return res.data;
});

export const submitInteraction = createAsyncThunk(
  'interactions/submit',
  async (payload) => {
    const res = await createInteraction(payload);
    return res.data;
  }
);

export const fetchInteractions = createAsyncThunk(
  'interactions/fetchAll',
  async (hcpId) => {
    const res = await listInteractions(hcpId);
    return res.data;
  }
);

const interactionSlice = createSlice({
  name: 'interactions',
  initialState: {
    hcps: [],
    interactions: [],
    activeHcpId: null,
    submitStatus: 'idle',
    lastResult: null,
    error: null,
  },
  reducers: {
    setActiveHcp(state, action) {
      state.activeHcpId = action.payload;
    },
    clearLastResult(state) {
      state.lastResult = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHcps.fulfilled, (state, action) => {
        state.hcps = action.payload;
        if (!state.activeHcpId && action.payload.length > 0) {
          state.activeHcpId = action.payload[0].id;
        }
      })
      .addCase(submitInteraction.pending, (state) => {
        state.submitStatus = 'loading';
      })
      .addCase(submitInteraction.fulfilled, (state, action) => {
        state.submitStatus = 'succeeded';
        state.lastResult = action.payload;
      })
      .addCase(submitInteraction.rejected, (state, action) => {
        state.submitStatus = 'failed';
        state.error = action.error.message;
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.interactions = action.payload;
      });
  },
});

export const { setActiveHcp, clearLastResult } = interactionSlice.actions;
export default interactionSlice.reducer;
