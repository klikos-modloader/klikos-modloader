from typing import Optional

from ..basic.frame import Frame

from customtkinter import ScalingTracker  # type: ignore


class FlexBox(Frame):
    available_width: int = -1
    gap: int
    column_width: int
    row_height: int
    frame_layer: int

    _update_id: Optional[str] = None
    _debounce: int = 100

    _id_counter: int = 0
    _frames: dict[str, Frame]


    def __init__(self, master, column_width: int, row_height: int, gap: int = 8, transparent: bool = False, layer: int = 0, **kwargs):
        super().__init__(master, transparent=transparent, round=transparent, border=transparent, layer=layer, **kwargs)
        self.column_width = column_width
        self.row_height = row_height
        self.gap = gap
        self._frames = {}
        self.frame_layer = layer + 1
        self.bind("<Configure>", self._on_configure)


    def add_item(self) -> Frame:
        self._id_counter += 1
        id: str = str(self._id_counter)
        frame: Frame = Frame(self, layer=self.frame_layer, width=self.column_width, height=self.row_height)
        frame.grid_propagate(False)
        setattr(frame, "id", id)

        self._frames[id] = frame
        self.after(10, self._update_layout)
        return frame


    def remove_item(self, item_or_id: str | Frame) -> None:
        if isinstance(item_or_id, str): id: str = item_or_id
        elif hasattr(item_or_id, "id"): id = item_or_id.id
        else: return

        item: Frame | None = self._frames.pop(id, None)
        if item and item.winfo_exists(): item.destroy()
        self._update_layout()


    def _on_configure(self, event) -> None:
        self.available_width = event.width
        if self._update_id is not None: self.after_cancel(self._update_id)
        self._update_id = self.after(self._debounce, self._update_layout)


    def _update_layout(self) -> None:
        if not self._frames: return
        if self.available_width < 0: return

        total_width: int = int(self.available_width / ScalingTracker.get_widget_scaling(self))
        column_width: int = self.column_width
        gap: int = self.gap

        columns: int = max(1, (total_width + gap) // (column_width + gap))
        self.grid_columnconfigure(list(range(columns)), minsize=column_width+gap)
        self.grid_columnconfigure(0, minsize=column_width)

        for i, frame in enumerate(list(self._frames.values())):
            column: int = i % columns
            row: int = i // columns
            padx: int | tuple[int, int] = 0 if column == 0 else (gap, 0)
            pady: int | tuple[int, int] = 0 if row == 0 else (gap, 0)

            if getattr(frame, "column", None) != column or getattr(frame, "row", None) != row:
                setattr(frame, "column", column)
                setattr(frame, "row", row)
                frame.grid(column=column, row=row, padx=padx, pady=pady, sticky="nsew")