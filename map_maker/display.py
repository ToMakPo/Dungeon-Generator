from tkinter import *

from map_maker.dungeon import Dungeon
from my_global import *


class MasterDisplay:
    def __init__(self, title='Map Maker (Dungeon Master)'):
        self.window = Tk()
        self.window.title(title)
        self.dungeon = Dungeon(self.window)

        self.seed_value = IntVar(value=self.dungeon.active_seed)
        self.random_seed = BooleanVar(value=True)

        self.grid_columns = IntVar(value=self.dungeon.grid_size.columns)
        self.grid_rows = IntVar(value=self.dungeon.grid_size.rows)
        self.canvas_width = IntVar(value=self.dungeon.canvas_size.width)
        self.canvas_height = IntVar(value=self.dungeon.canvas_size.height)
        self.cell_size = IntVar(value=self.dungeon.cell_size)
        self.padding = IntVar(value=self.dungeon.padding)
        self.dynamic_size = BooleanVar(value=True)

        self.top_floor = IntVar(value=self.dungeon.top_floor)
        self.random_top = BooleanVar(value=True)
        self.bottom_floor = IntVar(value=self.dungeon.bottom_floor)
        self.random_bottom = BooleanVar(value=True)

        self.current_floor = 0

        self.create_side_bar()
        self.map: Canvas = self.dungeon.draw(0)
        self.generate_map()
        self.map.grid(sticky=NW, row=0, column=2)

    def create_side_bar(self):
        container_padding = 5
        side_bar = Frame(self.window, padx=container_padding, pady=container_padding)

        def make_seed():
            # seed container
            seed_container = Frame(side_bar, pady=container_padding)

            # seed label
            Label(seed_container, text='Seed').grid(sticky=W, row=0, columnspan=2)

            # seed input
            seed_input = NumBox(seed_container, from_=0, to=SYS_MAX, state=DISABLED, textvariable=self.seed_value)
            seed_input.grid(sticky=W, row=1, column=0)

            # seed random check box
            def toggle_seed_random():
                if self.random_seed.get():
                    self.seed_value.set(self.dungeon.active_seed)
                    seed_input.config(state=DISABLED)
                else:
                    seed_input.config(state=NORMAL)
                    seed_input.focus_set()
                    seed_input.selection_range(0, END)
                    seed_input.icursor(END)

            Checkbutton(seed_container, text='get random', variable=self.random_seed, command=toggle_seed_random) \
                .grid(sticky=E, row=1, column=1)

            seed_container.grid(sticky=W, row=0)

        def make_size():
            ''' GRID '''
            # grid container
            grid_container = Frame(side_bar, pady=container_padding)

            # grid size title
            Label(grid_container, text='Grid').grid(sticky=W, row=0, column=0, columnspan=2)

            # grid column label
            Label(grid_container, text='Columns').grid(sticky=W, row=1, column=0)

            # grid column input
            columns_input = NumBox(grid_container, from_=6, to=SYS_MAX, textvariable=self.grid_columns)
            columns_input.grid(sticky=W, row=2, column=0)

            # grid row label
            Label(grid_container, text='Rows').grid(sticky=W, row=1, column=1)

            # grid row input
            rows_input = NumBox(grid_container, from_=6, to=SYS_MAX, textvariable=self.grid_rows)
            rows_input.grid(sticky=W, row=2, column=1)

            grid_container.grid(sticky=W, row=1)

            ''' CANVAS '''
            # canvas container
            canvas_container = Frame(side_bar, pady=container_padding)

            # canvas size title
            Label(canvas_container, text='Canvas').grid(sticky=W, row=0, column=0, columnspan=2)

            # canvas width label
            Label(canvas_container, text='Width').grid(sticky=W, row=1, column=0)

            # canvas width input
            width_input = NumBox(canvas_container, from_=6 * self.cell_size.get(), state=DISABLED, to=SYS_MAX,
                                 textvariable=self.canvas_width)
            width_input.grid(sticky=W, row=2, column=0)

            # canvas height label
            Label(canvas_container, text='Height').grid(sticky=W, row=1, column=1)

            # canvas height input
            height_input = NumBox(canvas_container, from_=6 * self.cell_size.get(), state=DISABLED, to=SYS_MAX,
                                  textvariable=self.canvas_height)
            height_input.grid(sticky=W, row=2, column=1)

            canvas_container.grid(sticky=W, row=2)

            ''' OTHER '''
            # other container
            other_container = Frame(side_bar, pady=container_padding)

            # grid column label
            Label(other_container, text='Cell Size').grid(sticky=W, row=0, column=0)

            # grid column input
            cell_size_input = NumBox(other_container, from_=6, to=SYS_MAX, textvariable=self.cell_size)
            cell_size_input.grid(sticky=W, row=1, column=0)

            # grid row label
            Label(other_container, text='Padding').grid(sticky=W, row=0, column=1)

            # grid row input
            padding_input = NumBox(other_container, from_=0, to=SYS_MAX, textvariable=self.padding)
            padding_input.grid(sticky=W, row=1, column=1)

            # dynamic size check box
            def toggle_dynamic_size():
                if self.dynamic_size.get():
                    columns_input.config(state=NORMAL)
                    rows_input.config(state=NORMAL)
                    padding_input.config(state=NORMAL)
                    self.padding.set(self.dungeon.padding)
                    columns_input.focus_set()
                    columns_input.selection_range(0, END)
                    columns_input.icursor(END)

                    self.canvas_width.set(self.dungeon.canvas_size.width)
                    width_input.config(state=DISABLED)
                    self.canvas_height.set(self.dungeon.canvas_size.height)
                    height_input.config(state=DISABLED)
                else:
                    width_input.config(state=NORMAL)
                    height_input.config(state=NORMAL)
                    width_input.focus_set()
                    width_input.selection_range(0, END)
                    width_input.icursor(END)

                    self.grid_columns.set(self.dungeon.grid_size.columns)
                    columns_input.config(state=DISABLED)
                    self.grid_rows.set(self.dungeon.grid_size.rows)
                    rows_input.config(state=DISABLED)
                    self.padding.set("AUTO")
                    padding_input.config(state=DISABLED)

            Checkbutton(other_container, text='dynamic size', variable=self.dynamic_size, command=toggle_dynamic_size)\
                .grid(sticky=E, row=2, column=1)

            other_container.grid(sticky=W, row=3)

        def make_floors():
            # floor container
            floor_container = Frame(side_bar, pady=container_padding)

            # floor title
            Label(floor_container, text='Floor').grid(sticky=W, row=0, column=0, columnspan=2)

            # top label
            Label(floor_container, text='Top').grid(sticky=W, row=1, column=0)

            # top input
            top_input = NumBox(floor_container, from_=0, to=SYS_MAX, state=DISABLED, textvariable=self.top_floor)
            top_input.grid(sticky=W, row=2, column=0)

            # bottom label
            Label(floor_container, text='Bottom').grid(sticky=W, row=1, column=1)

            # bottom input
            bottom_input = NumBox(floor_container, from_=-SYS_MAX, to=0, state=DISABLED, textvariable=self.bottom_floor)
            bottom_input.grid(sticky=W, row=2, column=1)

            # random top
            def toggle_random_top():
                if self.random_top.get():
                    self.top_floor.set(self.dungeon.top_floor)
                    top_input.config(state=DISABLED)
                else:
                    top_input.config(state=NORMAL)
            Checkbutton(floor_container, text='random', variable=self.random_top, command=toggle_random_top)\
                .grid(sticky=E, row=3, column=0)

            # random bottom
            def toggle_random_bottom():
                if self.random_bottom.get():
                    self.bottom_floor.set(self.dungeon.bottom_floor)
                    bottom_input.config(state=DISABLED)
                else:
                    bottom_input.config(state=NORMAL)
            Checkbutton(floor_container, text='random', variable=self.random_bottom, command=toggle_random_bottom)\
                .grid(sticky=E, row=3, column=1)

            floor_container.grid(sticky=W, row=4)

        def make_button():
            Button(side_bar, text='GENERATE MAP', command=self.generate_map).grid(sticky=E, row=15)

        make_seed()
        make_size()
        make_floors()
        make_button()

        side_bar.grid(sticky=NW, row=0, column=0)

        floor_toggle_container = Frame(self.window, padx=container_padding, pady=container_padding)
        fs = 15

        self.increment_floor_button = Button(floor_toggle_container, text='p', font=('Wingdings 3', fs),
                                             command=self.increment_floor)
        self.increment_floor_button.pack()
        self.floor_number_label = Label(floor_toggle_container, text='0', font=('Calibri', fs))
        self.floor_number_label.pack()
        self.decrement_floor_button = Button(floor_toggle_container, text='q', font=('Wingdings 3', fs),
                                             command=self.decrement_floor)
        self.decrement_floor_button.pack()
        self.change_floor(to=0)
        floor_toggle_container.grid(sticky=NW, row=0, column=1)

    def generate_map(self):
        self.current_floor = 0
        if self.random_seed.get():
            seed = self.dungeon.set_seed(-1)
            self.seed_value.set(seed)
        else:
            self.dungeon.set_seed(self.seed_value.get())

        if self.dynamic_size.get():
            self.dungeon.set_size(**{
                'grid_columns': self.grid_columns.get(),
                'grid_rows': self.grid_rows.get(),
                'canvas_width': -1,
                'canvas_height': -1,
                'cell_size': self.cell_size.get(),
                'padding': self.padding.get()
            })
            self.padding.set(self.dungeon.padding)
        else:
            self.dungeon.set_size(**{
                'canvas_width': self.canvas_width.get(),
                'canvas_height': self.canvas_height.get(),
                'cell_size': self.cell_size.get()
            })
        self.canvas_width.set(self.dungeon.canvas_size.width)
        self.canvas_height.set(self.dungeon.canvas_size.height)
        self.grid_columns.set(self.dungeon.grid_size.columns)
        self.grid_rows.set(self.dungeon.grid_size.rows)
        self.cell_size.set(self.dungeon.cell_size)

        fn = ["", ""]
        if not self.random_top.get():
            fn[0] = self.top_floor.get()
        if not self.random_bottom.get():
            fn[1] = self.bottom_floor.get()
        fn = self.dungeon.set_floors(*fn)
        self.top_floor.set(fn[0])
        self.bottom_floor.set(fn[1])

        self.change_floor(to=0)

        self.draw_map()

    def increment_floor(self):
        if self.current_floor < self.dungeon.top_floor:
            self.change_floor(1)

    def decrement_floor(self):
        if self.current_floor > self.dungeon.bottom_floor:
            self.change_floor(-1)

    def change_floor(self, by=0, to=None):
        if to is None:
            self.current_floor += by
        else:
            self.current_floor = to
        self.draw_map()
        self.floor_number_label.config(text=self.current_floor)
        if self.current_floor == self.dungeon.top_floor:
            self.increment_floor_button.config(state=DISABLED, text='r')
        else:
            self.increment_floor_button.config(state=NORMAL, text='p')

        if self.current_floor == self.dungeon.bottom_floor:
            self.decrement_floor_button.config(state=DISABLED, text='s')
        else:
            self.decrement_floor_button.config(state=NORMAL, text='q')

    def draw_map(self):
        self.map = self.dungeon.draw(self.current_floor)

    def show(self):
        self.window.mainloop()


class NumBox(Spinbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        def check_input(event):
            v = event.char
            try:
                if v != "\x08" and v != "":
                    _ = int(v)
            except ValueError:
                return "break"

        self.bind('<Key>', check_input)
