import express from 'express';
import axios from 'axios';
import dotenv from 'dotenv';
import { MODULE_MAP } from './modules';
import { authenticateJWT } from './auth';
import { logRequest } from './logger';
import { ApiResponse } from './types';

dotenv.config();

const app = express();
app.use(express.json());

app.post('/api/v1/:module/:action', authenticateJWT, async (req, res) => {
  const { module, action } = req.params as { module: string; action: string };
  const payload = req.body;

  if (!MODULE_MAP[module]) {
    logRequest(module, action, 'error', 'Unknown module');
    const response: ApiResponse = { status: 'error', timestamp: new Date().toISOString(), message: 'Unknown module' };
    return res.status(400).json(response);
  }

  const targetUrlBase = MODULE_MAP[module];
  const targetUrl = `${targetUrlBase.replace(/\/$/, '')}/${action}`;

  try {
    const requests = Array.isArray(payload)
      ? payload.map((p) => axios.post(targetUrl, p))
      : [axios.post(targetUrl, payload)];

    const responses = await Promise.all(requests);
    const data = responses.length === 1 ? responses[0].data : responses.map((r) => r.data);

    logRequest(module, action, 'success');
    const response: ApiResponse = { status: 'success', timestamp: new Date().toISOString(), data };
    return res.json(response);
  } catch (err: any) {
    const message = err?.response?.data?.message || err?.message || 'Upstream request failed';
    logRequest(module, action, 'error', message);
    const response: ApiResponse = { status: 'error', timestamp: new Date().toISOString(), message };
    const statusCode = err?.response?.status && Number.isInteger(err.response.status) ? err.response.status : 500;
    return res.status(statusCode).json(response);
  }
});

const PORT = Number(process.env.PORT) || 4000;
app.listen(PORT, () => console.log(`Unified API Gateway running on port ${PORT}`));
