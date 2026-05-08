const express = require('express');
const jwt = require('jsonwebtoken');

const router = express.Router();
const users = [
  { username: 'admin', password: 'admin123', role: 'governor' },
  { username: 'operator', password: 'operator123', role: 'operator' }
];

router.post('/login', (req, res) => {
  const { username, password } = req.body;
  const user = users.find((u) => u.username === username && u.password === password);
  if (!user) return res.status(401).json({ error: 'invalid credentials' });
  const token = jwt.sign({ sub: user.username, role: user.role }, process.env.JWT_SECRET || 'change_me', { expiresIn: '12h' });
  return res.json({ token, role: user.role });
});

module.exports = router;
