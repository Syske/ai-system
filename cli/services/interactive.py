"""Unified interactive-command state machine.

Commands that collect several inputs interactively (e.g. skill-launch:
pick skills → pick agent → enter task → confirm) implement the
InteractiveCommand protocol. A single driver runs the declared step
sequence and gives every step a uniform BACK behavior:

- A step handler returns:
  - ("done", result)  → command finished with a result
  - "back"            → roll back to the previous step
  - "quit"            → abandon the command (caller decides)
  - None              → stay/abort the command
- The driver loops; BACK at the first step propagates "quit" so the
  caller (e.g. the wizard) can re-select or exit — it never hard-exits
  mid-command.

New interactive commands subclass InteractiveCommand and declare
`steps` (list of callables). This keeps the BACK/rollback/quit contract
uniform across commands.
"""

from cli.utils.menu import BACK

NEXT = "next"
BACK_ = "back"
QUIT = "quit"


class InteractiveCommand:

    # Subclasses set this: ordered list of step callables.
    # Each step: def step(self, state) -> "next" | "back" | "quit" | ("done", result)
    steps = []

    def __init__(self, wizard):

        self.wizard = wizard

        self.state = {}

    def run(self):
        """Execute the declared steps with uniform BACK rollback.

        Returns the ("done", result) payload, or None when the command was
        abandoned (quit) — the caller decides what to do (e.g. re-pick).
        """

        step_index = 0

        while True:

            if step_index < 0:

                return None

            if step_index >= len(self.steps):

                return None

            handler = self.steps[step_index]

            outcome = handler(self)

            if outcome is None:

                return None

            if isinstance(outcome, tuple) and outcome[0] == "done":

                return outcome[1:]

            if outcome == BACK_:

                step_index -= 1

            elif outcome == QUIT:

                return None

            elif outcome == NEXT:

                step_index += 1

            else:

                return None
