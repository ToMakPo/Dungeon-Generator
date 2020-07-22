from __future__ import annotations

from tkinter import *

from my_global import *

DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right


class Dungeon:
    """ A customisable randomly generated dungeon map for role playing games like D&D. """
    class CanvasSize: width = height = area = 0
    class GridSize: columns = rows = area = 0
    class PaddingSize: top = bottom = left = right = 0

    built = False

    rand = np.random
    seed = None
    active_seed = None

    grid_columns = None
    grid_rows = None
    grid_size = GridSize
    canvas_width = None
    canvas_height = None
    canvas_size = CanvasSize
    cell_size = None
    padding = None
    padding_size = PaddingSize

    top_floor = 0
    bottom_floor = 0
    floors = {}

    tile_count = 0
    tile_percent = 0

    chains = {}
    links = {}

    def __init__(self, window=None,
                 grid_columns: int = 50, grid_rows: int = 35,
                 canvas_width: int = -1, canvas_height: int = -1,
                 cell_size: int = 25, padding: int = 15,
                 top_floor: int = "", bottom_floor: int = "",
                 tile_count: int = 0, tile_percent: float = 0.2,
                 seed: int = -1, ):
        """
        Create a new dungeon.

        :param window: the tkinter window that the dungeon will be displayed in.
        :param grid_columns: the number of columns for the grid that the map will be on. Must be at minimum 6 cells.
            Will be ignored if pixel_width is not -1. (default 50 columns)
        :param grid_rows: the number of rows for the grid that the map will be on. Must be at minimum 6 cells. Will be
            ignored if pixel_height is not -1. (default 35 rows)
        :param canvas_width: The width of the map in pixels. Must be at minimum 6 cells. If set to -1, then
            pixel width will calculated using grid_width. (default -1)
        :param canvas_height: The height of the map in pixels. Must be at minimum 6 cells. If set to -1, then
            pixel height will calculated using grid_height. (default -1)
        :param cell_size: the width/height of the cells in pixels that make up the grid. Mist be at minimum 5 px. 
            (default 25 px)
        :param padding: the padding in pixels around the edge of the map. Padding will be calculated automatically when
            using pixel_width or pixel_height. Must be at minimum 0 px. (default 15 px)
        :param top_floor: the upper most floor of your dungeon. Minimum top floor must be 0 (ground floor). You can make
            the tower be more than one story tall. Use "" to get a random normal distribution (sd of 3)
            number of floors. (default "")
        :param bottom_floor: the lower most floor of your dungeon. Maximum bottom floor must be 0 (ground floor); the
            number should be a negative number. You can make the cavern be more than one level deep. Use ""
            to get a random normal distribution (sd of 5) number of floors. (default "")
        :param tile_count: the number of floor tiles that will be created. Must have a minimum of 1 and a maximum
            of the total grid area. Anything above that will be ignored. Use negative numbers to get that number fewer
            then the total grid area. Enter 0 to use the tile_percent instead. (default 0)
        :param tile_percent: the percentage of the map that will get used. If tile_count is not 0, then this will
            ignored. Must be between 0.0 (0%) and 1.0 (100%). (default 0.2 (20%))
        :param seed: the seed to be used. Use -1 or "" to set the seed to
            random. Otherwise, seed needs to be between 0 and 2,147,483,647. (default -1)
        """
        self.window: Tk = window
        self.set_seed(seed)
        self.set_size(grid_columns, grid_rows, canvas_width, canvas_height, cell_size, padding)
        self.set_floors(top_floor, bottom_floor)
        self.set_tile_count(tile_count, tile_percent)

        self.canvas: Canvas = Canvas(self.window, width=self.canvas_size.width, height=self.canvas_size.height)

    def set_seed(self, seed: int = None):
        """
        Change the seed used for the random number generator for this dungeon.

        :param seed: the seed to be used. Use -1 or "" to set the seed to
            random. Otherwise, seed needs to be between 0 and 2,147,483,647. (default current seed)
        :return the active seed
        """
        if seed is not None:
            self.seed = seed

        if seed in (-1, ""):
            self.active_seed = np.random.randint(MAX32)
        else:
            self.active_seed = clamp(int(self.seed))

        self.rand.seed(self.active_seed)

        self.built = False
        return self.active_seed

    def set_size(self, grid_columns: int = None, grid_rows: int = None,
                 canvas_width: int = None, canvas_height: int = None,
                 cell_size: int = None, padding: int = None):
        """
        Set the size of the grid and the map.

        :param grid_columns: the number of columns for the grid that the map will be on. Must be at minimum 6 cells.
            Will be ignored if pixel_width is not -1. (default current grid_width)
        :param grid_rows: the number of rows for the grid that the map will be on. Must be at minimum 6 cells. Will be
            ignored if pixel_height is not -1. (default current grid_height)
        :param canvas_width: The width of the map in pixels. Must be at minimum 6 cells. If set to -1, then
            pixel width will calculated using grid_width. (default current pixel_width)
        :param canvas_height: The height of the map in pixels. Must be at minimum 6 cells. If set to -1, then
            pixel height will calculated using grid_height. (default current pixel_height)
        :param cell_size: the width/height of the cells in pixels that make up the grid. Mist be at minimum 5 px.
            (default current cell_size)
        :param padding: the padding in pixels around the edge of the map. Padding will be calculated automatically when
            using pixel_width or pixel_height. Must be at minimum 0 px. (default current padding)
        :return the grid size, the canvas size, the cell size, and the padding
        """
        if cell_size is not None:
            self.cell_size = clamp(int(cell_size), 5)
        if grid_columns is not None:
            self.grid_columns = clamp(int(grid_columns), 6)
        if grid_rows is not None:
            self.grid_rows = clamp(int(grid_rows), 6)
        if canvas_width is not None:
            self.canvas_width = clamp(int(canvas_width), 6 * self.cell_size) if canvas_width != -1 else -1
        if canvas_height is not None:
            self.canvas_height = clamp(int(canvas_height), 6 * self.cell_size) if canvas_height != -1 else -1
        if padding is not None:
            self.padding = clamp(int(padding))

        if self.canvas_width == -1:
            self.grid_size.columns = self.grid_columns
            self.canvas_size.width = self.grid_columns * self.cell_size + self.padding * 2
            self.padding_size.left = self.padding
            self.padding_size.right = self.padding
        else:
            self.canvas_size.width = self.canvas_width
            self.grid_size.columns = int(self.canvas_width / self.cell_size)
            padding = (self.canvas_size.width - self.grid_size.columns * self.cell_size) / 2
            self.padding_size.left = padding
            self.padding_size.right = padding

        if self.canvas_height == -1:
            self.grid_size.rows = self.grid_rows
            self.canvas_size.height = self.grid_rows * self.cell_size + self.padding * 2
            self.padding_size.top = self.padding
            self.padding_size.bottom = self.padding
        else:
            self.canvas_size.height = self.canvas_height
            self.grid_size.rows = int(self.canvas_height / self.cell_size)
            padding = (self.canvas_size.height - self.grid_size.rows * self.cell_size) / 2
            self.padding_size.top = padding
            self.padding_size.bottom = padding

        self.grid_size.area = self.grid_size.columns * self.grid_size.columns
        self.canvas_size.area = self.canvas_size.height * self.canvas_size.width
        self.built = False
        return self.grid_size, self.canvas_size, self.cell_size, self.padding

    def set_floors(self, top_floor: int = None, bottom_floor: int = None):
        """
        Set the upper and lower floor numbers and recreate the floors.

        :param top_floor: the upper most floor of your dungeon. Minimum top floor must be 0 (ground floor). You can make
            the tower be more than one story tall. Use "" to get a random normal distribution (sd of 3)
            number of floors. (default current top_floor)
        :param bottom_floor: the lower most floor of your dungeon. Maximum bottom floor must be 0 (ground floor); the
            number should be a negative number. You can make the cavern be more than one level deep. Use ""
            to get a random normal distribution (sd of 5) number of floors. (default current bottom_floor)
        :return the top floor number and the bottom floor number
        """
        if top_floor is not None:
            if top_floor == "":
                top_floor = abs(round(self.rand.normal(0, 3)))
            self.top_floor = abs(int(top_floor))
        if bottom_floor is not None:
            if bottom_floor == "":
                bottom_floor = -abs(round(self.rand.normal(0, 4)))
            self.bottom_floor = -abs(int(bottom_floor))
        self.built = False
        return top_floor, bottom_floor

    def set_tile_count(self, tile_count: int = None, tile_percent: float = None):
        """
        Set the number of floor tiles that will will added to the map.

        :param tile_count: the number of floor tiles that will be created. Must have a minimum of 1 and a maximum
            of the total grid area. Anything above that will be ignored. Use negative numbers to get that number fewer
            then the total grid area. Enter 0 to use the tile_percent instead. (default current tile_count)
        :param tile_percent: the percentage of the map that will get used. If tile_count is not 0, then this will
            ignored. Must be between 0.0 (0%) and 1.0 (100%). (default current tile_percent)
        :return the tile count and tile percent
        """
        if tile_count is not None:
            self.tile_count = int(tile_count)
        if tile_percent is not None:
            self.tile_percent = clamp_float(float(tile_percent), 0.0, 1.0)
        self.built = False
        return tile_count, tile_percent

    def build(self):
        """ Build the maps. """
        self.floors.clear()
        self.chains.clear()
        self.links.clear()

        for floor_number in range(self.bottom_floor, self.top_floor + 1):
            self.floors[floor_number] = self.Floor(self, floor_number)
            self.chains[floor_number] = {}
            self.links[floor_number] = {}

        for _ in range(abs(round(self.rand.normal(0, 1))) + 1):  # create a random number of entries
            while True:
                wall = DIRECTIONS[self.rand.randint(4)]
                column, row = wall

                if column == 0:
                    size = self.grid_size.columns - 1
                    mean = size / 2
                    sd = mean / 3
                    column = clamp(round(self.rand.normal(mean, sd)), 2, size - 2)
                    row = int((row + 1) / 2) * (self.grid_size.rows - 1)
                else:
                    size = self.grid_size.rows - 1
                    mean = size / 2
                    sd = mean / 3
                    row = clamp(round(self.rand.normal(mean, sd)), 2, size - 2)
                    column = int((column + 1) / 2) * (self.grid_size.columns - 1)

                if self.floors[0].grid[row][column].name == 'wall':
                    chain: list = []
                    chain_id = len(self.chains[0])
                    direction = [w * -1 for w in wall]
                    etw = Dungeon.EntryTile(self, self.floors[0], row, column, direction)
                    self.floors[0].grid[row][column] = etw
                    last_link = Dungeon.Link(etw, chain_id, direction)
                    chain.append(last_link)
                    self.chains[0][chain_id] = chain
                    self.links[0][column, row] = last_link
                    break

        c_total = self.grid_size.columns - 1
        c_mean = c_total / 2
        c_sd = c_mean / 3
        r_total = self.grid_size.rows - 1
        r_mean = r_total / 2
        r_sd = r_mean / 3

        for floor_number in range(self.bottom_floor, self.top_floor):
            next_floor = floor_number + 1
            for _ in range(abs(round(self.rand.normal(0, 1))) + 1):  # create a random number of staircases
                while True:
                    column = clamp(int(self.rand.normal(c_mean, c_sd)), 1, c_total - 1)
                    row = clamp(int(self.rand.normal(r_mean, r_sd)), 1, r_total - 1)

                    if self.floors[floor_number].grid[row][column].name == 'wall':
                        chain1: list = []
                        chain_id1 = len(self.chains[floor_number])
                        scu = Dungeon.StaircaseUpTile(self, self.floors[floor_number], row, column)
                        self.floors[floor_number].grid[row][column] = scu
                        link1 = Dungeon.Link(scu, chain_id1, DIRECTIONS[self.rand.randint(4)])
                        chain1.append(link1)
                        self.chains[floor_number][chain_id1] = chain1
                        self.links[floor_number][column, row] = link1

                        chain2: list = []
                        chain_id2 = len(self.chains[next_floor])
                        scd = Dungeon.StaircaseDownTile(self, self.floors[next_floor], row, column)
                        self.floors[next_floor].grid[row][column] = scd
                        link2 = Dungeon.Link(scd, chain_id2, DIRECTIONS[self.rand.randint(4)])
                        chain2.append(link2)
                        self.chains[next_floor][chain_id2] = chain2
                        self.links[next_floor][column, row] = link2
                        break

        if self.tile_count == 0:
            total_links = round(self.grid_size.area * self.tile_percent)
        else:
            total_links = clamp(self.tile_count if self.tile_count > 0 else self.grid_size.area + self.tile_count, 0,
                                self.grid_size.area)

        for floor_number, chains in self.chains.items():
            while len(self.links[floor_number]) < total_links or len(chains) > 1:
                for chain_id, chain in list(chains.items()):
                    if chain_id in chains:
                        last_link = chain[self.rand.randint(-1, 0)]
                        column = last_link.column
                        row = last_link.row

                        if self.rand.randint(5) == 0:  # 1/n chance of changing directions
                            direction = DIRECTIONS[self.rand.randint(4)]
                        else:
                            direction = last_link.direction

                        while True:
                            if 0 <= column + direction[0] < self.grid_size.columns and \
                                    0 <= row + direction[1] < self.grid_size.rows:  # not out of bounds
                                column = column + direction[0]
                                row = row + direction[1]
                                if self.floors[floor_number].grid[row][column].name == 'wall':  # is a wall tile
                                    flt = Dungeon.FloorTile(self, self.floors[0], row, column)
                                    self.floors[floor_number].grid[row][column] = flt
                                    link = Dungeon.Link(flt, chain_id, direction)
                                    chain.append(link)
                                    self.links[floor_number][column, row] = link

                                    for c, r in DIRECTIONS:
                                        key = (column + c, row + r)
                                        if key in self.links[floor_number]:
                                            other: Dungeon.Link = self.links[floor_number][key]
                                            if other.tile.name != 'wall' and other.chain_id != chain_id:
                                                for other in self.chains[floor_number].pop(other.chain_id):
                                                    other.chain_id = chain_id
                                                    self.chains[floor_number][chain_id].append(other)

                                    break
                                else:
                                    direction = DIRECTIONS[self.rand.randint(4)]
                            else:
                                direction = DIRECTIONS[self.rand.randint(4)]

        self.built = True

    def draw(self, floor_number: int = 0) -> Canvas:
        """
        Build and draw the different layers of the map.

        :param floor_number: the number of the floor that will be drawn
        :return the map as a set of tkinter canvases
        """
        if not self.built:
            self.build()

        if floor_number in self.floors:
            return self.floors[floor_number].draw(self.canvas, self.canvas_size)

        return self.canvas

    class Floor:
        def __init__(self, dungeon: Dungeon, floor_number: int):
            self.dungeon = dungeon
            self.number = floor_number
            self.rows = range(self.dungeon.grid_size.rows)
            self.cols = range(self.dungeon.grid_size.columns)
            self.grid = [[Dungeon.WallTile(self.dungeon, self, row, col) for col in self.cols] for row in self.rows]
            self.padding_left = self.dungeon.padding_size.left
            self.padding_top = self.dungeon.padding_size.top
            self.cell_size = self.dungeon.cell_size
            self.dungeon.floors[self.number] = self

        def draw(self, canvas: Canvas, size: Dungeon.CanvasSize) -> Canvas:
            wall_color = Dungeon.WallTile.default_color
            canvas.config(width=size.width, height=size.height)
            canvas.create_rectangle(0, 0, size.width, size.height, fill=wall_color)

            for row in self.grid:
                for tile in row:
                    if tile.name != 'wall':
                        color = tile.color
                        x1 = self.padding_left + self.cell_size * tile.column
                        y1 = self.padding_top + self.cell_size * tile.row
                        x2 = x1 + self.cell_size
                        y2 = y1 + self.cell_size
                        tile.draw(canvas, x1, y1, x2, y2)

            return canvas

    class Link:
        def __init__(self, tile: Dungeon.Tile, chain: [], direction):
            self.dungeon = tile.dungeon
            self.floor = tile.floor
            self.name = tile.name
            self.row = tile.row
            self.column = tile.column
            self.tile: Dungeon.Tile = tile
            self.chain_id = chain
            self.direction = direction

        def __str__(self):
            return self.name + ' link(' + str(self.floor.number) + ', ' + str(self.column) + ', ' \
                   + str(self.row) + ')'

    class Tile:
        default_color = None

        def __init__(self, dungeon: Dungeon, floor: Dungeon.Floor, name: str, row: int, column: int, color,
                     interaction=None, state=None):
            self.dungeon = dungeon
            self.floor = floor
            self.name = name
            self.row = row
            self.column = column
            self.color = color
            self.interact = interaction
            self.state = state

        def draw(self, canvas, x1, y1, x2, y2):
            pass

        def __str__(self):
            return self.name + ' tile(' + str(self.floor.number) + ', ' + str(self.column) + ', ' + str(self.row) + ')'

    class WallTile(Tile):
        default_color = "#656565"

        def __init__(self, dungeon: Dungeon, floor: Dungeon.Floor, row: int, column: int):
            super().__init__(dungeon, floor, 'wall', row, column, self.default_color)

        def draw(self, canvas, x1, y1, x2, y2):
            pass

    class FloorTile(Tile):
        default_color = "white"

        def __init__(self, dungeon: Dungeon, floor: Dungeon.Floor, row: int, column: int):
            super().__init__(dungeon, floor, 'floor', row, column, self.default_color)

        def draw(self, canvas, x1, y1, x2, y2):
            canvas.create_rectangle(x1, y1, x2, y2, fill=self.color)

    class CrackedWallTile(Tile):
        default_color = "#757575"

        def __init__(self, dungeon: Dungeon, floor: Dungeon.Floor, row: int, column: int, state="unbroken"):
            super().__init__(dungeon, floor, 'cracked wall', row, column, self.default_color, self.break_wall, state)

        def draw(self, canvas, x1, y1, x2, y2):
            canvas.create_rectangle(x1, y1, x2, y2, fill=self.color)

        def break_wall(self):
            if self.state == 'unbroken':
                self.state = 'broken'
                self.default_color = Dungeon.FloorTile.default_color

    class CrackedFloorTile(Tile):
        default_color = "#EEEEEE"

        def __init__(self, dungeon: Dungeon, floor: Dungeon.Floor, row: int, column: int, state="unbroken"):
            super().__init__(dungeon, floor, 'cracked wall', row, column, self.default_color, self.break_floor, state)

        def draw(self, canvas, x1, y1, x2, y2):
            canvas.create_rectangle(x1, y1, x2, y2, fill=self.color)

        def break_floor(self):
            if self.state == 'unbroken':
                self.state = 'broken'
                self.default_color = Dungeon.PitTile.default_color

    class PitTile(Tile):
        default_color = "black"

        def __init__(self, dungeon: Dungeon, floor: Dungeon.Floor, row: int, column: int):
            super().__init__(dungeon, floor, 'pit', row, column, self.default_color, self.fall_in)

        def draw(self, canvas, x1, y1, x2, y2):
            canvas.create_rectangle(x1, y1, x2, y2, fill=self.color)

        def fall_in(self):
            pass

    class EntryTile(Tile):
        arrow_color = "#4c9e62"

        def __init__(self, dungeon: Dungeon, floor: Dungeon.Floor, row: int, column: int, direction):
            super().__init__(dungeon, floor, 'entry', row, column, self.default_color, self.enter)
            self.direction = direction

        def draw(self, canvas: Canvas, x1, y1, x2, y2):
            canvas.create_rectangle(x1, y1, x2, y2, fill=Dungeon.FloorTile.default_color)

            x1 += 1
            y1 += 1
            x2 -= 1
            y2 -= 1
            x3 = (x1 + x2) / 2
            y3 = (y1 + y2) / 2

            if self.direction == [0, -1]:  # up
                canvas.create_polygon(x1, y2, x2, y2, x3, y3, fill=self.arrow_color, width=0)
            if self.direction == [0, 1]:  # down
                canvas.create_polygon(x1, y1, x2, y1, x3, y3, fill=self.arrow_color, width=0)
            if self.direction == [-1, 0]:  # left
                canvas.create_polygon(x2, y1, x2, y2, x3, y3, fill=self.arrow_color, width=0)
            if self.direction == [1, 0]:  # right
                canvas.create_polygon(x1, y1, x1, y2, x3, y3, fill=self.arrow_color, width=0)

        def enter(self):
            pass

    class StaircaseUpTile(Tile):
        def __init__(self, dungeon: Dungeon, floor: Dungeon.Floor, row: int, column: int):
            super().__init__(dungeon, floor, 'staircase up', row, column, self.default_color, self.go_up)

        def draw(self, canvas: Canvas, x1, y1, x2, y2):
            canvas.create_rectangle(x1, y1, x2, y2, fill=Dungeon.FloorTile.default_color)

            x3 = (x1 + x2) / 2
            y3 = (y1 + y2) / 2
            fs = round((x2 - x1) / 2)

            canvas.create_text(x3, y3, text='ä', font=('Wingdings', fs))

        def go_up(self):
            pass

    class StaircaseDownTile(Tile):
        def __init__(self, dungeon: Dungeon, floor: Dungeon.Floor, row: int, column: int):
            super().__init__(dungeon, floor, 'staircase down', row, column, self.default_color, self.go_down)

        def draw(self, canvas: Canvas, x1, y1, x2, y2):
            canvas.create_rectangle(x1, y1, x2, y2, fill=Dungeon.FloorTile.default_color)

            x3 = (x1 + x2) / 2
            y3 = (y1 + y2) / 2
            fs = round((x2 - x1) / 2)

            canvas.create_text(x3, y3, text='æ', font=('Wingdings', fs))

        def go_down(self):
            pass

    class TreasureTile(Tile):
        icon_color = "goldenrod"

        def __init__(self, dungeon: Dungeon, floor: Dungeon.Floor, row: int, column: int, state='closed'):
            super().__init__(dungeon, floor, 'treasure', row, column, self.default_color, self.open, state)

        def draw(self, canvas: Canvas, x1, y1, x2, y2):
            canvas.create_rectangle(x1, y1, x2, y2, fill=Dungeon.FloorTile.default_color)

            x3 = (x1 + x2) / 2
            y3 = (y1 + y2) / 2
            fs = round((x2 - x1) / 2)

            canvas.create_text(x3, y3, text='▄', font=('Arial', fs), fill=self.icon_color)

        def open(self):
            if self.state == 'closed':
                self.state = 'opened'
                self.default_color = Dungeon.FloorTile.default_color


# window = Tk()
# window.title('Dungeon Maker')
# dungeon: Dungeon = Dungeon(window, cell_size=50, grid_columns=40, grid_rows=20)
# dungeon.draw(0).grid(row=0, column=0)
# window.mainloop()

