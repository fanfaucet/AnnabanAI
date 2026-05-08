const crypto = require('crypto');
const express = require('express');
const auth = require('../middleware/auth');
const python = require('../services/pythonClient');
const { db, addDecision, addAudit } = require('../services/state');

const router = express.Router();

router.get('/', auth, (_, res) => res.json(db.decisions.slice(0, 100)));

router.post('/recommend', auth, async (req, res) => {
  try {
    const context = { sensors: db.sensorEvents.slice(0, 20), prompt: req.body.prompt || 'Optimize safely' };
    const [orchestration, simulation, reasoning] = await Promise.all([
      python.orchestrate(context),
      python.simulate(context),
      python.reason(context)
    ]);

    const combined = {
      ...orchestration,
      simulation,
      reasoning
    };

    const decisionHash = crypto.createHash('sha256').update(JSON.stringify(combined)).digest('hex');
    const decision = addDecision({ ...combined, decisionHash, requires_human: true });
    addAudit({ type: 'decision_recommended', decisionId: decision.id, decisionHash });
    return res.status(201).json(decision);
  } catch (error) {
    return res.status(502).json({ error: 'orchestration services unavailable', detail: error.message });
  }
});

module.exports = router;
