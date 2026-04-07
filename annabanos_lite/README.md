# AnnabanOS-Lite

AnnabanOS-Lite is a ready-to-run simulation scaffold for a customizable operating environment. It keeps kernel services stable while letting users extend workflows, interface components, and AI-assisted utilities through pluggable modules.

## Architecture

```text
annabanos_lite/
  kernel/      # Core services: config, persistence, scheduler, monitor, module sandbox
  modules/     # User-extensible modules
  interface/   # CLI and minimal Tk GUI entry points
  config/      # Per-user personalization JSON
  data/        # Persistent state, logs, snapshots
  tests/       # Unit tests for kernel + module behavior
```

### Kernel/Core Guarantees
- **Modular kernel:** File, task, config, monitoring, and module-management services are isolated inside `kernel/`.
- **Sandboxing:** Module exceptions are contained and converted into `sandboxed` results instead of crashing the kernel.
- **Persistence:** Logs, snapshots, and per-module state are stored in JSON under `data/`.
- **Personalization:** User profiles define themes, shortcuts, enabled modules, and AI behavior.

## Running the simulation

### CLI
```bash
python -m annabanos_lite.interface.cli boot --user default
python -m annabanos_lite.interface.cli cycle --user default
python -m annabanos_lite.interface.cli notify --user default --message "Stretch and hydrate"
python -m annabanos_lite.interface.cli status --user default
```

### GUI
```bash
python -m annabanos_lite.interface.gui
```

## Included example modules

### 1. `notifications`
Stores notifications and reminders in persistent module state.

### 2. `ai_suggestions`
Provides a scaffold for AI-assisted suggestions using personalization settings such as tone and automation level.

## Adding new modules safely
1. Create a class in `annabanos_lite/modules/` that subclasses `ModuleBase`.
2. Implement `on_load()` and optionally `on_tick()` / `on_event()`.
3. Keep module state JSON-serializable so it can be persisted safely.
4. Use only the `ModuleContext` capabilities (`config`, `emit_event`, `logger`, `storage_path`) instead of importing kernel internals directly.
5. Register the module in `AnnabanOSLite._register_builtin_modules()` or add a discovery layer later.
6. Add the module identifier to a user's `enabled_modules` config entry.
7. Add or update tests in `annabanos_lite/tests/` to verify failure isolation and expected behavior.

## Suggested next extensions
- Multi-profile authentication and session switching
- Richer automation hooks inspired by AnnabanAI workflow orchestration
- Web-based GUI or dashboard replacement modules
- Capability-based permissions for tighter module sandboxing
