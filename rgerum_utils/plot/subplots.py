import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
from matplotlib.axes import Axes
import pandas as pd

do_enumerate = enumerate


class SubPlots:
    axes = None
    row_count = 0
    col_count = 0
    first_ax = None

    current_row = 0
    current_col = 0
    current_color = None

    col_labels = []
    row_labels = []

    def __init__(
        self,
        fig=None,
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
        self.params = dict(
            sharex=sharex, sharey=sharey, despine=despine, xlabel=xlabel, ylabel=ylabel
        )
        self.col_labels = []
        self.row_labels = []

        # Start with one subplot
        self.axes = np.zeros([0, 0], dtype=object)

    def select_row(self, row, label=None):
        if label is not None:
            while len(self.row_labels) <= row:
                self.row_labels.append("")
            self.row_labels[row] = label
        return self.select_ax(row=row)

    def select_col(self, col, label=None):
        if label is not None:
            while len(self.col_labels) <= col:
                self.col_labels.append("")
            self.col_labels[col] = label
        return self.select_ax(col=col)

    def select_ax(self, row=None, col=None, color=None):
        if row is None:
            row = self.current_row
        if col is None:
            col = self.current_col
        if color is not None:
            self.current_color = color
        if row >= self.row_count or col >= self.col_count:
            self.change_shape(
                rows=max(row + 1, self.row_count), cols=max(col + 1, self.col_count)
            )
        ax = self.axes[row, col]
        self.current_row = row
        self.current_col = col
        plt.sca(ax)
        if self.current_color is not None:
            ax.set_prop_cycle("color", self.color_list[self.current_color :])
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
        )

        for r in range(self.row_count):
            for c in range(self.col_count):
                try:
                    ax = self.axes[r, c]
                    ax.set_position(gs[r, c].get_position(self.fig))
                    ax.set_subplotspec(gs[r, c])
                except IndexError:
                    refs = [None, None]
                    for i, name in enumerate(["sharex", "sharey"]):
                        value = self.params[name]
                        # the reference is the top left for "all"
                        if (value is True or value == "all") and not (
                            r == 0 and c == 0
                        ):
                            refs[i] = new_axes[0, 0]
                        # the reference is the first row for "col"
                        elif value == "col" and r > 0:
                            refs[i] = new_axes[0, c]
                        # the reference is the first col for "row"
                        elif value == "row" and c > 0:
                            refs[i] = new_axes[r, 0]
                    ax = self.fig.add_subplot(gs[r, c], sharex=refs[0], sharey=refs[1])
                    if self.first_ax is None:
                        self.first_ax = ax

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
                        if (
                            self.params["sharex"] is True
                            or self.params["sharex"] == "col"
                        ):
                            plt.xticks(color="none")
                        plt.xlabel("")
                    else:
                        if self.params["xlabel"]:
                            plt.xlabel(self.params["xlabel"])
                    if c != 0:
                        if (
                            self.params["sharey"] is True
                            or self.params["sharey"] == "row"
                        ):
                            plt.yticks(color="none")
                        plt.ylabel("")
                    else:
                        if self.params["ylabel"]:
                            plt.ylabel(row_label + self.params["ylabel"])
                        elif row_label:
                            plt.ylabel(row_label[:-1])
                    if self.params["despine"]:
                        ax.spines[["right", "top"]].set_visible(False)
