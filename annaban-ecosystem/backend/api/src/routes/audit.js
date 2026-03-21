const express = require('express');
const auth = require('../middleware/auth');
const { db } = require('../services/state');

const router = express.Router();
router.get('/', auth, (_, res) => res.json(db.audit.slice(0, 200)));

module.exports = router;
