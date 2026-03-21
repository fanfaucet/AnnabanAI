import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:4000';

export function client(token) {
  return axios.create({
    baseURL: API_BASE,
    headers: { Authorization: `Bearer ${token}` }
  });
}

export async function login() {
  const { data } = await axios.post(`${API_BASE}/auth/login`, { username: 'admin', password: 'admin123' });
  return data.token;
}
