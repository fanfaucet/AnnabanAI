# AnnabanAI React Boot API Simulation

**Authored under Jacob Wayne Kinnaird.** This is a local React/Vite demonstration of a generic model-service boot lifecycle. It is not OpenAI source code, does not reproduce a private OpenAI API, and does not call OpenAI or perform model inference.

## Run locally

Requirements: Node.js 18+ and npm.

```bash
cd demos/react-boot-api-simulation
npm install
npm run dev
```

To verify a production build:

```bash
npm run build
npm run preview
```

## Simulated sequence

1. Runtime initialized
2. Advisory policy loaded
3. Mock transport handshake
4. Session configuration
5. Ready for input

The UI exposes model profile, environment, human-gate state, and a session trace. State transitions are local and illustrative. The event list exists only in page memory; it is not a durable or tamper-evident audit log.

## Safety and scope

- External effects: **0**
- Network/provider calls: **none**
- Credentials or API keys: **not read**
- Authorization: a UI configuration flag only, not real identity verification or a security boundary
- Human authorization: represented as a design requirement, not connected to any real action executor

This demo illustrates the governance principle: **AI recommends. Humans decide. Everything is logged.** The current trace is ephemeral, so “logged” means visible in this browser session only.

## Attribution and status

Project attribution supplied by the user: Jacob Wayne Kinnaird. This is a simulation artifact; the commit does not establish deployment, ownership beyond repository access, independent verification, or integration with OpenAI systems.
