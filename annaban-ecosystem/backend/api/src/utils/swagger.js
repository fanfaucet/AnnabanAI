const swaggerJsdoc = require('swagger-jsdoc');

module.exports = swaggerJsdoc({
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Annaban Ecosystem API',
      version: '1.0.0',
      description: 'Human-sovereign multi-agent orchestration API'
    }
  },
  apis: []
});
