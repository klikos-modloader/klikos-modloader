from typing import Callable, Optional

from modules.localization import Localizer

from customtkinter import CTkButton  # type: ignore


class LocalizedCTkButton(CTkButton):
    _localizer_string_key: Optional[str] = None
    _localizer_string_modification: Optional[Callable[[str], str]] = None
    _localizer_callback_id: Optional[str] = None


    def __init__(self, master, key: Optional[str] = None, modification: Optional[Callable[[str], str]] = None, **kwargs):
        kwargs.pop("text", None)
        super().__init__(master, text=key or "", **kwargs)
        self._localizer_string_key = key
        if key is None:
            self._localizer_string_modification = None
            self._localizer_callback_id = None
        else:
            if callable(modification):
                self._localizer_string_modification = modification
            self._localizer_callback_id = Localizer.add_callback(self._update_localized_string)
            self._update_localized_string()


    def configure(self, **kwargs):
        key = kwargs.pop("key", None)
        modification = kwargs.pop("modification", ...)

        update_text = False
        if key is not None:
            self._localizer_string_key = key
            if self._localizer_callback_id is None:
                self._localizer_callback_id = Localizer.add_callback(self._update_localized_string)
            update_text = True
        if modification is not ...:
            self._localizer_string_modification = modification
            update_text = True
        if update_text:
            self._update_localized_string()

        kwargs.pop("text", None)
        return super().configure(**kwargs)


    def destroy(self):
        if self._localizer_callback_id is not None: Localizer.remove_callback(self._localizer_callback_id)
        return super().destroy()


    def _update_localized_string(self) -> None:
        string: str | None = Localizer.Strings.get(self._localizer_string_key)
        if string is None:
            super().configure(text=self._localizer_string_key)
            return

        if self._localizer_string_modification is not None:
            string = self._localizer_string_modification(string)

        super().configure(text=string)