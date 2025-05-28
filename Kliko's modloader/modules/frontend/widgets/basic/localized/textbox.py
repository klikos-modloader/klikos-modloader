from typing import Callable, Optional

from modules.localization import Localizer

from customtkinter import CTkTextbox  # type: ignore


class LocalizedCTkTextbox(CTkTextbox):
    _localizer_string_key: Optional[str] = None
    _localizer_string_modification: Optional[Callable[[str], str]] = None
    _localizer_callback_id: Optional[str] = None


    def __init__(self, master, placeholder_key: Optional[str] = None, placeholder_modification: Optional[Callable[[str], str]] = None, **kwargs):
        super().__init__(master, **kwargs)
        self._localizer_string_key = placeholder_key
        if placeholder_key is None:
            self._localizer_string_modification = None
            self._localizer_callback_id = None
        else:
            if callable(placeholder_modification):
                self._localizer_string_modification = placeholder_modification
            self._localizer_callback_id = Localizer.add_callback(self._update_localized_string)
            self._update_localized_string()


    def destroy(self):
        if self._localizer_callback_id is not None: Localizer.remove_callback(self._localizer_callback_id)
        return super().destroy()


    def _update_localized_string(self) -> None:
        string: str | None = Localizer.Strings.get(self._localizer_string_key)
        if string is None:
            self.configure(placeholder_text=self._localizer_string_key)
            return

        if self._localizer_string_modification is not None:
            string = self._localizer_string_modification(string)

        self.configure(placeholder_text=string)