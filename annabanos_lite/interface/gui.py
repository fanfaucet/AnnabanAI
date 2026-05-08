from __future__ import annotations

from dataclasses import asdict
import json
import tkinter as tk
from tkinter import ttk

from annabanos_lite.kernel.os import AnnabanOSLite


class AnnabanOSLiteGUI:
    def __init__(self) -> None:
        self.os_app = AnnabanOSLite()
        self.root = tk.Tk()
        self.root.title("AnnabanOS-Lite")
        self.root.geometry("640x420")
        self.theme = self.os_app.config_manager.load_user_config("default").get("theme", "aurora")
        self.root.configure(bg="#10141f")
        self.output = tk.Text(self.root, wrap="word", bg="#0f172a", fg="#dbeafe")
        self.output.pack(fill="both", expand=True, padx=12, pady=12)

        controls = ttk.Frame(self.root)
        controls.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(controls, text="Boot", command=self.boot).pack(side="left", padx=4)
        ttk.Button(controls, text="Run Cycle", command=self.run_cycle).pack(side="left", padx=4)
        ttk.Button(controls, text="Notify", command=self.notify).pack(side="left", padx=4)

    def _render(self, payload) -> None:
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, json.dumps(payload, indent=2))

    def boot(self) -> None:
        self._render({"theme": self.theme, **self.os_app.boot()})

    def run_cycle(self) -> None:
        self._render(self.os_app.run_cycle())

    def notify(self) -> None:
        records = [asdict(r) for r in self.os_app.trigger_event("notify", {"message": "GUI reminder"})]
        self._render(records)

    def launch(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    AnnabanOSLiteGUI().launch()
