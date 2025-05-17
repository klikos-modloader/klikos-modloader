from typing import Callable, Optional

from modules.localization import Localizer

from customtkinter import CTkOptionMenu  # type: ignore


class LocalizedCTkOptionMenu(CTkOptionMenu):
    _localizer_data: dict[str, Optional[Callable[[str], str]]]
    _localizer_callback_id: str


    def __init__(self, master, value_keys: list[str], value_modifications: Optional[list[Optional[Callable[[str], str]]]] = None, dont_localize: bool = False, **kwargs):
        kwargs.pop("values", None)
        super().__init__(master, values=value_keys, **kwargs)
        if dont_localize: return

        if value_modifications is None: value_modifications = [None] * len(value_keys)
        key_count: int = len(value_keys)
        modification_count: int = len(value_modifications)
        if key_count > modification_count: value_modifications += [None] * (key_count - modification_count)
        self._localizer_data = dict(zip(value_keys, value_modifications))

        self._localizer_callback_id = Localizer.add_callback(self._update_localized_string)
        self._update_localized_string()


    def destroy(self):
        if hasattr(self, "_localizer_callback_id"):
            Localizer.remove_callback(self._localizer_callback_id)
        return super().destroy()


    def _update_localized_string(self) -> None:
        options: list[str] = []

        for key, modification in self._localizer_data.items():
            string: str | None = Localizer.Strings.get(key)
            if string is None:
                options.append(key)
                continue
            elif modification is not None and callable(modification):
                string = modification(string)
            options.append(string)

        self.configure(values=options)