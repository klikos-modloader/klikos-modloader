from typing import Callable, Optional

from modules.localization import Localizer

from customtkinter import CTkSwitch  # type: ignore


class LocalizedCTkSwitch(CTkSwitch):
    _localizer_string_key: Optional[str] = None
    _localizer_string_modification: Optional[Callable[[str], str]] = None
    _localizer_callback_id: Optional[str] = None


    def __init__(self, master, key: Optional[str] = None, modification: Optional[Callable[[str], str]] = None, **kwargs):
        kwargs.pop("text", None)
        if not key:
            if "width" not in kwargs: kwargs["width"] = 36
            if "height" not in kwargs: kwargs["height"] = 18
        super().__init__(master, text=key or "", **kwargs)
        if key is not None:
            self._localizer_string_key = key
            if callable(modification):
                self._localizer_string_modification = modification
            self._localizer_callback_id = Localizer.add_callback(self._update_localized_string)
            self._update_localized_string()
        else: self._localizer_callback_id = None


    def destroy(self):
        if self._localizer_callback_id is not None: Localizer.remove_callback(self._localizer_callback_id)
        return super().destroy()


    def _update_localized_string(self) -> None:
        string: str | None = Localizer.Strings.get(self._localizer_string_key)
        if string is None:
            self.configure(text=self._localizer_string_key)
            return

        if callable(self._localizer_string_modification):
            string = self._localizer_string_modification(string)

        self.configure(text=string)