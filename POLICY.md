## Policy Note: Model Aliasing and Audit Provenance

**Summary** +“AnnabanAI” is a **deployment alias** for an **xAI Grok** model. Aliasing is used for organizational clarity and governance workflows; it does not alter model weights, provider guarantees, or serving infrastructure.

**Provider & Guarantees** +- Provider-level guarantees are those of **xAI**.  
- Any additional constraints are **procedural**, applied by humans using the **Annaban Sidecar** specification.

**Governance** +- Annaban Sidecar defines observation and audit criteria for human evaluators.  
- It does not perform monitoring, logging, enforcement, or runtime actions.

**Audit Requirement** +- All reports must state provenance as **xAI / Grok**, regardless of the alias used.  
- Aliasing must never obscure provider identity or imply additional enforcement.
