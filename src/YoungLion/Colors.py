"""Dependency-free ANSI styling utilities.

The historical constant names are preserved while v0.1 adds RGB/256-color
helpers and safe wrapping/stripping utilities for application terminals.
"""
from __future__ import annotations

import re
from typing import Iterable, Tuple

_ANSI_RE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\))")


class Colors:
    RESET = "\033[0m"; BRIGHT = "\033[1m"; DIM = "\033[2m"; ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"; BLINK = "\033[5m"; REVERSE = "\033[7m"; HIDDEN = "\033[8m"; STRIKETHROUGH = "\033[9m"
    BLACK = "\033[30m"; RED = "\033[31m"; GREEN = "\033[32m"; YELLOW = "\033[33m"; BLUE = "\033[34m"; MAGENTA = "\033[35m"; CYAN = "\033[36m"; WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"; BRIGHT_RED = "\033[91m"; BRIGHT_GREEN = "\033[92m"; BRIGHT_YELLOW = "\033[93m"; BRIGHT_BLUE = "\033[94m"; BRIGHT_MAGENTA = "\033[95m"; BRIGHT_CYAN = "\033[96m"; BRIGHT_WHITE = "\033[97m"
    BG_BLACK = "\033[40m"; BG_RED = "\033[41m"; BG_GREEN = "\033[42m"; BG_YELLOW = "\033[43m"; BG_BLUE = "\033[44m"; BG_MAGENTA = "\033[45m"; BG_CYAN = "\033[46m"; BG_WHITE = "\033[47m"
    BG_BRIGHT_BLACK = "\033[100m"; BG_BRIGHT_RED = "\033[101m"; BG_BRIGHT_GREEN = "\033[102m"; BG_BRIGHT_YELLOW = "\033[103m"; BG_BRIGHT_BLUE = "\033[104m"; BG_BRIGHT_MAGENTA = "\033[105m"; BG_BRIGHT_CYAN = "\033[106m"; BG_BRIGHT_WHITE = "\033[107m"

    @staticmethod
    def _channel(value: int) -> int:
        value = int(value)
        if not 0 <= value <= 255:
            raise ValueError("RGB channels must be between 0 and 255")
        return value

    @classmethod
    def rgb(cls, r: int, g: int, b: int) -> str:
        """24-bit foreground escape sequence."""
        return f"\033[38;2;{cls._channel(r)};{cls._channel(g)};{cls._channel(b)}m"

    @classmethod
    def bg_rgb(cls, r: int, g: int, b: int) -> str:
        """24-bit background escape sequence."""
        return f"\033[48;2;{cls._channel(r)};{cls._channel(g)};{cls._channel(b)}m"

    @staticmethod
    def ansi256(index: int) -> str:
        index = int(index)
        if not 0 <= index <= 255:
            raise ValueError("ANSI-256 index must be between 0 and 255")
        return f"\033[38;5;{index}m"

    @staticmethod
    def bg_ansi256(index: int) -> str:
        index = int(index)
        if not 0 <= index <= 255:
            raise ValueError("ANSI-256 index must be between 0 and 255")
        return f"\033[48;5;{index}m"

    @staticmethod
    def strip(text: object) -> str:
        return _ANSI_RE.sub("", str(text))

    @classmethod
    def wrap(cls, text: object, *styles: str, reset: bool = True) -> str:
        prefix = "".join(str(style) for style in styles)
        return f"{prefix}{text}{cls.RESET if reset and prefix else ''}"

    @classmethod
    def foreground(cls, rgb: Tuple[int, int, int], text: object) -> str:
        return cls.wrap(text, cls.rgb(*rgb))

    @classmethod
    def background(cls, rgb: Tuple[int, int, int], text: object) -> str:
        return cls.wrap(text, cls.bg_rgb(*rgb))

    @classmethod
    def gradient(cls, text: str, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> str:
        """Return a simple per-character true-color gradient."""
        if not text:
            return ""
        sr, sg, sb = map(cls._channel, start)
        er, eg, eb = map(cls._channel, end)
        denominator = max(1, len(text) - 1)
        out = []
        for i, char in enumerate(text):
            t = i / denominator
            r = round(sr + (er - sr) * t); g = round(sg + (eg - sg) * t); b = round(sb + (eb - sb) * t)
            out.append(f"{cls.rgb(r, g, b)}{char}")
        out.append(cls.RESET)
        return "".join(out)


__all__ = ["Colors"]
