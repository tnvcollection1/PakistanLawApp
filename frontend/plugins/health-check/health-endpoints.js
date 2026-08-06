const express = require('express');
const router = express.Router();

router.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

router.get('/health/db', (req, res) => {
  // Check database connectivity
  const db = req.app.locals.db;
  if (db) {
    res.json({ status: 'ok', service: 'database' });
  } else {
    res.status(503).json({ status: 'error', service: 'database' });
  }
});

router.get('/health/external', async (req, res) => {
  // Check external API connectivity
  try {
    const response = await fetch(process.env.EXTERNAL_API_URL + '/health');
    if (response.ok) {
      res.json({ status: 'ok', service: 'external_api' });
    } else {
      res.status(503).json({ status: 'error', service: 'external_api' });
    }
  } catch (e) {
    res.status(503).json({ status: 'error', service: 'external_api', message: e.message });
  }
});

module.exports = router;
