const express = require('express');
const auth = require('../middleware/auth');
const { db, addSensorEvent } = require('../services/state');

const router = express.Router();

router.get('/', auth, (_, res) => res.json(db.sensorEvents.slice(0, 100)));
router.post('/ingest', auth, (req, res) => {
  const normalized = {
    source: req.body.source || 'simulated',
    metric: req.body.metric,
    value: Number(req.body.value),
    unit: req.body.unit || 'n/a',
    location: req.body.location || 'unknown'
  };
  const event = addSensorEvent(normalized);
  res.status(201).json(event);
});

module.exports = router;
