from tkinter import TclError
from typing import TYPE_CHECKING
import webbrowser

from modules.project_data import ProjectData, License
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button
from modules.frontend.functions import get_ctk_image
from modules.localization import Localizer
from modules.filesystem import Resources

if TYPE_CHECKING: from modules.frontend.widgets import Root

from customtkinter import CTkImage  # type: ignore


class AboutSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8

    _SECTION_GAP: int = 16
    _ENTRY_GAP: int = 8
    _ENTRY_PADDING: tuple[int, int] = (16, 16)
    _ENTRY_INNER_GAP: int = 8


    def __init__(self, master):
        super().__init__(master, transparent=False, round=True, border=True, layer=1)
        self.root = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def clear(self) -> None:
        for widget in self.winfo_children():
            try: widget.destroy()
            except TclError: pass
        self.loaded = False


    def refresh(self) -> None:
        self.clear()
        self.show()


    def show(self) -> None:
        self.load()


# region load
    def load(self) -> None:
        if self.loaded: return

        content: Frame = Frame(self, transparent=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid(column=0, row=0, sticky="nsew", padx=self._SECTION_PADX, pady=self._SECTION_PADY)

        self._load_header(content)
        self._load_content(content)

        self.loaded = True


    def _load_header(self, master) -> None:
        header: Frame = Frame(master, transparent=True)
        header.grid_columnconfigure(0, weight=1)
        header.grid(column=0, row=0, sticky="nsew", pady=(0,16))

        Label(header, "menu.about.header.title", style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.about.header.description", lambda string: Localizer.format(string, {"{app.name}": ProjectData.NAME}), style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")

        button_wrapper: Frame = Frame(header, transparent=True)
        button_wrapper.grid(column=0, row=2, sticky="w", pady=(8, 0))

        github_image: CTkImage = get_ctk_image(Resources.Brands.Light.GITHUB, Resources.Brands.Dark.GITHUB, size=20)
        Button(button_wrapper, "menu.about.header.button.github", secondary=True, image=github_image, command=lambda: webbrowser.open_new_tab(ProjectData.REPOSITORY)).grid(column=0, row=0)
        Button(button_wrapper, "menu.about.header.button.releases", secondary=True, image=github_image, command=lambda: webbrowser.open_new_tab(ProjectData.RELEASES)).grid(column=1, row=0, padx=(8, 0))

        discord_image: CTkImage = get_ctk_image(Resources.Brands.Light.DISCORD, Resources.Brands.Dark.DISCORD, size=20)
        Button(button_wrapper, "menu.about.header.button.discord", secondary=True, image=discord_image, command=lambda: webbrowser.open_new_tab(ProjectData.DISCORD)).grid(column=2, row=0, padx=(8, 0))


    def _load_content(self, master) -> None:
        wrapper: Frame = Frame(master, transparent=True)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(1, weight=1)
        wrapper.grid(column=0, row=1, sticky="nsew")
        section_counter: int = -1


        # # Banner
        # section_counter += 1
        # banner_frame = Frame(wrapper, transparent=True)
        # banner_frame.grid(column=0, row=section_counter, sticky="ns", pady=0 if section_counter == 0 else (self._SECTION_GAP, 0))

        # banner_image: CTkImage = get_ctk_image(Resources.BANNER, size=(500, "auto"))
        # Label(banner_frame, image=banner_image).grid(column=0, row=0)


        # Licenses
        if ProjectData.LICENSES:
            section_counter += 1
            licenses_frame: Frame = Frame(wrapper, transparent=True)
            licenses_frame.grid_columnconfigure(0, weight=1)
            licenses_frame.grid(column=0, row=section_counter, sticky="nsew", pady=0 if section_counter == 0 else (self._SECTION_GAP, 0))

            Label(licenses_frame, "menu.about.content.licenses", style="subtitle", autowrap=True).grid(column=0, row=0, sticky="nsew")

            license_wrapper: Frame = Frame(licenses_frame, transparent=True)
            license_wrapper.grid(column=0, row=1, sticky="nsew", pady=(self._ENTRY_GAP, 0))

            arrow_image: CTkImage = get_ctk_image(Resources.Common.Light.ARROW_RIGHT, Resources.Common.Dark.ARROW_RIGHT, size=20)

            if len(ProjectData.LICENSES) <= 3:
                license_wrapper.grid_columnconfigure(0, weight=1)
                for i, license in enumerate(ProjectData.LICENSES):
                    box: Frame = self._create_license_box(license_wrapper, license, arrow_image)
                    box.grid(column=0, row=i, sticky="nsew", pady=0 if i == 0 else (self._ENTRY_GAP, 0))

            else:
                license_wrapper.grid_columnconfigure((0, 1), weight=1, uniform="group")
                for i, license in enumerate(ProjectData.LICENSES):
                    column: int = i % 2
                    row: int = i // 2
                    box = self._create_license_box(license_wrapper, license, arrow_image)
                    box.grid(column=column, row=row, padx=0 if column == 0 else (self._ENTRY_GAP, 0), pady=0 if row == 0 else (self._ENTRY_GAP, 0), sticky="nsew")


        # Contributors, Feature suggestions & Special thanks
        has_contributors: bool = bool(ProjectData.CONTRIBUTORS)
        has_feature_suggestions: bool = bool(ProjectData.FEATURE_SUGGESTIONS)
        has_special_thanks: bool = bool(ProjectData.SPECIAL_THANKS)
        if has_contributors or has_feature_suggestions or has_special_thanks:
            section_counter += 1
            contributor_suggestion_thanks_wrapper = Frame(wrapper, transparent=True)
            contributor_suggestion_thanks_wrapper.grid_columnconfigure(list(range(int(has_contributors) + int(has_feature_suggestions) + int(has_special_thanks))), weight=1, uniform="group")
            contributor_suggestion_thanks_wrapper.grid(column=0, row=section_counter, sticky="nsew", pady=0 if section_counter == 0 else (self._SECTION_GAP, 0))

            Label(contributor_suggestion_thanks_wrapper, "menu.about.content.credits", style="subtitle", autowrap=True).grid(column=0, row=0, sticky="nsew", pady=(0, self._ENTRY_GAP))
            column = -1
            if has_contributors:
                column += 1
                contributors_box: Frame = Frame(contributor_suggestion_thanks_wrapper, layer=2)
                contributors_box.grid_columnconfigure(0, weight=1)
                contributors_box.grid(column=0, row=1, sticky="nsew")

                column_wrapper: Frame = Frame(contributors_box, transparent=True)
                column_wrapper.grid_columnconfigure(0, weight=1)
                column_wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

                Label(column_wrapper, "menu.about.content.credits.contributors", style="body_strong", autowrap=True).grid(column=0, row=0, columnspan=3, sticky="nsew")
                for i, contributor in enumerate(ProjectData.CONTRIBUTORS): Label(column_wrapper, contributor.name, style="body", autowrap=True, url=contributor.url).grid(column=column, row=i+1, pady=(4, 0), sticky="ew")

            if has_feature_suggestions:
                column += 1
                feature_suggestions_box: Frame = Frame(contributor_suggestion_thanks_wrapper, layer=2)
                feature_suggestions_box.grid_columnconfigure(0, weight=1)
                feature_suggestions_box.grid(column=column, row=1, sticky="nsew", padx=0 if column == 0 else (self._ENTRY_GAP, 0))

                column_wrapper = Frame(feature_suggestions_box, transparent=True)
                column_wrapper.grid_columnconfigure(0, weight=1)
                column_wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

                Label(column_wrapper, "menu.about.content.credits.feature_suggestions", style="body_strong", autowrap=True).grid(column=0, row=0, sticky="nsew")
                for i, contributor in enumerate(ProjectData.FEATURE_SUGGESTIONS): Label(column_wrapper, contributor.name, style="body", autowrap=True, url=contributor.url).grid(column=0, row=i+1, pady=(4, 0), sticky="ew")

            if has_special_thanks:
                column += 1
                special_thanks_box: Frame = Frame(contributor_suggestion_thanks_wrapper, layer=2)
                special_thanks_box.grid_columnconfigure(0, weight=1)
                special_thanks_box.grid(column=column, row=1, sticky="nsew", padx=0 if column == 0 else (self._ENTRY_GAP, 0))

                column_wrapper = Frame(special_thanks_box, transparent=True)
                column_wrapper.grid_columnconfigure(0, weight=1)
                column_wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

                Label(column_wrapper, "menu.about.content.credits.special_thanks", style="body_strong", autowrap=True).grid(column=0, row=0, sticky="nsew")
                for i, contributor in enumerate(ProjectData.SPECIAL_THANKS): Label(column_wrapper, contributor.name, style="body", autowrap=True, url=contributor.url).grid(column=0, row=i+1, pady=(4, 0), sticky="ew")
# endregion


# functions
    def _create_license_box(self, master, license: License, arrow_image: CTkImage) -> Frame:
        frame: Frame = Frame(master, layer=2)
        frame.grid_columnconfigure(0, weight=1)
        content_wrapper: Frame = Frame(frame, transparent=True)
        content_wrapper.grid_columnconfigure(0, weight=1)
        content_wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

        Label(content_wrapper, license.product, style="body_strong", autowrap=True).grid(column=0, row=0, sticky="sew")
        Label(content_wrapper, license.type, style="body", autowrap=True).grid(column=0, row=1, sticky="new")
        if license.url: Button(content_wrapper, secondary=True, image=arrow_image, width=40, height=40, command=lambda url=license.url: webbrowser.open_new_tab(url)).grid(column=1, row=0, rowspan=2, sticky="e", padx=(self._ENTRY_INNER_GAP, 0))

        return frame
# endregion