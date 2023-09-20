import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
from matplotlib.axes import Axes
import pandas as pd

do_enumerate = enumerate
from .subplots import SubPlots
from .subfigs import SubFigs


class PlotGroup:
    axes = None
    row_count = 0
    col_count = 0
    first_ax = None

    def __init__(
        self,
        dataframe=None,
        fig=None,
        hierarchy=0,
        sharex=None,
        sharey=None,
        despine=True,
        xlabel=None,
        ylabel=None,
    ) -> None:
        if fig is not None:
            self.fig = fig
        else:
            self.fig = plt.figure()
        self.dataframe0 = dataframe
        self.dataframe = dataframe
        self.params = dict(
            sharex=sharex, sharey=sharey, despine=despine, xlabel=xlabel, ylabel=ylabel
        )

        self.current_row = [0, 0]
        self.current_col = [0, 0]

        self.subplots = SubFigs(self.fig, **self.params)
        self.current_iterators = []

    def select_row(self, row: int, label: str = None):
        return self.select(1).select_row(row, label)

    def select_col(self, col: int, label: str = None):
        return self.select(1).select_col(col, label)

    def wrap_iterator(self, iterable=None, groupby=None, label=None, enumerate=False):
        global group
        stored_dataframe = None
        if groupby is not None:
            if iterable is None:
                if label is None:
                    label = groupby + "\n{x}"
                iterable = self.dataframe.groupby(groupby)
                iterable = [
                    (k, self.dataframe[self.dataframe[groupby] == k])
                    for k in sorted(self.dataframe0[groupby].unique())
                ]
                stored_dataframe = self.dataframe

        for v in iterable:
            if stored_dataframe is not None:
                self.dataframe = v[1]

            current_label = None
            if label is not None:
                if (
                    isinstance(v, tuple)
                    and len(v) == 2
                    and isinstance(v[1], pd.DataFrame)
                ):
                    current_label = label.format(x=v[0])
                else:
                    current_label = label.format(x=v)

            yield current_label, v

        if stored_dataframe is not None:
            self.dataframe = stored_dataframe

    def iter(
        self,
        iterable=None,
        groupby=None,
        label=None,
        enumerate=False,
        cmap=None,
        type=None,
    ):
        if type == "rows":
            yield from self.rows(iterable, label)
        elif type == "cols":
            yield from self.cols(iterable, label)
        elif type == "colors":
            yield from self.colors(iterable, cmap=cmap)
        else:
            for i, v in do_enumerate(iterable):
                if enumerate is True:
                    yield i, v
                else:
                    yield v

    def rows(self, iterator, label=None):
        for i, value in enumerate(iterator):
            self.add_iterator("row")
            self.select(1).select_row(
                i, label=label.format(x=value) if label is not None else None
            )
            yield value
        self.remove_iterator("row")

    def cols(self, iterator, label=None):
        for i, value in enumerate(iterator):
            self.add_iterator("col")
            self.select(1).select_col(
                i, label=label.format(x=value) if label is not None else None
            )
            yield value
        self.remove_iterator("col")

    def colors(self, iterator, label=None, cmap="turbo"):
        length = len(iterator)
        cmap = plt.get_cmap(cmap)
        self.select(1).color_list = [cmap(i / (length - 1)) for i in range(length)]

        for i, value in enumerate(iterator):
            self.add_iterator("color")
            self.select(1).select_ax(color=i)
            yield value
        self.remove_iterator("color")

    current_iterators = []

    def remove_iterator(self, name):
        while name in self.current_iterators:
            iterator = self.current_iterators.pop()
            if iterator == "col":
                self.current_col[-1] = 0
                self.select(1).select_col(0)
            if iterator == "row":
                self.current_row[-1] = 0
                self.select(1).select_row(0)
            if iterator == "figcol":
                self.current_col[-2] = 0
                self.select(0).select_col(0)
            if iterator == "figrow":
                self.current_row[-2] = 0
                self.select(0).select_row(0)

    def add_iterator(self, name):
        if name in self.current_iterators and self.current_iterators[-1] != name:
            while self.current_iterators[-1] != name:
                self.remove_iterator(self.current_iterators[-1])

        if not len(self.current_iterators) or self.current_iterators[-1] != name:
            self.current_iterators.append(name)

    def add_figrow(self, **params):
        self.add_iterator("figrow")
        ax = self.select(0).select_row(self.current_row[-2])
        ax.params.update(params)
        self.current_row[-2] += 1
        return ax

    def add_figcol(self, **params):
        self.add_iterator("figcol")
        ax = self.select(0).select_col(self.current_col[-2])
        ax.params.update(params)
        self.current_col[-2] += 1
        return ax

    def add_row(self, label=None):
        self.add_iterator("row")
        ax = self.select(1).select_row(self.current_row[-1], label)
        self.current_row[-1] += 1
        return ax

    def add_col(self, label=None):
        self.add_iterator("col")
        ax = self.select(1).select_col(self.current_col[-1], label)
        self.current_col[-1] += 1
        return ax

    def add(self, type=None, label=None):
        if type == "row":
            return self.add_row(label)
        if type == "col":
            return self.add_col(label)
        if type == "figcol":
            return self.add_figcol(label)
        if type == "figrow":
            return self.add_figrow(label)

    selected = []

    def select(self, hierarchy):
        if hierarchy == 0:
            return self.subplots
        if hierarchy == 1:
            return self.subplots.select_ax()


class PlotGroupOld:
    axes = None
    row_count = 0
    col_count = 0
    first_ax = None

    current_row = 0
    current_col = 0

    def __init__(
        self,
        dataframe=None,
        fig=None,
        hierarchy=0,
        sharex=None,
        sharey=None,
        despine=True,
        xlabel=None,
        ylabel=None,
    ) -> None:
        if fig is not None:
            self.fig = fig
        else:
            self.fig = plt.figure()
        self.dataframe0 = dataframe
        self.dataframe = dataframe
        self.params = dict(
            sharex=sharex, sharey=sharey, despine=despine, xlabel=xlabel, ylabel=ylabel
        )

        self.cur_row = [0]
        self.cur_col = [0]

        # Start with one subplot
        self.axes = np.zeros([0, 0], dtype=object)
        self.hierarchy = hierarchy

    def select_ax(self, row=None, col=None, color=None):
        if row is None:
            row = self.current_row
        if col is None:
            col = self.current_col
        if isinstance(row, (tuple, list)):
            obj = self
            for r, c in zip(row, col):
                if len(self.row_labels):
                    obj.row_labels = self.row_labels
                if len(self.col_labels):
                    obj.col_labels = self.col_labels
                if r is None or c is None:
                    if obj.hierarchy == 0:
                        obj.select_ax(0, 0, color=color)
                    return obj
                obj = obj.select_ax(r, c, color=color)
            return obj
        if row >= self.row_count or col >= self.col_count:
            self.change_shape(
                rows=max(row + 1, self.row_count), cols=max(col + 1, self.col_count)
            )
        ax = self.axes[row, col]
        self.current_row = row
        self.current_col = col
        if isinstance(ax, Axes):
            plt.sca(ax)
            if color is not None:
                ax.set_prop_cycle("color", self.color_list[color:])
        return ax

    def change_shape(self, rows=None, cols=None) -> None:
        """Plots the data to a new subplot at the bottom."""
        if rows is not None:
            self.row_count = rows
        if cols is not None:
            self.col_count = cols

        new_axes = np.zeros([self.row_count, self.col_count], dtype=object)
        gs = gridspec.GridSpec(
            self.row_count,
            self.col_count,
            height_ratios=self.height_ratios
            if len(self.height_ratios) == self.row_count
            else None,
            width_ratios=self.width_ratios
            if len(self.width_ratios) == self.col_count
            else None,
        )

        for r in range(self.row_count):
            for c in range(self.col_count):
                try:
                    ax = self.axes[r, c]
                    if isinstance(ax, Axes):
                        ax.set_position(gs[r, c].get_position(self.fig))
                        ax.set_subplotspec(gs[r, c])
                    else:
                        ax.fig._subplotspec = gs[r, c]
                        ax.fig._redo_transform_rel_fig()
                except IndexError:
                    if self.hierarchy == 0:
                        ref_ax_x = self.first_ax if self.params["sharex"] else None
                        ref_ax_y = self.first_ax if self.params["sharey"] else None
                        if self.params["sharex"] == "col" and r != 0:
                            ref_ax_x = new_axes[0, c]
                        if self.params["sharey"] == "row" and c != 0:
                            ref_ax_y = new_axes[r, 0]
                        print("ref_ax_x", ref_ax_x, ref_ax_y)
                        ax = self.fig.add_subplot(
                            gs[r, c], sharex=ref_ax_x, sharey=ref_ax_y
                        )
                        if self.first_ax is None:
                            self.first_ax = ax
                    else:
                        ax = self.fig.add_subfigure(gs[r, c])
                        ax = PlotGroup(
                            fig=ax, hierarchy=self.hierarchy - 1, **self.params
                        )

                new_axes[r, c] = ax
        self.axes = new_axes
        self.update_ax_labels()

    def update_ax_labels(self):
        for r in range(self.row_count):
            for c in range(self.col_count):
                ax = self.axes[r, c]
                if isinstance(ax, Axes):
                    plt.sca(ax)
                    if r == 0 and c < len(self.col_labels):
                        plt.title(self.col_labels[c])
                    row_label = ""
                    if c == 0 and r < len(self.row_labels) and self.row_labels[r]:
                        row_label = self.row_labels[r] + "\n"

                    if r != self.row_count - 1:
                        if self.params["sharex"]:
                            plt.xticks(color="none")
                            plt.xlabel("")
                    else:
                        if self.params["xlabel"]:
                            plt.xlabel(self.params["xlabel"])
                    if c != 0:
                        if self.params["sharey"]:
                            plt.yticks(color="none")
                            plt.ylabel("")
                    else:
                        if self.params["ylabel"]:
                            plt.ylabel(row_label + self.params["ylabel"])
                        elif row_label:
                            plt.ylabel(row_label[:-1])
                    if self.params["despine"]:
                        ax.spines[["right", "top"]].set_visible(False)

    cur_row = 0
    cur_col = 0

    def wrap_iterator(self, iterable=None, groupby=None, label=None, enumerate=False):
        global group
        stored_dataframe = None
        if groupby is not None:
            if iterable is None:
                if label is None:
                    label = groupby + "\n{x}"
                iterable = self.dataframe.groupby(groupby)
                iterable = [
                    (k, self.dataframe[self.dataframe[groupby] == k])
                    for k in sorted(self.dataframe0[groupby].unique())
                ]
                stored_dataframe = self.dataframe

        for v in iterable:
            if stored_dataframe is not None:
                self.dataframe = v[1]

            current_label = None
            if label is not None:
                if (
                    isinstance(v, tuple)
                    and len(v) == 2
                    and isinstance(v[1], pd.DataFrame)
                ):
                    current_label = label.format(x=v[0])
                else:
                    current_label = label.format(x=v)

            yield current_label, v

        if stored_dataframe is not None:
            self.dataframe = stored_dataframe

    def fig_row(
        self, iterable=None, groupby=None, label=None, enumerate=False, hierarchy=1
    ):
        while len(self.cur_row) < (hierarchy + 1):
            self.cur_row = [0] + self.cur_row
            self.cur_col = [0] + self.cur_col
            self.hierarchy = hierarchy
        for i, (label, v) in do_enumerate(
            self.wrap_iterator(iterable, groupby, label, enumerate)
        ):
            self.cur_row[-1 - hierarchy] = i
            self.select_ax(row=self.cur_row, col=self.cur_col)

            if enumerate is True:
                yield i, v
            else:
                yield v
        self.cur_row[-1 - hierarchy] = 0

    def iter(
        self,
        iterable=None,
        groupby=None,
        label=None,
        enumerate=False,
        cmap=None,
        type=None,
    ):
        if type == "rows":
            yield from self.rows(iterable, groupby, label, enumerate)
        elif type == "cols":
            yield from self.cols(iterable, groupby, label, enumerate)
        elif type == "colors":
            yield from self.colors(
                iterable=iterable, groupby=groupby, enumerate=enumerate, cmap=cmap
            )
        else:
            for i, v in do_enumerate(iterable):
                if enumerate is True:
                    yield i, v
                else:
                    yield v

    row_labels = []

    def rows(self, iterable=None, groupby=None, label=None, enumerate=False):
        self.row_labels = []
        for i, (label, v) in do_enumerate(
            self.wrap_iterator(iterable, groupby, label, enumerate)
        ):
            self.cur_row[-1] = i
            self.select_ax(row=self.cur_row)

            self.row_labels.append(label)
            if enumerate is True:
                yield i, v
            else:
                yield v
        self.update_ax_labels()
        self.cur_row[-1] = 0

    def fig_col(
        self, iterable=None, groupby=None, label=None, enumerate=False, hierarchy=1
    ):
        while len(self.cur_row) < (hierarchy + 1):
            self.cur_row = [0] + self.cur_row
            self.cur_col = [0] + self.cur_col
            self.hierarchy = hierarchy

        for i, (label, v) in do_enumerate(
            self.wrap_iterator(iterable, groupby, label, enumerate)
        ):
            self.cur_col[-1 - hierarchy] = i
            self.select_ax(row=self.cur_row, col=self.cur_col)

            if enumerate is True:
                yield i, v
            else:
                yield v
        self.select_ax(
            row=[self.cur_row[0], None], col=[self.cur_col[0], None]
        ).update_ax_labels()

        self.cur_col[-1 - hierarchy] = 0

    col_labels = []

    def cols(self, iterable=None, groupby=None, label=None, enumerate=False):
        self.col_labels = []
        for i, (label, v) in do_enumerate(
            self.wrap_iterator(iterable, groupby, label, enumerate)
        ):
            self.cur_col[-1] = i
            self.select_ax(row=self.cur_row, col=self.cur_col)

            self.col_labels.append(label)
            if enumerate is True:
                yield i, v
            else:
                yield v
        self.update_ax_labels()
        self.cur_col[-1] = 0

    def colors(self, iterable=None, groupby=None, cmap="viridis", enumerate=False):
        stored_dataframe = None
        if groupby is not None:
            if iterable is None:
                iterable = self.dataframe.groupby(groupby)
                iterable = [
                    (k, self.dataframe[self.dataframe[groupby] == k])
                    for k in sorted(self.dataframe0[groupby].unique())
                ]
                stored_dataframe = self.dataframe

        length = len(iterable)
        # from lab_colormap import LabColormap
        # cmap = LabColormap((color1, color2), length)
        cmap = plt.get_cmap(cmap)
        self.color_list = [cmap(i / (length - 1)) for i in range(length)]

        for i, v in do_enumerate(iterable):
            self.select_ax(row=self.cur_row, col=self.cur_col, color=i)
            if stored_dataframe is not None:
                self.dataframe = v[1]

            if enumerate is True:
                yield i, v
            else:
                yield v

        if stored_dataframe is not None:
            self.dataframe = stored_dataframe

    height_ratios = []

    def add_subfig_row(self, hierarchy=1, weight=1, **kwargs):
        self.height_ratios.append(weight)
        if hierarchy != self.hierarchy:
            while len(self.cur_row) < (hierarchy + 1):
                self.cur_row = [0] + self.cur_row
                self.cur_col = [0] + self.cur_col
                self.hierarchy = hierarchy
        else:
            self.cur_row[-1 + hierarchy] += 1
        group = self.select_ax([self.cur_row[0], None], [self.cur_col[0], None])
        group.params.update(kwargs)
        return group

    width_ratios = []

    def add_subfig_col(self, hierarchy=1, weight=1, **kwargs):
        self.width_ratios.append(weight)
        if hierarchy != self.hierarchy:
            while len(self.cur_col) < (hierarchy + 1):
                self.cur_row = [0] + self.cur_row
                self.cur_col = [0] + self.cur_col
                self.hierarchy = hierarchy
        else:
            self.cur_col[-1 + hierarchy] += 1
        group = self.select_ax([self.cur_row[0], None], [self.cur_col[0], None])
        group.params.update(kwargs)
        return group
