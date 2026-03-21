const express = require('express');
const auth = require('../middleware/auth');
const { resolveDecision, addAudit } = require('../services/state');
const { mintDecisionNFT } = require('../services/blockchain');

const router = express.Router();

async function processDecision(req, res, status) {
  const decision = resolveDecision(req.params.id, status, req.user.sub);
  if (!decision) return res.status(404).json({ error: 'decision not found' });
  addAudit({ type: 'decision_reviewed', decisionId: decision.id, status, reviewer: req.user.sub });

  let chain = { skipped: true };
  if (status === 'approved') {
    chain = await mintDecisionNFT({
      decisionHash: decision.decisionHash,
      confidence: decision.confidence,
      ethicalScore: decision.ethical_score
    });
    addAudit({ type: 'decision_minted', decisionId: decision.id, ...chain });
  }

  return res.json({ decision, blockchain: chain });
}

router.post('/:id/approve', auth, (req, res) => processDecision(req, res, 'approved'));
router.post('/:id/reject', auth, (req, res) => processDecision(req, res, 'rejected'));

module.exports = router;
