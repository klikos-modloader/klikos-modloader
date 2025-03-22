import webbrowser
from pathlib import Path

from modules.info import NAME, LICENSES, CONTRIBUTORS, FEATURE_SUGGESTIONS, SPECIAL_THANKS, GITHUB, CHANGELOG, DISCORD
from modules.localization import Localizer
from modules.frontend.widgets.fluent import FluentFrame, FluentLabel, FluentButton, FluentToolTipButton, get_root_instance

import customtkinter as ctk  # type: ignore
from PIL import Image  # type: ignore


class AboutSection:
    PADDING_X: int = 16
    PADDING_Y: int = 16
    GRID_GAP: int = 16
    BOX_PADX: int = 16
    BOX_PADY: int = 16
    BOX_TITLE_FONT_SIZE: int = 18

    resources: Path
    banner: ctk.CTkImage
    arrow_right_light: Image.Image
    arrow_right_dark: Image.Image

    master: ctk.CTkFrame
    content: ctk.CTkFrame | ctk.CTkScrollableFrame
    tooltip_button: FluentToolTipButton

    active: bool = False
    first_load: bool = True


    def __init__(self, root: ctk.CTk, master: ctk.CTkFrame | ctk.CTkScrollableFrame, resources: Path) -> None:
        self.root = root
        self.master = master
        self.resources = resources
        self.banner = ctk.CTkImage(Image.open(self.resources / "about" / "banner.png"), size=(548,165))
        self.arrow_right_light = Image.open(self.resources / "common" / "light" / "arrow_right.png")
        self.arrow_right_dark = Image.open(self.resources / "common" / "dark" / "arrow_right.png")


    def refresh(self) -> None:
        self._clear()
        self._load()


    def load(self) -> None:
        if self.active: return
        self.active = True
        self.tooltip_button.enable()


    def unload(self) -> None:
        self.active = False
        self.tooltip_button.disable()

    
    def _clear(self) -> None:
        for widget in self.master.winfo_children():
            widget.destroy()


    def _load(self) -> None:
        self.content = ctk.CTkFrame(self.master, fg_color="transparent")
        self.content.grid(column=0, row=0, sticky="nsew", padx=self.PADDING_X, pady=self.PADDING_Y)
        self.content.grid_columnconfigure(0, weight=1)
        self._get_title_frame().grid(column=0, row=0, sticky="nsew")
        self._get_content().grid(column=0, row=1, sticky="nsew", pady=(16,0))


    def _get_title_frame(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content, fg_color="transparent")

        title_row = ctk.CTkFrame(frame, fg_color="transparent")
        title_row.grid(column=0, row=0, sticky="w")

        FluentLabel(title_row, Localizer.strings["menu.about"]["title"], font_size=28, font_weight="bold").grid(column=0, row=0, sticky="w")
        self.tooltip_button = FluentToolTipButton(get_root_instance(), master=title_row, wraplength=400, tooltip_title=Localizer.strings["menu.about"]["tooltip.title"].replace("{project_name}", NAME), tooltip_message=Localizer.strings["menu.about"]["tooltip.message"].replace("{project_name}", NAME), tooltip_orientation="down", toplevel=True)
        self.tooltip_button.grid(column=1, row=0, padx=(8,0), sticky="w")

        return frame

    
    def _get_content(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        # Banner
        banner_frame = FluentFrame(frame)
        banner_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(banner_frame, text="", image=self.banner).grid(column=0, row=0)

        button_row = ctk.CTkFrame(banner_frame, fg_color="transparent")
        button_row.grid(column=0, row=1, pady=(0,self.BOX_PADY+2))

        FluentButton(button_row, Localizer.strings["buttons.github"], command=lambda: webbrowser.open(GITHUB, 2)).grid(column=0, row=0)
        FluentButton(button_row, Localizer.strings["buttons.changelog"], command=lambda: webbrowser.open(CHANGELOG, 2)).grid(column=1, row=0, padx=(8, 0))
        FluentButton(button_row, Localizer.strings["buttons.discord"], command=lambda: webbrowser.open(DISCORD, 2)).grid(column=2, row=0, padx=(8, 0))

        banner_frame.grid(column=0, row=0, sticky="ew", pady=(0, self.GRID_GAP))

        # Licenses
        license_frame = FluentFrame(frame)
        license_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(license_frame, text=Localizer.strings["menu.about"]["licenses"], font_size=self.BOX_TITLE_FONT_SIZE, font_weight="bold", justify="center").grid(column=0, row=0, sticky="ew", padx=self.BOX_PADX, pady=self.BOX_PADY)
        
        if not LICENSES: FluentLabel(license_frame, text=Localizer.strings["menu.about"]["no_data"], justify="center").grid(column=0, row=1, sticky="ew", padx=self.BOX_PADX, pady=(0, self.BOX_PADY))
        else:
            license_list_frame = ctk.CTkFrame(license_frame, fg_color="transparent")
            license_list_frame.grid_columnconfigure((0,1), weight=1, uniform="group")
            license_list_frame.grid(column=0, row=1, padx=self.BOX_PADX, pady=(0, self.BOX_PADY), sticky="nsew")
            license_count: int = -1
            for license in LICENSES:
                license_name: str | None = license.get("name")
                license_type: str = license.get("type", "Unknown License Type")
                license_author: str | None = license.get("author")
                license_url: str | None = license.get("url")
                license_text: str | None = license.get("license")

                if not license_name or not license_author or not license_text: continue
                license_count += 1

                # TODO: Try to make FluentButtonFrame and see if it looks better
                license_box = FluentFrame(license_list_frame, toplevel=True)
                license_box.grid_columnconfigure(0, weight=1)

                FluentLabel(license_box, license_name, font_size=14, font_weight="bold", justify="left").grid(column=0, row=0, padx=self.BOX_PADX, pady=(self.BOX_PADY,0), sticky="w")
                FluentLabel(license_box, license_type, font_size=14, justify="left").grid(column=0, row=1, padx=self.BOX_PADX, pady=(0,self.BOX_PADY), sticky="w")
                if license_url is not None: FluentButton(license_box, width=36, height=36, command=lambda: webbrowser.open(license_url, 2), light_icon=self.arrow_right_light, dark_icon=self.arrow_right_dark, icon_size=(24, 24)).grid(column=1, row=0, rowspan=2, sticky="w", padx=(0, self.BOX_PADX+2), pady=self.BOX_PADY+2)

                license_box.grid(column=self._get_license_column(license_count), row=self._get_license_row(license_count), sticky="nsew", padx=self._get_license_padx(license_count), pady=0 if license_count < 2 else (self.GRID_GAP, 0))

        license_frame.grid(column=0, row=1, sticky="ew", pady=(0, self.GRID_GAP))

        # Contributors
        contributors_section_frame = ctk.CTkFrame(frame, fg_color="transparent")
        contributors_section_frame.grid_columnconfigure((0,1,2), weight=1)
        contributors_section_frame.grid(column=0, row=2, sticky="ew")

        contributors_frame = FluentFrame(contributors_section_frame)
        contributors_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(contributors_frame, text=Localizer.strings["menu.about"]["contributors"], font_size=self.BOX_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=self.BOX_PADX, pady=self.BOX_PADY)
        
        if not CONTRIBUTORS: FluentLabel(contributors_frame, text=Localizer.strings["menu.about"]["no_data"]).grid(column=0, row=1, sticky="w", padx=self.BOX_PADX, pady=(0, self.BOX_PADY))
        else:
            contributors_list_frame = ctk.CTkFrame(contributors_frame, fg_color="transparent")
            contributors_list_frame.grid(column=0, row=1, sticky="ew", padx=self.BOX_PADX, pady=(0, self.BOX_PADY))
            contributor_count: int = -1
            for contributor in CONTRIBUTORS:
                text: str | None = contributor.get("text")
                url: str = contributor.get("url", "")

                if text is None: continue
                contributor_count += 1

                FluentLabel(contributors_list_frame, text=text, justify="left", anchor="w", hyperlink=True if url else False, hyperlink_url=url).grid(column=0, row=contributor_count, sticky="ew")

        contributors_frame.grid(column=0, row=2, sticky="nsew")

        feature_suggestions_frame = FluentFrame(contributors_section_frame)
        feature_suggestions_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(feature_suggestions_frame, text=Localizer.strings["menu.about"]["feature_suggestions"], font_size=self.BOX_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=self.BOX_PADX, pady=self.BOX_PADY)
        
        if not FEATURE_SUGGESTIONS: FluentLabel(feature_suggestions_frame, text=Localizer.strings["menu.about"]["no_data"]).grid(column=0, row=1, sticky="w", padx=self.BOX_PADX, pady=(0, self.BOX_PADY))
        else:
            feature_suggestions_list_frame = ctk.CTkFrame(feature_suggestions_frame, fg_color="transparent")
            feature_suggestions_list_frame.grid(column=0, row=1, sticky="ew", padx=self.BOX_PADX, pady=(0, self.BOX_PADY))
            feature_suggestion_count: int = -1
            for feature_suggestion in FEATURE_SUGGESTIONS:
                text = feature_suggestion.get("text")
                url = feature_suggestion.get("url", "")

                if text is None: continue
                feature_suggestion_count += 1

                FluentLabel(feature_suggestions_list_frame, text=text, justify="left", anchor="w", hyperlink=True if url else False, hyperlink_url=url).grid(column=0, row=feature_suggestion_count, sticky="ew")

        feature_suggestions_frame.grid(column=1, row=2, sticky="nsew", padx=self.GRID_GAP)

        special_thanks_frame = FluentFrame(contributors_section_frame)
        special_thanks_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(special_thanks_frame, text=Localizer.strings["menu.about"]["special_thanks"], font_size=self.BOX_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=self.BOX_PADX, pady=self.BOX_PADY)

        if not SPECIAL_THANKS: FluentLabel(special_thanks_frame, text=Localizer.strings["menu.about"]["no_data"]).grid(column=0, row=1, sticky="w", padx=self.BOX_PADX, pady=(0, self.BOX_PADY))
        else:
            special_thanks_list_frame = ctk.CTkFrame(special_thanks_frame, fg_color="transparent")
            special_thanks_list_frame.grid(column=0, row=1, sticky="ew", padx=self.BOX_PADX, pady=(0, self.BOX_PADY))
            special_thanks_count: int = -1
            for special_thanks in SPECIAL_THANKS:
                text = special_thanks.get("text")
                url = special_thanks.get("url", "")

                if text is None: continue
                special_thanks_count += 1

                FluentLabel(special_thanks_list_frame, text=text, justify="left", anchor="w", hyperlink=True if url else False, hyperlink_url=url).grid(column=0, row=special_thanks_count, sticky="ew")

        special_thanks_frame.grid(column=2, row=2, sticky="nsew")

        return frame


# region functions
    def _get_license_column(self, i: int) -> int:
        return i%2

    def _get_license_row(self, i: int) -> int:
        return i//2

    def _get_license_padx(self, i: int) -> int | tuple[int, int]:
        return (self.GRID_GAP, 0) if i%2 == 1 else 0
# endregion