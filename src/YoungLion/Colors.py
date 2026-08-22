"""YoungLion.Colors — dependency-free ANSI terminal color and styling utilities.

Overview
--------
This module provides the :class:`Colors` namespace used throughout YoungLion for
portable terminal presentation.  It exposes the traditional ANSI style constants
expected by small scripts while also supporting true-color RGB sequences,
ANSI-256 foreground/background colors, safe stripping, style composition and
text gradients.

The API is deliberately dependency-free.  It does not install terminal drivers,
change global output streams, or require a rendering framework.  Callers decide
whether to emit the returned escape sequences and can use :meth:`Colors.strip`
when plain text is required for logs, files, tests, or non-ANSI terminals.

Typical uses
------------
* Add readable severity or status coloring to command-line applications.
* Generate 24-bit foreground/background colors from application theme values.
* Remove ANSI control sequences before persisting console output.
* Build compact gradients or combine multiple ANSI styles without dependencies.

Example
-------
    from YoungLion import Colors

    label = Colors.wrap("READY", Colors.BRIGHT_GREEN, Colors.BOLD)
    print(label)
    assert Colors.strip(label) == "READY"

Notes
-----
All helpers return strings and do not print by themselves.  Terminal capability
checking belongs to the caller or to :class:`YoungLion.Terminal` when automatic
presentation decisions are required.
"""
from __future__ import annotations

import re
from typing import Iterable, Tuple

_ANSI_RE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\))")


class Colors:
    """ANSI styling namespace.
    
    Overview
    --------
    ``Colors`` provides classic ANSI constants, true-color, ANSI-256, stripping, wrapping and gradients.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use to construct style sequences; pair with Terminal.supports_color when capability detection is required.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    rgb, bg_rgb, ansi256, bg_ansi256, strip, wrap, foreground, background, gradient.
    
    Example::
    
        status = Colors.wrap("SUCCESS", Colors.BRIGHT_GREEN, Colors.BOLD)
        print(status)
        print(Colors.strip(status))
    """
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
        """Return an ANSI true-color foreground escape sequence for the supplied RGB channels.
        
        Details
        -------
        This method belongs to :class:`Colors` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        r : int
            Red channel 0..255.
        g : int
            Green channel 0..255.
        b : int
            Second string/value.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        return f"\033[38;2;{cls._channel(r)};{cls._channel(g)};{cls._channel(b)}m"

    @classmethod
    def bg_rgb(cls, r: int, g: int, b: int) -> str:
        """Return an ANSI true-color background escape sequence for the supplied RGB channels.
        
        Details
        -------
        This method belongs to :class:`Colors` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        r : int
            Red channel 0..255.
        g : int
            Green channel 0..255.
        b : int
            Second string/value.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        return f"\033[48;2;{cls._channel(r)};{cls._channel(g)};{cls._channel(b)}m"

    @staticmethod
    def ansi256(index: int) -> str:
        """Return an ANSI-256 foreground escape sequence.
        
        Details
        -------
        This method belongs to :class:`Colors` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        index : int
            Value supplied for ``index`` according to the Colors contract.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        index = int(index)
        if not 0 <= index <= 255:
            raise ValueError("ANSI-256 index must be between 0 and 255")
        return f"\033[38;5;{index}m"

    @staticmethod
    def bg_ansi256(index: int) -> str:
        """Return an ANSI-256 background escape sequence.
        
        Details
        -------
        This method belongs to :class:`Colors` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        index : int
            Value supplied for ``index`` according to the Colors contract.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        index = int(index)
        if not 0 <= index <= 255:
            raise ValueError("ANSI-256 index must be between 0 and 255")
        return f"\033[48;5;{index}m"

    @staticmethod
    def strip(text: object) -> str:
        """Remove ANSI control sequences from text.
        
        Details
        -------
        This method belongs to :class:`Colors` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : object
            Text/content input.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        return _ANSI_RE.sub("", str(text))

    @classmethod
    def wrap(cls, text: object, *styles: str, reset: bool = True) -> str:
        """Wrap text in one or more ANSI style sequences and optionally append reset.
        
        Details
        -------
        This method belongs to :class:`Colors` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : object
            Text/content input.
        *styles : str
            Value supplied for ``styles`` according to the Colors contract.
        reset : bool (default: ``True``)
            Value supplied for ``reset`` according to the Colors contract.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        prefix = "".join(str(style) for style in styles)
        return f"{prefix}{text}{cls.RESET if reset and prefix else ''}"

    @classmethod
    def foreground(cls, rgb: Tuple[int, int, int], text: object) -> str:
        """Apply an RGB foreground color to text.
        
        Details
        -------
        This method belongs to :class:`Colors` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        rgb : Tuple[int, int, int]
            Value supplied for ``rgb`` according to the Colors contract.
        text : object
            Text/content input.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        return cls.wrap(text, cls.rgb(*rgb))

    @classmethod
    def background(cls, rgb: Tuple[int, int, int], text: object) -> str:
        """Apply an RGB background color to text.
        
        Details
        -------
        This method belongs to :class:`Colors` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        rgb : Tuple[int, int, int]
            Value supplied for ``rgb`` according to the Colors contract.
        text : object
            Text/content input.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        return cls.wrap(text, cls.bg_rgb(*rgb))

    @classmethod
    def gradient(cls, text: str, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> str:
        """Apply a linear RGB foreground gradient across the characters of a string.
        
        Details
        -------
        This method belongs to :class:`Colors` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : str
            Text/content input.
        start : Tuple[int, int, int]
            Whether the stopwatch starts immediately or remains stopped initially.
        end : Tuple[int, int, int]
            Value supplied for ``end`` according to the Colors contract.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
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
