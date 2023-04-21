from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Header, Static, Button
from server import stepper

mpx = stepper.EncoderMultiplexer(11, 13, 15)
elev_stepper = stepper.Stepper(step_pin=35, dir_pin=37, enc_multiplexer=mpx, enc_idx=0)
base_stepper = stepper.Stepper(step_pin=38, dir_pin=40, enc_multiplexer=mpx, enc_idx=1)


class BaseStepper(Static):
    """Base stepper control widget"""

    angle = reactive(0.0)

    def compose(self) -> ComposeResult:
        yield Button("Left")
        yield Static(f"{self.angle} °")
        yield Button("Right")


class ElevStepper(Static):
    """Elevation stepper control widget"""

    angle = reactive(0.0)

    def compose(self) -> ComposeResult:
        yield Button("Up")
        yield Static(f"{self.angle} °")
        yield Button("Down")


class StepperCtrl(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield BaseStepper()
        yield ElevStepper()


if __name__ == "__main__":
    app = StepperCtrl()
    app.run()
