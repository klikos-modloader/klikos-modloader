from typing import Literal, Optional, Callable, Any
from pathlib import Path
import re

from modules.filesystem import Resources

from ..basic import Frame, Entry, Label, Toplevel

import colorsys  # type: ignore
from PIL import Image, ImageTk  # type: ignore
from customtkinter import CTkCanvas, AppearanceModeTracker, ScalingTracker  # type: ignore


# region ColorValidation
class ColorValidation:
    @staticmethod
    def is_valid_hex(value_hex: str) -> bool:
        return bool(re.fullmatch(r"#([0-9a-fA-F]{6})", value_hex))

    @staticmethod
    def is_valid_hsv(value_hsv: tuple[float, float, float]) -> bool:
        if len(value_hsv) != 3: return False
        h, s, v = value_hsv
        return 0 <= h <= 1 and 0 <= s <= 1 and 0 <= v <= 1

    @staticmethod
    def is_valid_hsv_normalized(value_hsv_normalized: tuple[int, int, int]) -> bool:
        if len(value_hsv_normalized) != 3: return False
        h, s, v = value_hsv_normalized
        return 0 <= h < 360 and 0 <= s <= 100 and 0 <= v <= 100

    @staticmethod
    def is_valid_rgb(value_rgb: tuple[float, float, float]) -> bool:
        if len(value_rgb) != 3: return False
        r, g, b = value_rgb
        return 0 <= r < 1 and 0 <= g <= 1 and 0 <= b <= 1

    @staticmethod
    def is_valid_rgb_normalized(value_rgb_normalized: tuple[int, int, int]) -> bool:
        if len(value_rgb_normalized) != 3: return False
        r, g, b = value_rgb_normalized
        return 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255
# endregion


# region ColorPicker
class ColorPicker(Frame):
    value_hex: str = "#FF0000"
    value_hsv: tuple[float, float, float] = (0, 1, 1)
    value_rgb: tuple[float, float, float] = (1, 0, 0)
    on_update_callback: Optional[Callable[[str], Any]] = None

    _widget_scaling: float

    _hue_canvas: CTkCanvas
    _sv_canvas: CTkCanvas
    _preview_frame: Optional[Frame] = None

    _hue_image: Image.Image
    _hue_indicator_image: Image.Image
    _sv_foreground_image: Image.Image
    _sv_background_image: Image.Image
    _sv_mixed_image: Image.Image
    _sv_indicator_image: Image.Image

    _scaled_hue_image: Image.Image
    _scaled_hue_indicator_image: Image.Image
    _scaled_sv_foreground_image: Image.Image
    _scaled_sv_background_image: Image.Image
    _scaled_sv_mixed_image: Image.Image
    _scaled_sv_indicator_image: Image.Image

    _hue_photoimage: ImageTk.PhotoImage
    _hue_indicator_photoimage: ImageTk.PhotoImage
    _sv_photoimage: ImageTk.PhotoImage
    _sv_indicator_photoimage: ImageTk.PhotoImage

    _hue_image_tag: int
    _hue_indicator_tag: int
    _sv_image_tag: int
    _sv_indicator_tag: int

    _hex_input: Optional[Entry] = None
    _rgb_r_input: Optional[Entry] = None
    _rgb_g_input: Optional[Entry] = None
    _rgb_b_input: Optional[Entry] = None
    _hsv_h_input: Optional[Entry] = None
    _hsv_s_input: Optional[Entry] = None
    _hsv_v_input: Optional[Entry] = None


    def __init__(self, master, color_hex: Optional[str] = None, advanced: bool = False, on_update_callback: Optional[Callable[[str], Any]] = None, **kwargs) -> None:
        if "transparent" not in kwargs:
            kwargs["transparent"] = True
        super().__init__(master, **kwargs)
        self.on_update_callback = on_update_callback

        # Images
        self._hue_image = Image.open(Resources.ColorPicker.HUE)
        self._hue_indicator_image = Image.open(Resources.ColorPicker.INDICATOR_WIDE)
        self._sv_foreground_image = Image.open(Resources.ColorPicker.SATURATION_VALUE)
        self._sv_background_image = Image.new("RGBA", self._sv_foreground_image.size, self.value_hex)
        self._sv_mixed_image = Image.alpha_composite(self._sv_background_image, self._sv_foreground_image)
        self._sv_indicator_image = Image.open(Resources.ColorPicker.INDICATOR)

        self._hue_photoimage = ImageTk.PhotoImage(self._hue_image)
        self._hue_indicator_photoimage = ImageTk.PhotoImage(self._hue_indicator_image)
        self._sv_photoimage = ImageTk.PhotoImage(self._sv_mixed_image)
        self._sv_indicator_photoimage = ImageTk.PhotoImage(self._sv_indicator_image)

        # Canvas
        canvas_frame: Frame = Frame(self, transparent=True)
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid(column=0, row=0, sticky="nsew")

        # w, h = self._sv_spactrum.width(), self._sv_spectrum.height()
        w, h = 256, 256
        self._sv_canvas = CTkCanvas(canvas_frame, cursor="hand2", width=w, height=h, highlightthickness=0)
        self._sv_canvas.grid(column=0, row=0, sticky="nsew")

        # w, h = self._hue_spactrum.width(), self._hue_spectrum.height()
        w, h = 32, 256
        self._hue_canvas = CTkCanvas(canvas_frame, cursor="hand2", width=w, height=h, highlightthickness=0)
        self._hue_canvas.grid(column=1, row=0, padx=(12, 0), sticky="nsew")

        # Canvas events & bindings
        appearance_mode: int = AppearanceModeTracker.appearance_mode
        if appearance_mode == 0: self._on_appearance_change("Light")
        elif appearance_mode == 1: self._on_appearance_change("Dark")
        AppearanceModeTracker.add(self._on_appearance_change)
        ScalingTracker.add_widget(self._on_scaling_change, self)
        widget_scaling: float = ScalingTracker.get_widget_scaling(self)
        self._on_scaling_change(widget_scaling, widget_scaling)

        self._sv_canvas.bind("<ButtonPress-1>", self._on_sv_drag)
        self._sv_canvas.bind("<B1-Motion>", self._on_sv_drag)
        self._hue_canvas.bind("<B1-Motion>", self._on_hue_drag)
        self._hue_canvas.bind("<ButtonPress-1>", self._on_hue_drag)

        # Input & Preview
        control_frame: Frame = Frame(self, transparent=True)
        control_frame.grid(column=0, row=1, sticky="nsew", pady=(12, 0))

        if not advanced:
            control_frame.grid_columnconfigure(1, weight=1)

            hex_input_wrapper = Frame(control_frame, transparent=True)
            hex_input_wrapper.grid(column=0, row=0, sticky="nsew")
            Label(hex_input_wrapper, "HEX", style="body", dont_localize=True).grid(column=0, row=0)
            self._hex_input = Entry(
                hex_input_wrapper, command=self._on_hex_input, on_focus_lost="command", reset_if_empty=True, run_command_if_empty=False, width=84, height=32,
                validate="key", validatecommand=(self.register(lambda value: value == "" or (len(value.removeprefix("#")) <= 6 and all(c in "0123456789ABCDEF" for c in value.removeprefix("#").upper()))), "%P")
            )
            self._hex_input.set(self.value_hex)
            self._hex_input.grid(column=1, row=0, padx=(8, 0))

            self._preview_frame = Frame(control_frame, border=False, fg_color=self.value_hex, width=32, height=32)
            self._preview_frame.grid(column=1, row=0, sticky="ew", padx=(12, 0))

        else:
            # RGB
            r, g, b = self.value_rgb
            r = round(r * 255)
            g = round(g * 255)
            b = round(b * 255)

            rgb_input_wrapper = Frame(control_frame, transparent=True)
            rgb_input_wrapper.grid(column=0, row=0, sticky="nse")

            Label(rgb_input_wrapper, "R", style="body", dont_localize=True).grid(column=0, row=0)
            self._rgb_r_input = Entry(
                rgb_input_wrapper, command=lambda event, mode="r": self._on_rgb_input(mode, event), on_focus_lost="command", reset_if_empty=True, run_command_if_empty=False, width=48, height=32,
                validate="key", validatecommand=(self.register(lambda value: len(value) <= 3 and (value == "" or value.isdigit())), "%P")
            )
            self._rgb_r_input.set(str(r))
            self._rgb_r_input.grid(column=1, row=0, sticky="e", padx=(8, 0))

            Label(rgb_input_wrapper, "G", style="body", dont_localize=True).grid(column=0, row=1, pady=(8, 0))
            self._rgb_g_input = Entry(
                rgb_input_wrapper, command=lambda event, mode="g": self._on_rgb_input(mode, event), on_focus_lost="command", reset_if_empty=True, run_command_if_empty=False, width=48, height=32,
                validate="key", validatecommand=(self.register(lambda value: len(value) <= 3 and (value == "" or value.isdigit())), "%P")
            )
            self._rgb_g_input.set(str(r))
            self._rgb_g_input.grid(column=1, row=1, sticky="e", padx=(8, 0), pady=(8, 0))

            Label(rgb_input_wrapper, "B", style="body", dont_localize=True).grid(column=0, row=2, pady=(8, 0))
            self._rgb_b_input = Entry(
                rgb_input_wrapper, command=lambda event, mode="b": self._on_rgb_input(mode, event), on_focus_lost="command", reset_if_empty=True, run_command_if_empty=False, width=48, height=32,
                validate="key", validatecommand=(self.register(lambda value: len(value) <= 3 and (value == "" or value.isdigit())), "%P")
            )
            self._rgb_b_input.set(str(r))
            self._rgb_b_input.grid(column=1, row=2, sticky="e", padx=(8, 0), pady=(8, 0))

            # HSV
            h, s, v = self.value_hsv  # type: ignore
            h = round(h * 360)
            s = round(s * 100)
            v = round(v * 100)

            hsv_input_wrapper = Frame(control_frame, transparent=True)
            hsv_input_wrapper.grid(column=1, row=0, sticky="nse", padx=(12, 0))

            Label(hsv_input_wrapper, "H", style="body", dont_localize=True).grid(column=0, row=0)
            self._hsv_h_input = Entry(
                hsv_input_wrapper, command=lambda event, mode="h": self._on_hsv_input(mode, event), on_focus_lost="command", reset_if_empty=True, run_command_if_empty=False, width=48, height=32,
                validate="key", validatecommand=(self.register(lambda value: len(value) <= 3 and (value == "" or value.isdigit())), "%P")
            )
            self._hsv_h_input.set(str(h))
            self._hsv_h_input.grid(column=1, row=0, sticky="e", padx=(8, 0))

            Label(hsv_input_wrapper, "S", style="body", dont_localize=True).grid(column=0, row=1, pady=(8, 0))
            self._hsv_s_input = Entry(
                hsv_input_wrapper, command=lambda event, mode="s": self._on_hsv_input(mode, event), on_focus_lost="command", reset_if_empty=True, run_command_if_empty=False, width=48, height=32,
                validate="key", validatecommand=(self.register(lambda value: len(value) <= 3 and (value == "" or value.isdigit())), "%P")
            )
            self._hsv_s_input.set(str(s))
            self._hsv_s_input.grid(column=1, row=1, sticky="e", padx=(8, 0), pady=(8, 0))

            Label(hsv_input_wrapper, "V", style="body", dont_localize=True).grid(column=0, row=2, pady=(8, 0))
            self._hsv_v_input = Entry(
                hsv_input_wrapper, command=lambda event, mode="v": self._on_hsv_input(mode, event), on_focus_lost="command", reset_if_empty=True, run_command_if_empty=False, width=48, height=32,
                validate="key", validatecommand=(self.register(lambda value: len(value) <= 3 and (value == "" or value.isdigit())), "%P")
            )
            self._hsv_v_input.set(str(v))
            self._hsv_v_input.grid(column=1, row=2, sticky="e", padx=(8, 0), pady=(8, 0))

            # HEX & Preview
            control_frame.grid_columnconfigure(2, weight=1)
            hex_and_preview_wrapper = Frame(control_frame, transparent=True)
            hex_and_preview_wrapper.grid_columnconfigure(0, weight=1)
            hex_and_preview_wrapper.grid(column=2, row=0, sticky="nsew", padx=(12, 0))

            self._preview_frame = Frame(hex_and_preview_wrapper, border=False, fg_color=self.value_hex, width=32, height=32)
            self._preview_frame.grid(column=0, row=0, sticky="ew")

            hex_input_wrapper = Frame(hex_and_preview_wrapper, transparent=True)
            hex_input_wrapper.grid(column=0, row=1, sticky="nse", pady=(12, 0))
            Label(hex_input_wrapper, "HEX", style="body", dont_localize=True).grid(column=0, row=0)
            self._hex_input = Entry(
                hex_input_wrapper, command=self._on_hex_input, on_focus_lost="command", reset_if_empty=True, run_command_if_empty=False, width=84, height=32,
                validate="key", validatecommand=(self.register(lambda value: value == "" or (len(value.removeprefix("#")) <= 6 and all(c in "0123456789ABCDEF" for c in value.removeprefix("#").upper()))), "%P")
            )
            self._hex_input.set(self.value_hex)
            self._hex_input.grid(column=1, row=0, padx=(8, 0))

        # Default color
        if color_hex:
            self.set(value_hex=color_hex)


    def get_hex(self) -> str:
        return self.value_hex


    def get_hsv(self, normalized: bool = False) -> tuple[float, float, float] | tuple[int, int, int]:
        h, s, v = self.value_hsv
        if normalized:
            h = max(0, min(359, round(h * 360)))  # 360 = 0
            s = max(0, min(100, round(s * 100)))
            v = max(0, min(100, round(v * 100)))
        return h, s, v


    def get_rgb(self, normalized: bool = False) -> tuple[float, float, float] | tuple[int, int, int]:
        r, g, b = self.value_rgb
        if normalized:
            r = max(0, min(255, round(r * 255)))
            g = max(0, min(255, round(g * 255)))
            b = max(0, min(255, round(b * 255)))
        return r, g, b


    def set(self, value_hex: Optional[str] = None,
            value_hsv: Optional[tuple[float, float, float]] = None,
            value_hsv_normalized: Optional[tuple[int, int, int]] = None,
            value_rgb: Optional[tuple[float, float, float]] = None,
            value_rgb_normalized: Optional[tuple[int, int, int]] = None
            ) -> None:

        if value_hex is not None:
            value_hex = value_hex.removeprefix("#").upper()
            if len(value_hex) == 3:
                value_hex = value_hex[0]*2+value_hex[1]*2+value_hex[2]*2
            value_hex = f"#{value_hex}"
            if not ColorValidation.is_valid_hex(value_hex):
                raise ValueError(f"Bad value: '{value_hex}'. Value must be a valid hex code with 3/6 characters (not including the #)")
            if value_hex == self.value_hex:
                return

            hex_without_prefix: str = value_hex.removeprefix("#")
            r, g, b = int(hex_without_prefix[0:2], 16) / 255, int(hex_without_prefix[2:4], 16) / 255, int(hex_without_prefix[4:6], 16) / 255
            h, s, v = colorsys.rgb_to_hsv(r, g, b)

            self.value_hex = value_hex
            self. value_hsv = (h, s, v)
            self.value_rgb = (r, g, b)

            self.redraw_all()
            self.update_input_boxes()
            self.update_preview()

        elif value_hsv is not None:
            if not ColorValidation.is_valid_hsv(value_hsv):
                raise ValueError(f"Bad value: '{value_hsv}'. Value must be a tuple of 3 float values between 0 and 1 (hue must be less than 1, saturation and value may be equal to 1)")
            if value_hsv == self.value_hsv:
                return

            h, s, v = value_hsv
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            r_normalized = max(0, min(255, round(r*255)))
            g_normalized = max(0, min(255, round(g*255)))
            b_normalized = max(0, min(255, round(b*255)))
            value_hex = f"#{r_normalized:02x}{g_normalized:02x}{b_normalized:02x}".upper()

            self.value_hex = value_hex
            self.value_hsv = (h, s, v)
            self.value_rgb = (r, g, b)

            self.redraw_all()
            self.update_input_boxes()
            self.update_preview()

        elif value_hsv_normalized is not None:
            if not ColorValidation.is_valid_hsv_normalized(value_hsv_normalized):
                raise ValueError(f"Bad value: '{value_hsv_normalized}'. Value must be a tuple of 3 integer values (hue must be between 0 and 359, saturation and value must be between 0 and 100)")
            
            h, s, v = value_hsv_normalized
            h /= 360
            s /= 100
            v /= 100
            if (h, s, v) == self.value_hsv:
                return

            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            r_normalized = max(0, min(255, round(r*255)))
            g_normalized = max(0, min(255, round(g*255)))
            b_normalized = max(0, min(255, round(b*255)))
            value_hex = f"#{r_normalized:02x}{g_normalized:02x}{b_normalized:02x}".upper()

            self.value_hex = value_hex
            self.value_hsv = (h, s, v)
            self.value_rgb = (r, g, b)

            self.redraw_all()
            self.update_input_boxes()
            self.update_preview()

        elif value_rgb is not None:
            if not ColorValidation.is_valid_rgb(value_rgb):
                raise ValueError(f"Bad value: '{value_rgb}'. Value must be a tuple of 3 float values between 0 and 1")
            if value_rgb == self.value_rgb:
                return

            r, g, b = value_rgb
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            r_normalized = max(0, min(255, round(r*255)))
            g_normalized = max(0, min(255, round(g*255)))
            b_normalized = max(0, min(255, round(b*255)))
            value_hex = f"#{r_normalized:02x}{g_normalized:02x}{b_normalized:02x}".upper()

            self.value_hex = value_hex
            self.value_hsv = (h, s, v)
            self.value_rgb = (r, g, b)

            self.redraw_all()
            self.update_input_boxes()
            self.update_preview()

        elif value_rgb_normalized is not None:
            if not ColorValidation.is_valid_rgb_normalized(value_rgb_normalized):
                raise ValueError(f"Bad value: '{value_rgb_normalized}'. Value must be a tuple of 3 integer values between 0 and 255")
            
            r, g, b = value_rgb_normalized
            r /= 255
            g /= 255
            b /= 255
            if (r, g, b) == self.value_rgb:
                return

            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            r_normalized = max(0, min(255, round(r*255)))
            g_normalized = max(0, min(255, round(g*255)))
            b_normalized = max(0, min(255, round(b*255)))
            value_hex = f"#{r_normalized:02x}{g_normalized:02x}{b_normalized:02x}".upper()

            self.value_hex = value_hex
            self.value_hsv = (h, s, v)
            self.value_rgb = (r, g, b)

            self.redraw_all()
            self.update_input_boxes()
            self.update_preview()


    def destroy(self):
        del self._hue_image
        del self._hue_indicator_image
        del self._sv_foreground_image
        del self._sv_background_image
        del self._sv_mixed_image
        del self._sv_indicator_image

        try:
            del self._scaled_hue_image
            del self._scaled_hue_indicator_image
            del self._scaled_sv_foreground_image
            del self._scaled_sv_background_image
            del self._scaled_sv_mixed_image
            del self._scaled_sv_indicator_image
        except AttributeError: pass

        del self._hue_photoimage
        del self._hue_indicator_photoimage
        del self._sv_photoimage
        del self._sv_indicator_photoimage

        return super().destroy()


    def redraw_all(self) -> None:
        self.redraw_hue()
        self.redraw_sv()


    def redraw_hue(self) -> None:
        scaling: float = self._widget_scaling

        w, h = self._hue_image.size
        w = round(w * scaling)
        h = round(h * scaling)
        self._hue_canvas.configure(width=w, height=h)
        self._scaled_hue_image = self._hue_image.resize((w, h), resample=Image.Resampling.LANCZOS)
        self._hue_photoimage = ImageTk.PhotoImage(self._scaled_hue_image)
        if hasattr(self, "_hue_image_tag"):
            self._hue_canvas.delete(self._hue_image_tag)
        self._hue_image_tag = self._hue_canvas.create_image(round(w/2), round(h/2), image=self._hue_photoimage)

        indicator_y: int = max(0, min(h - 1, round(h * self.value_hsv[0])))

        w, h = self._hue_indicator_image.size
        w = round(w * scaling)
        h = round(h * scaling)
        self._scaled_hue_indicator_image = self._hue_indicator_image.resize((w, h), resample=Image.Resampling.LANCZOS)
        self._hue_indicator_photoimage = ImageTk.PhotoImage(self._scaled_hue_indicator_image)
        if hasattr(self, "_hue_indicator_tag"):
            self._hue_canvas.delete(self._hue_indicator_tag)
        self._hue_indicator_tag = self._hue_canvas.create_image(round(w/2), indicator_y, image=self._hue_indicator_photoimage)


    def redraw_sv(self) -> None:
        h: float = self.value_hsv[0]
        r, g, b = colorsys.hsv_to_rgb(h, 1, 1)
        r = max(0, min(255, round(r*255)))
        g = max(0, min(255, round(g*255)))
        b = max(0, min(255, round(b*255)))
        value_hex: str = f"#{r:02x}{g:02x}{b:02x}".upper()
        self._sv_background_image = Image.new("RGBA", self._sv_foreground_image.size, value_hex)
        self._sv_mixed_image = Image.alpha_composite(self._sv_background_image, self._sv_foreground_image)

        scaling: float = self._widget_scaling

        w, h = self._sv_mixed_image.size
        w = round(w * scaling)
        h = round(h * scaling)
        self._sv_canvas.configure(width=w, height=h)
        self._scaled_sv_image = self._sv_mixed_image.resize((w, h), resample=Image.Resampling.LANCZOS)
        self._sv_photoimage = ImageTk.PhotoImage(self._scaled_sv_image)
        if hasattr(self, "_sv_image_tag"):
            self._sv_canvas.delete(self._sv_image_tag)
        self._sv_image_tag = self._sv_canvas.create_image(round(w/2), round(h/2), image=self._sv_photoimage)

        indicator_x: int = max(0, min(w - 1, round(w * self.value_hsv[1])))
        indicator_y: int = max(0, min(h - 1, round(h - (h * self.value_hsv[2]))))

        w, h = self._sv_indicator_image.size
        w = round(w * scaling)
        h = round(h * scaling)
        self._scaled_sv_indicator_image = self._sv_indicator_image.resize((w, h), resample=Image.Resampling.LANCZOS)
        self._sv_indicator_photoimage = ImageTk.PhotoImage(self._scaled_sv_indicator_image)
        if hasattr(self, "_sv_indicator_tag"):
            self._sv_canvas.delete(self._sv_indicator_tag)
        self._sv_indicator_tag = self._sv_canvas.create_image(indicator_x, indicator_y, image=self._sv_indicator_photoimage)


    def update_input_boxes(self) -> None:
        value_hex: str = self.value_hex
        h, s, v = self.value_hsv
        r, g, b = self.value_rgb

        hue: int = max(0, min(359, round(h * 360)))
        saturation: int = max(0, min(100, round(s * 100)))
        value: int = max(0, min(100, round(v * 100)))

        red: int = max(0, min(255, round(r * 255)))
        green: int = max(0, min(255, round(g * 255)))
        blue: int = max(0, min(255, round(b * 255)))

        if self._hex_input is not None:
            self._hex_input.set(value_hex)

        if self._hsv_h_input is not None:
            self._hsv_h_input.set(str(hue))
        if self._hsv_s_input is not None:
            self._hsv_s_input.set(str(saturation))
        if self._hsv_v_input is not None:
            self._hsv_v_input.set(str(value))

        if self._rgb_r_input is not None:
            self._rgb_r_input.set(str(red))
        if self._rgb_g_input is not None:
            self._rgb_g_input.set(str(green))
        if self._rgb_b_input is not None:
            self._rgb_b_input.set(str(blue))


    def update_preview(self) -> None:
        if self._preview_frame is not None:
            self._preview_frame.configure(fg_color=self.value_hex)
        try:
            if self.on_update_callback is not None:
                self.on_update_callback(self.value_hex)
        except Exception:
            pass


    def _on_scaling_change(self, widget_scaling: float, window_scaling: float) -> None:
        self._widget_scaling = widget_scaling
        self.redraw_all()


    def _on_appearance_change(self, appearance: Literal["Light", "Dark"]) -> None:
        parent_background: tuple[str, str] = self.cget("bg_color")
        if appearance == "Light":
            self._sv_canvas.configure(background=parent_background[0])
            self._hue_canvas.configure(background=parent_background[0])
        elif appearance == "Dark":
            self._sv_canvas.configure(background=parent_background[1])
            self._hue_canvas.configure(background=parent_background[1])


    def _on_hue_drag(self, event) -> None:
        h: int = self._hue_photoimage.height() - 1
        y: int = max(0, min(h, event.y))
        hue: float = y / (h + 1)
        _, s, v = self.value_hsv

        if self.value_hsv == (hue, s, v):
            return

        self.value_hsv = (hue, s, v)
        r, g, b = colorsys.hsv_to_rgb(hue, s, v)
        self.value_rgb = (r, g, b)
        r = max(0, min(255, round(r*255)))
        g = max(0, min(255, round(g*255)))
        b = max(0, min(255, round(b*255)))
        self.value_hex = f"#{r:02x}{g:02x}{b:02x}".upper()

        self.redraw_hue()
        self.redraw_sv()
        self.update_input_boxes()
        self.update_preview()


    def _on_sv_drag(self, event) -> None:
        w: int = self._sv_photoimage.width() - 1
        h: int = self._sv_photoimage.height() - 1
        x: int = max(0, min(w, event.x))
        y: int = max(0, min(h, event.y))

        hue: float = self.value_hsv[0]
        s: float = x / w
        v: float = 1 - (y / h)

        if self.value_hsv == (hue, s, v):
            return

        self.value_hsv = (hue, s, v)
        r, g, b = colorsys.hsv_to_rgb(hue, s, v)
        self.value_rgb = (r, g, b)
        r = max(0, min(255, round(r*255)))
        g = max(0, min(255, round(g*255)))
        b = max(0, min(255, round(b*255)))
        self.value_hex = f"#{r:02x}{g:02x}{b:02x}".upper()

        self.redraw_sv()
        self.update_input_boxes()
        self.update_preview()


    def _on_hex_input(self, event) -> None:
        value: str = event.value
        try:
            self.set(value_hex=value)
        except ValueError:
            event.widget.set(self.value_hex)


    def _on_hsv_input(self, mode: Literal["h", "s", "v"], event) -> None:
        h, s, v = self.value_hsv
        value: str = event.value

        try:
            value_int: int = int(value)
            match mode:
                case "h": h = value_int / 360
                case "s": s = value_int / 100
                case "v": v = value_int / 100
            self.set(value_hsv=(h, s, v))
        except ValueError:
            h, s, v = self.value_hsv
            match mode:
                case "h":
                    if self._hsv_h_input is not None:
                        self._hsv_h_input.set(str(int(h * 360)))
                case "s":
                    if self._hsv_s_input is not None:
                        self._hsv_s_input.set(str(int(s * 100)))
                case "v":
                    if self._hsv_v_input is not None:
                        self._hsv_v_input.set(str(int(v * 100)))


    def _on_rgb_input(self, mode: Literal["r", "g", "b"], event) -> None:
        r, g, b = self.value_rgb
        value: str = event.value

        try:
            value_int: int = int(value)
            match mode:
                case "r": r = value_int / 360
                case "g": g = value_int / 100
                case "b": b = value_int / 100
            self.set(value_rgb=(r, g, b))
        except ValueError:
            r, g, b = self.value_rgb
            match mode:
                case "r":
                    if self._rgb_r_input is not None:
                        self._rgb_r_input.set(str(int(r * 255)))
                case "g":
                    if self._rgb_g_input is not None:
                        self._rgb_g_input.set(str(int(g * 255)))
                case "b":
                    if self._rgb_b_input is not None:
                        self._rgb_b_input.set(str(int(b * 255)))
# endregion


# region ask_color
def ask_color(master=None, title: str = "ColorPicker", icon: Optional[str | Path] = None, default_color: Optional[str] = None, advanced: bool = False, **kwargs) -> str:
    window: Toplevel = Toplevel(title, icon, master=master)
    window.resizable(False, False)


    color_picker: ColorPicker = ColorPicker(window, default_color, advanced=advanced, **kwargs)
    color_picker.grid(padx=8, pady=8, sticky="nsew")

    if master:  # center on master
        master.update_idletasks()
        window.update_idletasks()
        root_scaling: float = ScalingTracker.get_window_scaling(master)
        self_scaling: float = ScalingTracker.get_window_scaling(window)

        root_x: int = master.winfo_rootx()
        root_y: int = master.winfo_rooty()
        root_w: int = int(master.winfo_width() / root_scaling)
        root_h: int = int(master.winfo_height() / root_scaling)
        width: int = int(window.winfo_reqwidth() / self_scaling)
        height: int = int(window.winfo_reqheight() / self_scaling)

        window.geometry(f"{width}x{height}+{root_x + int((root_w - width) / 2)}+{root_y + int((root_h - height) / 2)}")

    window.grab_set()
    window.wait_window()
    return color_picker.value_hex
# endregion