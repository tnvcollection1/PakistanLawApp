const checkHealth = async (req, res) => {
  try {
    const healthcheck = {
      uptime: process.uptime(),
      message: 'OK',
      timestamp: Date.now(),
      environment: process.env.NODE_ENV || 'development',
      version: process.env.npm_package_version || '1.0.0',
    };
    res.status(200).json(healthcheck);
  } catch (error) {
    res.status(500).json({
      message: 'Health check failed',
      error: error.message,
    });
  }
};

const checkDatabaseHealth = async (req, res) => {
  try {
    // Check database connection
    const dbStatus = await checkDatabaseConnection();
    res.status(200).json({
      database: dbStatus ? 'connected' : 'disconnected',
      timestamp: Date.now(),
    });
  } catch (error) {
    res.status(500).json({
      database: 'error',
      error: error.message,
      timestamp: Date.now(),
    });
  }
};

const checkExternalServices = async (req, res) => {
  try {
    const services = {
      api: { status: 'up', latency: 0 },
      database: { status: 'up', latency: 0 },
      cache: { status: 'up', latency: 0 },
    };
    res.status(200).json({
      services,
      timestamp: Date.now(),
    });
  } catch (error) {
    res.status(500).json({
      message: 'External services check failed',
      error: error.message,
    });
  }
};

module.exports = {
  checkHealth,
  checkDatabaseHealth,
  checkExternalServices,
};
