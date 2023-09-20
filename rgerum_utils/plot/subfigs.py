import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
from matplotlib.axes import Axes
import pandas as pd
from .subplots import SubPlots

do_enumerate = enumerate


class SubFigs:
    axes = None
    row_count = 0
    col_count = 0
    first_ax = None

    current_row = 0
    current_col = 0

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
        if row >= self.row_count or col >= self.col_count:
            self.change_shape(
                rows=max(row + 1, self.row_count), cols=max(col + 1, self.col_count)
            )
        ax = self.axes[row, col]
        self.current_row = row
        self.current_col = col
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
                    ax.fig._subplotspec = gs[r, c]
                    ax.fig._redo_transform_rel_fig()
                except IndexError:
                    ax = self.fig.add_subfigure(gs[r, c])
                    ax = SubPlots(fig=ax, **self.params)

                new_axes[r, c] = ax
        self.axes = new_axes
