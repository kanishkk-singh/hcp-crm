import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { sendChatMessage } from '../../api/api';

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ message, hcpId }) => {
    const res = await sendChatMessage({ message, hcp_id: hcpId });
    return { userMessage: message, ...res.data };
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [], // { role: 'user'|'agent', text, toolUsed }
    status: 'idle',
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state, action) => {
        state.status = 'loading';
        state.messages.push({ role: 'user', text: action.meta.arg.message });
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.status = 'idle';
        state.messages.push({
          role: 'agent',
          text: action.payload.reply,
          toolUsed: action.payload.tool_used,
        });
      })
      .addCase(sendMessage.rejected, (state) => {
        state.status = 'idle';
        state.messages.push({ role: 'agent', text: 'Something went wrong. Please try again.' });
      });
  },
});

export default chatSlice.reducer;
