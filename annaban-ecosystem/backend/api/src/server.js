require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const swaggerUi = require('swagger-ui-express');
const swaggerSpec = require('./utils/swagger');
const authRoutes = require('./routes/auth');
const sensorRoutes = require('./routes/sensors');
const decisionRoutes = require('./routes/decisions');
const governanceRoutes = require('./routes/governance');
const auditRoutes = require('./routes/audit');

const app = express();
app.use(cors());
app.use(helmet());
app.use(express.json());

app.get('/health', (_, res) => res.json({ status: 'ok', service: 'annaban-api' }));
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

app.use('/auth', authRoutes);
app.use('/sensors', sensorRoutes);
app.use('/decisions', decisionRoutes);
app.use('/governance', governanceRoutes);
app.use('/audit', auditRoutes);

const port = process.env.PORT || 4000;
app.listen(port, () => {
  console.log(`Annaban API listening on ${port}`);
});
