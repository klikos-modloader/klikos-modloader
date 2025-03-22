import tempfile
import time
import hashlib
import shutil
from io import BytesIO
from typing import Callable
from pathlib import Path
from threading import Thread
from tkinter import TclError
from ssl import SSLError

from modules.logger import Logger
from modules.localization import Localizer
from modules import filesystem
from modules.filesystem import Directory, StreamedDownloadHandler, DownloadInProgressError, DownloadPermissionError, DownloadSocketTimeoutError, DownloadConnectionError, DownloadHTTPError, ExtractPermissionError
from modules.networking import requests, Api, Response, RequestException
from modules.frontend.widgets.fluent import FluentFrame, FluentLabel, FluentButtonFrame, FluentToolTipButton, messagebox, get_root_instance
from modules.frontend.menu.toplevels.mod_download_window import ModDownloadWindow

import customtkinter as ctk  # type: ignore
from PIL import Image, UnidentifiedImageError  # type: ignore


class MarketplaceSection:
    PADDING_X: int = 16
    PADDING_Y: int = 16
    ENTRY_GAP: int = 16
    ENTRY_INNER_PADX: int = 8
    ENTRY_INNER_PADY: int = 8
    COLUMNS: int = 3

    resources: Path
    favicon: Path
    download_light: Image.Image
    download_dark: Image.Image
    placeholder_light: Image.Image
    placeholder_dark: Image.Image
    wifi_off: ctk.CTkImage
    thumbnail_mask: Image.Image

    root: ctk.CTk
    master: ctk.CTkFrame
    content: ctk.CTkFrame | ctk.CTkScrollableFrame
    tooltip_button: FluentToolTipButton
    marketplace_content_frame: ctk.CTkFrame

    active: bool = False
    _DEBOUNCE: int = 200
    _MOD_THUMBNAIL_ASPECT_RATIO: float = 16/9
    _MOD_THUMBNAIL_CACHE_EXPIRY: int = 86400 * 7  # 86400 * n DAYS
    _is_downloading: bool = False


    def __init__(self, root: ctk.CTk, master: ctk.CTkFrame | ctk.CTkScrollableFrame, resources: Path) -> None:
        self.root = root
        self.master = master
        self.resources = resources
        self.favicon = self.resources / "favicon.ico"
        self.download_light = Image.open(self.resources / "common" / "light" / "download.png")
        self.download_dark = Image.open(self.resources / "common" / "dark" / "download.png")
        self.wifi_off = ctk.CTkImage(Image.open(self.resources / "marketplace" / "light" / "wifi_off.png"), Image.open(self.resources / "marketplace" / "dark" / "wifi_off.png"), size=(96, 96))

        self.thumbnail_mask = Image.open(self.resources / "marketplace" / "mask.png")
        self.placeholder_light = Image.open(self.resources / "marketplace" / "light" / "placeholder.png")
        self.placeholder_dark = Image.open(self.resources / "marketplace" / "dark" / "placeholder.png")


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

        FluentLabel(title_row, Localizer.strings["menu.marketplace"]["title"], font_size=28, font_weight="bold").grid(column=0, row=0, sticky="w")
        self.tooltip_button = FluentToolTipButton(get_root_instance(), master=title_row, wraplength=400, tooltip_title=Localizer.strings["menu.marketplace"]["tooltip.title"], tooltip_message=Localizer.strings["menu.marketplace"]["tooltip.message"], tooltip_orientation="down", toplevel=True)
        self.tooltip_button.grid(column=1, row=0, padx=(8,0), sticky="w")

        return frame

    
    def _get_content(self) -> ctk.CTkFrame:
        self.marketplace_content_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self._get_marketplace_data(self._load_mods)
        return self.marketplace_content_frame
    

    def _load_mods(self, data: list[dict] | None) -> None:
        try:
            frame = self.marketplace_content_frame

            for widget in frame.winfo_children():
                widget.destroy()

            if not data:
                frame.grid_columnconfigure(0, weight=1)
                content_frame = FluentFrame(frame)
                content_frame.grid(column=0, row=0, sticky="nsew")
                FluentLabel(content_frame, Localizer.strings["menu.marketplace"]["failed_to_load"], image=self.wifi_off, font_size=24, font_weight="bold", compound="left", padx=16).place(relx=0.5, rely=0.5, anchor="center")
                return

            # Annoying workaround because `uniform="group"` ignores padding
            # Instead of padding, I add an invisible frame between each column
            for i in range(0, (self.COLUMNS*2)-1, 2):
                frame.grid_columnconfigure(i, weight=1, uniform="group")
            for i in range(1, (self.COLUMNS*2)-1, 2):
                ctk.CTkFrame(frame, width=self.ENTRY_GAP, height=1, fg_color="transparent").grid(column=i, row=0, sticky="ns")

            mod_counter: int = -1
            for mod in data:
                id: str | None = mod.get("id")
                name: str | None = mod.get("name")
                description: str | None = mod.get("description")
                author: str | None = mod.get("author")
                thumbnail_url: str | None = mod.get("thumbnail")
                thumbnail_hash: str | None = mod.get("cache_id")
                download_url: str | None = mod.get("download")

                if not name or not id or not download_url: continue
                mod_counter += 1

                thumbnail_image: Image.Image | tuple[Image.Image, Image.Image] = self._get_thumbnail(id, thumbnail_url, thumbnail_hash)

                self.root.after(0, self._scheduled_frame_creation, frame, id, name, description, author, thumbnail_image, download_url, mod_counter)

        except TclError:
            pass


# region functions
    def _get_marketplace_data(self, callback: Callable) -> None:
        def worker() -> None:
            try:
                response: Response = requests.get(url=Api.GitHub.MARKETPLACE, attempts=1)
                data: list[dict] = response.json()
                callback(data)
                return
            except (RequestException, RuntimeError):
                Logger.error(f"Marketplace data failed to load!")
                callback(None)
                return
        Thread(target=worker, daemon=True).start()


    def _get_thumbnail(self, id: str, url: str | None, thumbnail_hash: str | None) -> Image.Image | tuple[Image.Image, Image.Image]:
        def get_md5(path: Path) -> str:
            hasher = hashlib.md5()
            with open(path, "rb") as file:
                for chunk in iter(lambda: file.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()

        cache_directory: Path = Directory.CACHE / "marketplace"
        cached_image: Path = cache_directory / f"{id}.png"

        if cached_image.is_file() and thumbnail_hash is not None:
            thumbnail_hash = thumbnail_hash.upper()
            cached_image_hash = get_md5(cached_image).upper()

            if thumbnail_hash == cached_image_hash:
                try: return Image.open(cached_image)
                except (OSError, UnidentifiedImageError):
                    Logger.warning(f"Corrupted cache thumbnail: {id}", prefix="marketplace")
                    cached_image.unlink(missing_ok=True)

        if not url: return (self.placeholder_light, self.placeholder_dark)

        try:
            Logger.info(f"Downloading thumbnail: {id}", prefix="marketplace")
            response: Response = requests.get(url, attempts=1)

            with BytesIO(response.content) as buffer:
                image = Image.open(buffer)
                image.load()
            cache_directory.mkdir(parents=True, exist_ok=True)
            image.save(cached_image)
            return image

        except (RequestException, RuntimeError) as e:
            Logger.warning(f"Failed to download marketplace thumbnail: {id} | {type(e).__name__}: {e}", prefix="marketplace")

        except (IOError, UnidentifiedImageError) as e:
            Logger.warning(f"Failed to process marketplace thumbnail: {id} | {type(e).__name__}: {e}", prefix="marketplace")

        return (self.placeholder_light, self.placeholder_dark)


    def _scheduled_frame_creation(self, master, id: str, name: str, description: str | None, author: str | None, thumbnail: Image.Image | tuple[Image.Image, Image.Image], download_url: str, index: int) -> None:
        def _update_wraplength(event, name_label, description_label, author_label) -> None:
            wraplength: int = event.width - (2 * self.ENTRY_INNER_PADX)
            if wraplength == name_label.cget("wraplength"): return
            name_label.configure(wraplength=wraplength)
            if description_label is not None: description_label.configure(wraplength=wraplength)
            author_label.configure(wraplength=wraplength)

        def _update_thumbnail(event, thumbnail: Image.Image | tuple[Image.Image], top_label, aspect_ratio: float= self._MOD_THUMBNAIL_ASPECT_RATIO) -> None:
            def _add_rounded_corners(image: Image.Image) -> Image.Image:
                image = image.convert("RGBA")

                mask = self.thumbnail_mask.split()[-1]
                mask_w, mask_h = mask.size
                corner_w, corner_h = mask_w//2, mask_h//2

                top_left = mask.crop((0, 0, corner_w, corner_h))
                top_right = mask.crop((corner_w, 0, mask_w, corner_h))
                bottom_left = mask.crop((0, corner_h, corner_w, mask_h))
                bottom_right = mask.crop((corner_w, corner_h, mask_w, mask_h))

                image_w, image_h = image.size
                final_mask = Image.new("L", (image_w, image_h), 255)
                final_mask.paste(top_left, (0, 0))
                final_mask.paste(top_right, (image_w - corner_w, 0))
                final_mask.paste(bottom_left, (0, image_h - corner_h))
                final_mask.paste(bottom_right, (image_w - corner_w, image_h - corner_h))

                rounded = Image.new("RGBA", (image_w, image_h))
                rounded.paste(image, (0, 0), final_mask)
                return rounded

            def _resize_and_crop(thumbnail: Image.Image, size: tuple[int, int]) -> Image.Image:
                if size == thumbnail.size: return thumbnail.copy()
                w, h = thumbnail.size
                ratio = w/h
                new_h = int(size[0]/ratio)
                method = Image.LANCZOS if w > size[0] else Image.BICUBIC
                resized = thumbnail.resize((size[0], new_h), method)
                if new_h > size[1]:
                    excess = new_h - size[1]
                    margin = excess//2
                    resized = resized.crop((0, margin, size[0], size[1]+margin))
                return resized

            def _get_resized_thumbnail(thumbnail: Image.Image | tuple[Image.Image], size: tuple[int, int]) -> ctk.CTkImage:
                if isinstance(thumbnail, tuple):
                    light, dark = thumbnail
                    resized_light = _resize_and_crop(light, size)
                    resized_light = _add_rounded_corners(resized_light)
                    resized_dark = _resize_and_crop(dark, size)
                    resized_dark = _add_rounded_corners(resized_dark)
                    return ctk.CTkImage(resized_light, resized_dark, size=size)
                resized = _resize_and_crop(thumbnail, size)
                resized = _add_rounded_corners(resized)
                return ctk.CTkImage(resized, size=size)

            width: int = (event.width - (2 * self.ENTRY_INNER_PADX))
            height: int = int(width/aspect_ratio)
            if height == top_label.cget("height"): return

            new_thumbnail: ctk.CTkImage = _get_resized_thumbnail(thumbnail, (width, height))
            top_label.configure(height=height, width=width)
            top_label.configure(image=new_thumbnail)

        column: int = self._get_grid_column(index)
        row: int = self._get_grid_row(index)

        frame = FluentButtonFrame(master, command=lambda id=id, name=name, download_url=download_url: self._download_mod(id, name, download_url), toplevel=True)
        frame.grid_columnconfigure(0, weight=1)

        top_label = ctk.CTkLabel(frame, fg_color="transparent", text="", image=None)
        top_label.grid(column=0, row=0, padx=self.ENTRY_INNER_PADX, pady=(self.ENTRY_INNER_PADY, 0), sticky="nsew")

        bottom_frame = ctk.CTkFrame(frame, fg_color="transparent")

        name_label = FluentLabel(bottom_frame, name, font_weight="bold", font_size=14, justify="left")
        name_label.grid(column=0, row=0, sticky="w")
        description_label = None
        if description:
            description_label = FluentLabel(bottom_frame, description, font_size=13, slant="italic", justify="left")
            description_label.grid(column=0, row=1, sticky="w")
        author_label = FluentLabel(bottom_frame, Localizer.strings["menu.marketplace"]["author_unknown"] if not author else Localizer.strings["menu.marketplace"]["author"].replace("{author}", author), font_size=12, justify="left")
        author_label.grid(column=0, row=2, sticky="w")

        bottom_frame.grid(column=0, row=1, padx=self.ENTRY_INNER_PADX, pady=self.ENTRY_INNER_PADY, sticky="nsew")

        frame.grid(column=column, row=row, pady=0 if row == 0 else (self.ENTRY_GAP, 0), sticky="nsew")

        # Debounce, without it everything breaks
        frame.wraplength_update_id = None
        frame.thumbnail_update_id = None
        def on_configure(event, name_label, description_label, author_label, top_label, thumbnail):
            if frame.wraplength_update_id: master.after_cancel(frame.wraplength_update_id)
            if frame.thumbnail_update_id: master.after_cancel(frame.thumbnail_update_id)
            frame.wraplength_update_id = master.after(self._DEBOUNCE, _update_wraplength, event, name_label, description_label, author_label)
            frame.thumbnail_update_id = master.after(self._DEBOUNCE, _update_thumbnail, event, thumbnail, top_label)
        frame.bind("<Configure>", lambda event, name_label=name_label, description_label=description_label, author_label=author_label, top_label=top_label, thumbnail=thumbnail: on_configure(event, name_label, description_label, author_label, top_label, thumbnail))

    def _get_grid_column(self, i: int) -> int:
        return (i%self.COLUMNS)*2

    def _get_grid_row(self, i: int) -> int:
        return i//self.COLUMNS

    def _download_mod(self, id: str, name: str, download_url: str) -> None:
        def worker(id: str, name: str, url: str) -> None:
            def on_progress(downloaded: int, total: int, window: ModDownloadWindow) -> None:
                if window.progress_bar.winfo_exists(): self.root.after(0, window.progress_bar.set, downloaded/total)

            def callback(command: Callable, temporary_directory: Path, window: ModDownloadWindow) -> None:
                time.sleep(0.5)
                try:
                    window.destroy()
                    command()
                except TclError:
                    pass
                try:
                    Logger.info(f"Removing temporary directory...", prefix=f"marketplace._download_mod({id})")
                    shutil.rmtree(temporary_directory)
                except Exception as e:
                    Logger.warning(f"Failed to remove temporary directory: {temporary_directory.resolve()} | {type(e).__name__}: {e}", prefix=f"marketplace._download_mod({id})")
                self._is_downloading = False

            def on_success(path: Path, name: str) -> None:
                Logger.info(f"Download success, extracting files...", prefix=f"marketplace._download_mod({id})")
                self._import_mod(path, name)

            def on_error(e: Exception) -> None:
                if isinstance(e, DownloadInProgressError):
                    Logger.error(f"Failed to download {id} | Another download is in progress", prefix=f"marketplace._download_mod({id})")
                    self.root.after(0, lambda: messagebox.show_warning(Localizer.strings["popups"]["marketplace"]["download_in_progress.title"], Localizer.strings["popups"]["marketplace"]["download_in_progress.message"], blocking=False))

                elif isinstance(e, DownloadPermissionError):
                    Logger.error(f"Failed to download {id} | {e}", prefix=f"marketplace._download_mod({id})")
                    self.root.after(0, lambda: messagebox.show_error(Localizer.strings["errors"]["marketplace"]["download.title"], Localizer.strings["errors"]["marketplace"]["download.permission_denied"].replace("{path}", str(e.path.resolve())).replace("{error}", f"{type(e).__name__}: {e}"), blocking=False))

                elif isinstance(e, DownloadSocketTimeoutError):
                    Logger.error(f"Failed to download {id} | {e}", prefix=f"marketplace._download_mod({id})")
                    self.root.after(0, lambda: messagebox.show_error(Localizer.strings["errors"]["marketplace"]["download.title"], Localizer.strings["errors"]["marketplace"]["download.timeout"].replace("{timeout}", str(e.timeout)).replace("{error}", f"{type(e).__name__}: {e}"), blocking=False))

                elif isinstance(e, DownloadHTTPError):
                    Logger.error(f"Failed to download {id} | Connection error: {e}", prefix=f"marketplace._download_mod({id})")
                    self.root.after(0, lambda: messagebox.show_error(Localizer.strings["errors"]["marketplace"]["download.title"], Localizer.strings["errors"]["marketplace"]["download.http_error"].replace("{code}", str(e.code)).replace("{reason}", e.reason), blocking=False))
                
                elif isinstance(e, DownloadConnectionError):
                    Logger.error(f"Failed to download {id} | Connection error: {e}", prefix=f"marketplace._download_mod({id})")
                    self.root.after(0, lambda: messagebox.show_error(Localizer.strings["errors"]["marketplace"]["download.title"], Localizer.strings["errors"]["marketplace"]["download.connection_failed"], blocking=False))

                elif isinstance(e, ConnectionResetError):
                    Logger.error(f"Failed to download {id} | Connection reset!", prefix=f"marketplace._download_mod({id})")
                    self.root.after(0, lambda: messagebox.show_error(Localizer.strings["errors"]["marketplace"]["download.title"], Localizer.strings["errors"]["marketplace"]["download.connection_reset"], blocking=False))

                elif isinstance(e, SSLError):
                    Logger.error(f"Failed to download {id} | SSL handshake failed!", prefix=f"marketplace._download_mod({id})")
                    self.root.after(0, lambda: messagebox.show_error(Localizer.strings["errors"]["marketplace"]["download.title"], Localizer.strings["errors"]["marketplace"]["download.ssl_handshake_failed"], blocking=False))

                else:
                    Logger.error(f"Failed to download {id} | {type(e).__name__}: {e}", prefix=f"marketplace._download_mod({id})")
                    self.root.after(0, lambda: messagebox.show_error(Localizer.strings["errors"]["marketplace"]["download.title"], Localizer.strings["errors"]["marketplace"]["download.other"].replace("{mod}", name).replace("{error}", f"{type(e).__name__}: {e}"), blocking=False))

            Logger.info(f"Downloading mod: {id}")
            window: ModDownloadWindow = ModDownloadWindow(get_root_instance(), self.favicon, name)

            tmp = tempfile.mkdtemp()
            temporary_directory: Path = Path(tmp)
            Logger.info(f"Created temporary directory: {temporary_directory.resolve()}", prefix=f"marketplace._download_mod({id})")
            
            Logger.info(f"Starting download: {download_url}", prefix=f"marketplace._download_mod({id})")
            target: Path = temporary_directory / "mod.zip"
            download_handler: StreamedDownloadHandler = StreamedDownloadHandler(on_success=lambda: callback(lambda: on_success(target, name), temporary_directory, window), on_error=lambda e: callback(lambda: on_error(e), temporary_directory, window), on_progress=lambda downloaded, total: on_progress(downloaded, total, window))
            download_handler.download_file(url, target, chunk_size=1024*100)

        if self._is_downloading:
            self.root.after(0, lambda: messagebox.show_warning(Localizer.strings["popups"]["marketplace"]["download_in_progress.title"], Localizer.strings["popups"]["marketplace"]["download_in_progress.message"], blocking=False))
            return

        self._is_downloading = True
        Thread(target=worker, args=(id, name, download_url), daemon=True).start()
    

    def _import_mod(self, source: Path, name: str) -> None:
        try:
            target = Directory.MODS / name
            n = 1
            while target.exists():
                target = Directory.MODS / f"{name} ({n})"
                n += 1

            filesystem.extract(source, target)

        except ExtractPermissionError as e:
            self.root.after(0, lambda: messagebox.show_error(Localizer.strings["errors"]["marketplace"]["download.title"], Localizer.strings["errors"]["marketplace"]["download.permission_denied"].replace("{path}", e.path), blocking=False))
            return
# endregion
