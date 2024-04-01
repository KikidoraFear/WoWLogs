
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# ToDo: LinePlot for each boss
# LinePlot for each player for each spell (text with Spellname + amount of casts)

def LinePlot(ax, df, player_names, val_col):
    df_sections = df["section"].unique()
    for source in player_names:
        time = np.array(df[df["source"]==source]["timestamp"])
        val = np.array(np.cumsum(df[df["source"]==source][val_col]))
        if np.size(time) > 0:
            ax.plot(time, val)
            ax.text(1.005*time[-1], val[-1], source, fontsize="small")
    for section in df_sections:
        if section != "":
            x_min = df[df["section"]==section]["timestamp"].min(axis=0)
            x_max = df[df["section"]==section]["timestamp"].max(axis=0)
            ax.axvspan(x_min, x_max, alpha=0.2)
            y_min, y_max = ax.get_ylim()
            y_mid =  (y_min+y_max)/2
            x_mid = (x_max+x_min)/2
            ax.text(x_mid, y_mid, section, rotation="vertical", va="center", ha="center", fontsize="small")

def BarPlot(ax, df, player_names, val_col):
    x_bar = []
    y_bar = []
    for source in player_names:
        x_bar.append(source)
        y_bar.append(df[df["source"]==source][val_col].sum())
    idx_s = list(np.argsort(y_bar))
    x_bar = np.array(x_bar)
    y_bar = np.array(y_bar)
    ax.barh(x_bar[idx_s], y_bar[idx_s])
    for x_txt, y_txt in enumerate(y_bar[idx_s]):
        ax.text(1.005*y_txt, x_txt, "{:.0f}".format(y_txt), fontsize="small")

def BarPlot3(ax, df, player_names):
    x_bar = []
    y_bar_eheal = []
    y_bar_oheal = []
    y_bar_theal = []
    for source in player_names:
        x_bar.append(source)
        y_bar_eheal.append(df[df["source"]==source]["eheal"].sum())
        y_bar_oheal.append(df[df["source"]==source]["oheal"].sum())
        y_bar_theal.append(df[df["source"]==source]["value"].sum())
    idx_s = list(np.argsort(y_bar_eheal))
    x_bar = np.array(x_bar)
    y_bar_eheal = np.array(y_bar_eheal)
    y_bar_oheal = np.array(y_bar_oheal)
    y_bar_theal = np.array(y_bar_theal)

    xs_bar = x_bar[idx_s]
    ys_bar_eheal = y_bar_eheal[idx_s]
    ys_bar_oheal = y_bar_oheal[idx_s]
    ys_bar_theal = y_bar_theal[idx_s]

    ys_bar_theal_add = ys_bar_theal - (ys_bar_eheal+ys_bar_oheal)
    ax.barh(xs_bar, ys_bar_eheal, color='g')
    ax.barh(xs_bar, ys_bar_oheal, left=ys_bar_eheal, color='r')
    ax.barh(xs_bar, ys_bar_theal_add, left=ys_bar_eheal+ys_bar_oheal, color='b')

    for x_txt, y_txt in enumerate(ys_bar_theal):
        ax.text(1.005*y_txt, x_txt, "{:.0f} (+{:.0f}/{:.0f})".format(ys_bar_eheal[x_txt], ys_bar_oheal[x_txt], ys_bar_theal_add[x_txt]), fontsize="small")

def Visualise(df, player_names):
    fig1 = plt.figure()
    gs = fig1.add_gridspec(2,2)
    print("Damaging yourself shouldnt add to your damage")
    ax1 = fig1.add_subplot(gs[0, :])
    ax1.set_title('Damage')
    LinePlot(ax1, df[df["subkind"]=="DAMAGE"], player_names, "value")

    ax2 = fig1.add_subplot(gs[1, 0])
    ax2.set_title('effective healing')
    LinePlot(ax2, df[df["subkind"]=="HEAL"], player_names, "eheal")

    ax3 = fig1.add_subplot(gs[1, 1])
    ax3.set_title('overhealing')
    LinePlot(ax3, df[df["subkind"]=="HEAL"], player_names, "oheal")

    fig2 = plt.figure()
    gs = fig2.add_gridspec(1,2)
    BarPlot(fig2.add_subplot(gs[0, 0]), df[df["subkind"]=="DAMAGE"], player_names, "value")
    BarPlot3(fig2.add_subplot(gs[0, 1]), df[df["subkind"]=="HEAL"], player_names)

    pp = PdfPages('foo.pdf')
    pp.savefig(fig1)
    pp.savefig(fig2)
    pp.close()