"""Stepper motor control module.

This module defines several classes to enable precise angular control of a NEMA17 stepper motor
using A4988 stepper motor driver and the AS5600 rotational encoder.

Examples:
    >>> stepper = Stepper(10, 11)
    >>> mux = EncoderMultiplexer(0, 1, 2)
    >>> with mux.enable(0) as enc:
            stepper.to_angle(enc, 100.0)

"""

from __future__ import annotations

from enum import IntEnum
from time import sleep
from typing import ContextManager
from types import TracebackType
from warnings import warn

from RPi import GPIO  # pyright: reportMissingModuleSource=false
from smbus2 import SMBus


class Direction(IntEnum):
    """Direction of motor rotation."""

    CW = 1
    CCW = 2


class Encoder:
    """An encoder to detect the angle of a stepper motor shaft.

    This implementation uses the AS5600 positional encoder to detect the angle of the motor shaft.
    It communicates using the I2C bus and has a fixed address, which requires a multiplexer in
    order to support multiple sensors.

    Args:
        idx: The port on the I2C multiplexer
        mux: The I2C multiplexer
        addr: The address of the encoder on the I2C bus
    """

    def __init__(self, idx: int, mux: EncoderMultiplexer, addr: int = 0x36):
        self._idx = idx
        self._mux = mux
        self._addr = addr

    @property
    def angle(self) -> float:
        """The angle of the motor shaft detected by the encoder."""

        theta1 = self._mux.bus.read_byte_data(self._addr, 0x0E)
        theta2 = self._mux.bus.read_byte_data(self._addr, 0x0F)
        raw_angle = (theta1 << 8) + theta2
        offset_angle = raw_angle - self.zero

        return offset_angle % 360  # Ensure angle is constrained [0, 360]

    @property
    def zero(self) -> float:
        """The zero angle of the encoder."""

        return self._mux.offsets[self._idx]

    @zero.setter
    def zero(self, offset: float) -> None:
        self._mux.offsets[self._idx] = offset


class _EncoderContext(ContextManager[Encoder]):
    """Context manager for an encoder.

    This class is responsible for enabling the selected port on a I2C multiplexer circuit. This
    operation is defined as a context manager so that selection does not occur until the context
    is entered.

    Args:
        mux: The I2C multiplexer
        port: The multiplexer port to enable
    """

    def __init__(self, mux: EncoderMultiplexer, port: int):
        self._mux = mux
        self._port = port

    def __enter__(self) -> Encoder:
        pin0 = self._port & 0x100
        pin1 = self._port & 0x010
        pin2 = self._port & 0x001

        GPIO.output(self._mux._pin0, GPIO.HIGH if pin0 > 0 else GPIO.LOW)
        GPIO.output(self._mux._pin1, GPIO.HIGH if pin1 > 0 else GPIO.LOW)
        GPIO.output(self._mux._pin2, GPIO.HIGH if pin2 > 0 else GPIO.LOW)

        return Encoder(self._port, self._mux)

    def __exit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        return None


class EncoderMultiplexer:
    """A multiplexer for managing multiple AS5600 encoders on a single I2C bus.

    This multiplexer is capable of selecting between 8 different encoders.

    Args:
        mux_pin0: The first multiplexer selector pin
        mux_pin1: The second multiplexer selector pin
        mux_pin2: The third multiplexer selector pin
        bus: The I2C bus device path

    """

    def __init__(self, mux_pin0: int, mux_pin1: int, mux_pin2: int, bus: str = "/dev/i2c-1"):
        GPIO.setup(mux_pin0, GPIO.OUTPUT)
        GPIO.setup(mux_pin1, GPIO.OUTPUT)
        GPIO.setup(mux_pin2, GPIO.OUTPUT)

        GPIO.output(mux_pin0, GPIO.LOW)
        GPIO.output(mux_pin1, GPIO.LOW)
        GPIO.output(mux_pin2, GPIO.LOW)

        self._pin0 = mux_pin0
        self._pin1 = mux_pin1
        self._pin2 = mux_pin2
        self._bus = SMBus(bus)
        self._offsets = [0.0] * 8

    @property
    def bus(self) -> SMBus:
        return self._bus

    @property
    def offsets(self) -> list[float]:
        return self._offsets

    def select(self, port: int) -> _EncoderContext:
        return _EncoderContext(self, port)


class Stepper:
    """Representation of a stepper motor with associated position information.

    Args:
        step_pin: The pin to use for sending step signals
        dir_pin: The pin to use to for selecting direction
        dir: The initial direction of rotation
    """

    def __init__(
        self,
        step_pin: int,
        dir_pin: int,
        dir: Direction = Direction.CW,
    ):
        self._step_pin = step_pin
        self._dir_pin = dir_pin
        self._dir = dir
        self._offset = 0.0

        GPIO.setup(step_pin, GPIO.OUTPUT)
        GPIO.setup(dir_pin, GPIO.OUTPUT)

    def step(self, *, delay: float = 0.0025) -> None:
        """Move the stepper motor shaft one step.

        The direction of movement is controlled by setting the direction property on the motor.

        Args:
            delay: How long to wait before changing pin states
        """

        pin_states = [GPIO.HIGH, GPIO.LOW]

        for pin_state in pin_states:
            GPIO.output(self._step_pin, pin_state)
            sleep(delay)

    @property
    def direction(self) -> Direction:
        """The direction of movement for the motor."""

        return self._dir

    @direction.setter
    def direction(self, value: Direction) -> None:
        if self._dir is not value:
            GPIO.output(self._dir_pin, GPIO.HIGH if value is Direction.CW else GPIO.LOW)

        self._dir = value

    def to_angle(self, enc: Encoder, angle: float, *, tol: float = 1.8) -> None:
        """Set the stepper motor to a given angle.

        Args:
            enc: The encoder measuring the angle of the motor shaft
            angle: The target shaft angle
            tol: The maximum difference between the target angle and the actual angle
        """

        tol = abs(tol)

        if enc.angle < angle:
            self.direction = Direction.CW
        else:
            self.direction = Direction.CCW

        last_angle = enc.angle
        self.step()

        if enc.angle == last_angle:
            warn("Encoder angle did not change after step, you may have the wrong encoder selected")

        while abs(enc.angle - angle) > tol:
            self.step()


__all__ = ["Encoder", "EncoderMultiplexer", "Stepper"]
