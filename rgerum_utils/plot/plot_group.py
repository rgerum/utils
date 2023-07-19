import numpy as np
import matplotlib.pyplot as plt


group = None
do_enumerate = enumerate
class PlotGroup:
    current_col = 0
    current_row = 0
    current_color = 0
    current_fig = 0

    row_count = 1
    col_count = 1
    fig_count = 0
    row_labels = []
    col_labels = []
    colors = None

    axes = None

    def __init__(self, dataframe=None, despine=False, sharex=True, sharey=True, xlabel=None, ylabel=None):
        self.dataframe = dataframe
        self.dataframe0 = dataframe
        self.despine = despine
        self.sharex = sharex
        self.sharey = sharey
        self.xlabel = xlabel
        self.ylabel = ylabel

        self.axes = {}

    def __enter__(self):
        global group
        group = self
        pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for fig in range(max(self.fig_count, 1)):
            if self.fig_count:
                self.select_axes(fig=fig)
            for i, label in enumerate(self.row_labels):
                self.select_axes(col=0, row=i)

                text = ""
                for line in label.split("\n"):
                    text += "$\\bf{" + line.replace(" ", "~") + "}$\n"
                if self.ylabel is not None:
                    plt.ylabel(text+self.ylabel)
                else:
                    plt.ylabel(text)
            for i, label in enumerate(self.col_labels):
                self.select_axes(col=i, row=0)
                plt.title(label, weight="bold")
                if self.xlabel:
                    self.select_axes(col=i, row=self.col_count)
                    plt.xlabel(self.xlabel)

    def select_axes(self, col=None, row=None, color=None, fig=None):
        if fig != None:
            self.current_fig = fig
        if col != None:
            self.current_col = col
        if row != None:
            self.current_row = row
        if color != None:
            self.current_color = color
        if self.current_fig not in self.axes:
            self.update_axes(update=True)
        if self.fig_count:
            plt.figure(self.current_fig)
        plt.sca(self.axes[self.current_fig][self.current_row, self.current_col])
        if self.despine:
            plt.gca().spines[["right", "top"]].set_visible(False)
        if self.colors is not None:
            plt.gca().set_prop_cycle('color', self.colors[self.current_color:])

    def update_axes(self, rows=None, cols=None, fig=None, update = False):
        if fig is not None:
            self.fig_count = fig
        if rows is not None and rows != self.row_count:
            self.row_count = rows
            update = True
        if cols is not None and cols != self.col_count:
            self.col_count = cols
            update = True
        if update:
            if self.fig_count:
                plt.figure(self.current_fig)
            plt.clf()
            self.axes[self.current_fig] = plt.gcf().subplots(self.row_count, self.col_count, squeeze=False, sharex=self.sharex,
                                           sharey=self.sharey)

    def fig(self, iterable=None, groupby=None, label=None, enumerate=False):
        global group
        stored_dataframe = None
        if groupby is not None:
            if iterable is None:
                if label is None:
                    label = groupby+"\n{x}"
                iterable = self.dataframe.groupby(groupby)
                iterable = [(k, self.dataframe[self.dataframe[groupby] == k]) for k in
                            sorted(self.dataframe0[groupby].unique())]
                stored_dataframe = self.dataframe

        length = len(iterable)
        self.update_axes(fig=length)

        for i, v in do_enumerate(iterable):
            self.select_axes(fig=i)

            if stored_dataframe is not None:
                self.dataframe = v[1]

            if enumerate is True:
                yield i, v
            else:
                yield v

            if label is not None:
                if isinstance(v, tuple) and len(v) == 2 and isinstance(v[1], pd.DataFrame):
                    plt.suptitle(label.format(x=v[0]))
                else:
                    plt.suptitle(label.format(x=v))

        self.select_axes(fig=0)

        if stored_dataframe is not None:
            self.dataframe = stored_dataframe

    def row(self, iterable=None, groupby=None, label=None, enumerate=False):
        global group
        stored_dataframe = None
        if groupby is not None:
            if iterable is None:
                if label is None:
                    label = groupby+"\n{x}"
                iterable = self.dataframe.groupby(groupby)
                iterable = [(k, self.dataframe[self.dataframe[groupby] == k]) for k in
                            sorted(self.dataframe0[groupby].unique())]
                stored_dataframe = self.dataframe

        length = len(iterable)
        self.update_axes(rows=length)

        self.row_labels = []
        for i, v in do_enumerate(iterable):
            self.select_axes(row=i)

            if stored_dataframe is not None:
                self.dataframe = v[1]

            if label is not None:
                if isinstance(v, tuple) and len(v) == 2 and isinstance(v[1], pd.DataFrame):
                    self.row_labels.append(label.format(x=v[0]))
                else:
                    self.row_labels.append(label.format(x=v))
            if enumerate is True:
                yield i, v
            else:
                yield v

        self.select_axes(row=0)

        if stored_dataframe is not None:
            self.dataframe = stored_dataframe

    def col(self, iterable=None, groupby=None, label=None, enumerate=False):
        stored_dataframe = None
        if groupby is not None:
            if iterable is None:
                if label is None:
                    label = groupby+"\n{x}"
                iterable = self.dataframe.groupby(groupby)
                #if len(iterable) != len(self.dataframe0.groupby(groupby)):
                iterable = [(k, self.dataframe[self.dataframe[groupby] == k]) for k in sorted(self.dataframe0[groupby].unique())]
                stored_dataframe = self.dataframe

        length = len(iterable)
        self.update_axes(cols=length)

        self.col_labels = []
        for i, v in do_enumerate(iterable):
            self.select_axes(col=i)

            if stored_dataframe is not None:
                self.dataframe = v[1]

            if label:
                if isinstance(v, tuple) and len(v) == 2 and isinstance(v[1], pd.DataFrame):
                    self.col_labels.append(label.format(x=v[0]))
                else:
                    self.col_labels.append(label.format(x=v))
            if enumerate is True:
                yield i, v
            else:
                yield v

        self.select_axes(col=0)

        if stored_dataframe is not None:
            self.dataframe = stored_dataframe

    def color(self, iterable=None, groupby=None, cmap="viridis", color1="b", color2="r", label=None, enumerate=False):
        stored_dataframe = None
        if groupby is not None:
            if iterable is None:
                iterable = self.dataframe.groupby(groupby)
                iterable = [(k, self.dataframe[self.dataframe[groupby] == k]) for k in
                            sorted(self.dataframe0[groupby].unique())]
                stored_dataframe = self.dataframe

        length = len(iterable)
        #from lab_colormap import LabColormap
        #cmap = LabColormap((color1, color2), length)
        cmap = plt.get_cmap(cmap)
        self.colors = [cmap(i/(length-1)) for i in range(length)]

        for i, v in do_enumerate(iterable):
            self.select_axes(color=i)
            if stored_dataframe is not None:
                self.dataframe = v[1]

            if enumerate is True:
                yield i, v
            else:
                yield v

        if stored_dataframe is not None:
            self.dataframe = stored_dataframe

if __name__ == "__main__":
    if 1:
     i = 1
     j = 1
     jj = 1
     with PlotGroup(despine=True) as group:
      for a, va in group.fig(["x", "yy"], label="dataset={x}", enumerate=True):
        for i, vi in group.row([1, 10, 20, 30], label="x\n{x}", enumerate=True):
            for j, vj in group.col([2, 12, 22], label="y\n{x}", enumerate=True):
                #for jj, vjj in group.color(range(20), label="y\n{x}", enumerate=True):
                    #print("plot", plt.gca())
                    plt.plot([0, i], [0, j*jj])
     plt.show()
     exit()
     plt.figure(20)

    import pandas as pd
    df = pd.DataFrame([
        #dict(x=10, y=10, z=1),
        dict(x=10, y=20, z=2),
        dict(x=10, y=30, z=3),
        dict(x=20, y=10, z=10),
        dict(x=20, y=10, z=20),
        #dict(x=20, y=20, z=20),
        dict(x=20, y=30, z=30),
    ])
    #if 0:
    #with Grouping(despine=True) as group:
    with PlotGroup(dataframe=df, despine=True, xlabel="ab", ylabel="yy") as group:
    #    for i, imax, (ival, d) in group.row(df.groupby("x"), label="x\n{x}"):
        for ival, d in group.fig(groupby="x"):
            for jval, d in group.row(groupby="y"):

                for vjj, d in group.color(groupby="z", label="y\n{x}"):
            #for j, jmax, (jval, d) in group.col(d.groupby("y"), label="y\n{x}"):

            #    for jj, jjmax, vjj in group.color([2, 12, 22], label="y\n{x}"):
                    #print("plot", i, j, jj)
                    if len(d):
                        print([0, ival+1], [0, d.iloc[0].z * 1])
                        plt.plot([0, ival+1], [0, d.iloc[0].z * 1], label=f"{jj}")
                    else:
                        plt.plot([], [], label=f"{jj}")

    plt.legend()

    plt.show()
