const axios = require('axios');

async function callService(baseUrl, path, body) {
  const url = `${baseUrl}${path}`;
  const { data } = await axios.post(url, body, { timeout: 15000 });
  return data;
}

module.exports = {
  orchestrate(payload) {
    return callService(process.env.PY_AI_URL, '/orchestrate', payload);
  },
  simulate(payload) {
    return callService(process.env.PY_AETHER_URL, '/simulate', payload);
  },
  reason(payload) {
    return callService(process.env.PY_ORACLE_URL, '/reason', payload);
  }
};
