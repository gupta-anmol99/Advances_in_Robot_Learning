from enum import IntEnum
from time import sleep
from typing import ContextManager

from RPi import GPIO  # pyright: reportMissingModuleSource=false
from smbus2 import SMBus


class Direction(IntEnum):
    """Direction of motor rotation."""

    CW = 1
    CCW = 2


class Encoder:
    def __init__(self, pwr_pin: int, bus: SMBus, addr: int = 0x36):
        self._pwr_pin = pwr_pin
        self._bus = bus
        self._addr = addr
        self._enabled = False

        GPIO.setup(pwr_pin, GPIO.OUTPUT)
        GPIO.output(pwr_pin, GPIO.LOW)

    @property
    def angle(self) -> float:
        theta1 = self._bus.read_byte_data(self._addr, 0x0E)
        theta2 = self._bus.read_byte_data(self._addr, 0x0F)
        return (theta1 << 8) + theta2

    @property
    def is_enabled(self) -> float:
        return self._enabled

    def enable(self) -> None:
        if self._enabled is not True:
            GPIO.output(self._pwr_pin, GPIO.HIGH)

        self._enabled = True

    def disable(self) -> None:
        if self._enabled is not False:
            GPIO.output(self._pwr_pin, GPIO.LOW)

        self._enabled = False


class _EncoderManagerContext(ContextManager[Encoder]):
    def __init__(self, encoders: list[Encoder], index: int):
        self._encoders = encoders
        self._index = index

    def __enter__(self) -> Encoder:
        for encoder in self._encoders:
            encoder.disable()

        self._encoders[self._index].enable()

        return self._encoders[self._index]

    def __exit__(self):
        pass


class EncoderManager:
    def __init__(self, *encoders: Encoder):
        self._encoders = list(encoders)

    def enable(self, index: int) -> _EncoderManagerContext:
        return _EncoderManagerContext(self._encoders, index)


def _step_motor(pin: int, *, delay: float = 0.0025) -> None:
    GPIO.output(pin, GPIO.HIGH)
    sleep(delay)

    GPIO.output(pin, GPIO.LOW)
    sleep(delay)


class Stepper:
    """Representation of a stepper motor with associated position information.

    Args:
        step_pin: The pin to use for sending step signals
        dir_pin: The pin to use to for selecting direction
        enc: The encoder tracking the position of the motor shaft
        dir: The initial direction of rotation
        tol: Angle tolerance while moving
    """

    def __init__(
        self,
        step_pin: int,
        dir_pin: int,
        enc: Encoder,
        dir: Direction = Direction.CW,
        tol: float = 0.1,
    ):
        self._step_pin = step_pin
        self._dir_pin = dir_pin
        self._enc = enc
        self._dir = dir
        self._offset = 0.0
        self._tol = abs(tol)

        GPIO.setup(step_pin, GPIO.OUTPUT)
        GPIO.setup(dir_pin, GPIO.OUTPUT)

    @property
    def angle(self) -> float:
        return self._enc.angle - self._offset

    @angle.setter
    def angle(self, value: float) -> None:
        self._enc.enable()

        if self.angle < value:
            self.direction = Direction.CW
        else:
            self.direction = Direction.CCW

        while abs(self.angle - value) > self._tol:
            _step_motor(self._step_pin)

        self._enc.disable()

    @property
    def direction(self) -> Direction:
        return self._dir

    @direction.setter
    def direction(self, value: Direction) -> None:
        if self._dir is not value:
            GPIO.output(self._dir_pin, GPIO.HIGH if value is Direction.CW else GPIO.LOW)

        self._dir = value

    @property
    def zero(self) -> float:
        return self._offset

    @zero.setter
    def zero(self, value: float) -> None:
        self._offset = value
