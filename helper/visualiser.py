
import pandas as pd
import numpy as np
import math
# import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

FONT_SIZE = 8

class_colours = {
    "WARRIOR": "peru",
    "PRIEST": "darkgrey",
    "SHAMAN": "mediumblue",
    "PALADIN": "lightpink",
    "DRUID": "orange",
    "WARLOCK": "mediumorchid",
    "MAGE": "deepskyblue",
    "ROGUE": "gold",
    "HUNTER": "lawngreen"
}

# ToDo: LinePlot for each boss
# LinePlot for each player for each spell (text with Spellname + amount of casts)

def LinePlot(ax, df, players, val_col, dmg, draw_section):
    df_sections = df["section"].unique()
    for source in players:
        col = class_colours[players[source]["class"]]
        if dmg:
            idx = (df["source"]==source) & (df["target"]!=source) # damage to self shouldnt add to damage (warlock hellfire,...)
            pet_name = players[source]["pet"]
            if pet_name:
                idx = idx | ((df["source"]==pet_name) & (df["target"]!=pet_name))
        else:
            idx = (df["source"]==source)
        time = np.array(df[idx]["timestamp"])
        val = np.array(np.cumsum(df[idx][val_col]))
        if np.size(time) > 0:
            ax.plot(time, val, color=col)
            ax.text(time[-1], val[-1], source, fontsize=FONT_SIZE, color=col)
    if draw_section:
        for section in df_sections:
            if section != "":
                x_min = df[df["section"]==section]["timestamp"].min(axis=0)
                x_max = df[df["section"]==section]["timestamp"].max(axis=0)
                ax.axvspan(x_min, x_max, alpha=0.2)
                y_min, y_max = ax.get_ylim()
                y_mid =  (y_min+y_max)/2
                x_mid = (x_max+x_min)/2
                ax.text(x_mid, y_mid, section, rotation="vertical", va="center", ha="center", fontsize=FONT_SIZE)

def BarPlot_Damage(ax, df, players, val_col):
    x_bar = []
    y_bar = []
    col = []
    for source in players:
        col.append(class_colours[players[source]["class"]])
        idx = (df["source"]==source) & (df["target"]!=source) # damage to self shouldnt add to damage (warlock hellfire,...)
        pet_name = players[source]["pet"]
        if pet_name:
            idx = idx | ((df["source"]==pet_name) & (df["target"]!=pet_name))
        x_bar.append(source)
        y_bar.append(df[idx][val_col].sum())
    idx_s = list(np.argsort(y_bar))
    x_bar = np.array(x_bar)
    y_bar = np.array(y_bar)
    col = np.array(col)
    cols = col[idx_s]
    ax.barh(x_bar[idx_s], y_bar[idx_s], color=col[idx_s])
    for x_txt, y_txt in enumerate(y_bar[idx_s]):
        ax.text(y_txt, x_txt, "{:.0f}".format(y_txt), fontsize=FONT_SIZE, color=cols[x_txt], va="center")
    ax.tick_params(labelbottom=False)

def BarPlot_Heal(ax, df, players):
    x_bar = []
    y_bar_eheal = []
    y_bar_oheal = []
    y_bar_theal = []
    col = []
    for source in players:
        x_bar.append(source)
        y_bar_eheal.append(df[df["source"]==source]["eheal"].sum())
        y_bar_oheal.append(df[df["source"]==source]["oheal"].sum())
        y_bar_theal.append(df[df["source"]==source]["value"].sum())
        col.append(class_colours[players[source]["class"]])
    idx_s = list(np.argsort(y_bar_eheal))
    x_bar = np.array(x_bar)
    y_bar_eheal = np.array(y_bar_eheal)
    y_bar_oheal = np.array(y_bar_oheal)
    y_bar_theal = np.array(y_bar_theal)
    col = np.array(col)

    xs_bar = x_bar[idx_s]
    ys_bar_eheal = y_bar_eheal[idx_s]
    ys_bar_oheal = y_bar_oheal[idx_s]
    ys_bar_theal = y_bar_theal[idx_s]
    cols = col[idx_s]

    ys_bar_theal_add = ys_bar_theal - (ys_bar_eheal+ys_bar_oheal)
    ax.barh(xs_bar, ys_bar_eheal, linewidth=2, color='g')
    ax.barh(xs_bar, ys_bar_oheal, left=ys_bar_eheal, linewidth=2, color='r')
    ax.barh(xs_bar, ys_bar_theal_add, left=ys_bar_eheal+ys_bar_oheal, linewidth=2, color='b')

    for x_txt, y_txt in enumerate(ys_bar_theal):
        ax.text(y_txt, x_txt, "{:.0f} (+{:.0f}/{:.0f})".format(ys_bar_eheal[x_txt], ys_bar_oheal[x_txt], ys_bar_theal_add[x_txt]),
                fontsize=FONT_SIZE, color=cols[x_txt], va="center")
    ax.tick_params(labelbottom=False)

def BarPlots_Spells(fig, df, players, val_col, dmg):
    players_amount = len(players)
    rows = math.ceil(math.sqrt(players_amount))
    cols = math.ceil(players_amount/rows)
    gs = fig.add_gridspec(rows,cols)

    for idx_player, source in enumerate(players):
        row = math.floor(idx_player/cols)
        col = idx_player%cols
        ax = fig.add_subplot(gs[row, col])
        class_col = class_colours[players[source]["class"]]
        ax.set_title(source, color=class_col)
        if dmg:
            idx = (df["source"]==source) & (df["target"]!=source) # damage to self shouldnt add to damage (warlock hellfire,...)
            pet_name = players[source]["pet"]
            if pet_name:
                idx = idx | ((df["source"]==pet_name) & (df["target"]!=pet_name))
        else:
            idx = (df["source"]==source)
        df_player = df[idx]
        spell_unique = df_player["spell"].unique()
        x_bar = []
        y_bar = []
        for spell in spell_unique:
            idx_spell = (df_player["spell"]==spell)
            x_bar.append(spell)
            y_bar.append(df_player[idx_spell][val_col].sum())
        idx_s = list(np.argsort(y_bar))
        x_bar = np.array(x_bar)
        y_bar = np.array(y_bar)
        top_spells_max = np.minimum(np.size(y_bar), 4)
        idx_s4 = idx_s[-top_spells_max:]
        ax.barh(x_bar[idx_s4], y_bar[idx_s4])
        for x_txt, y_txt in enumerate(y_bar[idx_s4]):
            ax.text(0, x_txt, "{:.0f}".format(y_txt), fontsize=FONT_SIZE, va="center", ha="left")
        ax.tick_params(labelbottom=False)

def GetPlayerHealDamage(df, players):
    df_damage = df[df["subkind"]=="DAMAGE"]
    df_heal = df[df["subkind"]=="HEAL"]
    players_damage = {}
    players_heal = {}
    for source in players:
        idx_damage = df_damage["source"]==source
        idx_heal = df_heal["source"]==source
        val_sum = df_damage[idx_damage]["value"].sum() + df_heal[idx_heal]["value"].sum()
        if (val_sum>0) and (df_damage[idx_damage]["value"].sum()/val_sum*100 > 10): # if damage > x% of total values -> damage dealer (careful: Shadow Priest does healing and damage)
            players_damage[source] = {
                "class": players[source]["class"],
                "pet": players[source]["pet"]
            }
        if (val_sum>0) and (df_heal[idx_heal]["value"].sum()/val_sum*100 > 10): # if heal > x% of total values -> healer
            players_heal[source] = {
                "class": players[source]["class"],
                "pet": players[source]["pet"]
            }
    return (players_damage, players_heal)
    

def Visualise(df, players):
    print("###### Use inbetween to plot boss sections (if boss fight is interrupted)")

    (players_damage, players_heal) = GetPlayerHealDamage(df, players)

    pp = PdfPages('foo.pdf')

    px = 1/plt.rcParams['figure.dpi']  # pixel in inches

    # SECTION: ALL
    fig = plt.figure(figsize=(1920*px,1080*px))
    fig.suptitle("Section: All")
    gs = fig.add_gridspec(2,2)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_title('Damage')
    LinePlot(ax1, df[df["subkind"]=="DAMAGE"], players_damage, "value", True, True)

    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_title('effective healing')
    LinePlot(ax2, df[df["subkind"]=="HEAL"], players_heal, "eheal", False, True)

    ax3 = fig.add_subplot(gs[0, 1])
    ax3.set_title('Damage')
    BarPlot_Damage(ax3, df[df["subkind"]=="DAMAGE"], players_damage, "value")

    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_title('effective healing')
    BarPlot_Heal(ax4, df[df["subkind"]=="HEAL"], players_heal)
    plt.close()
    pp.savefig(fig)

    fig = plt.figure(figsize=(1920*px,1080*px))
    fig.suptitle("Section: All (Damage)")
    BarPlots_Spells(fig, df[df["subkind"]=="DAMAGE"], players_damage, "value", True)
    plt.close()
    pp.savefig(fig)

    fig = plt.figure(figsize=(1920*px,1080*px))
    fig.suptitle("Section: All (Healing)")
    BarPlots_Spells(fig, df[df["subkind"]=="HEAL"], players_heal, "eheal", False)
    plt.close()
    pp.savefig(fig)

    # SECTION: BOSSES
    fig = plt.figure(figsize=(1920*px,1080*px))
    fig.suptitle("Section: Bosses")
    gs = fig.add_gridspec(2,2)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_title('Damage')
    LinePlot(ax1, df[(df["subkind"]=="DAMAGE") & (df["section"]!="")], players_damage, "value", True, True)

    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_title('effective healing')
    LinePlot(ax2, df[(df["subkind"]=="HEAL") & (df["section"]!="")], players_heal, "eheal", False, True)

    ax3 = fig.add_subplot(gs[0, 1])
    ax3.set_title('Damage')
    BarPlot_Damage(ax3, df[(df["subkind"]=="DAMAGE") & (df["section"]!="")], players_damage, "value")

    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_title('effective healing')
    BarPlot_Heal(ax4, df[(df["subkind"]=="HEAL") & (df["section"]!="")], players_heal)
    plt.close()
    pp.savefig(fig)

    fig = plt.figure(figsize=(1920*px,1080*px))
    fig.suptitle("Section: Bosses (Damage)")
    BarPlots_Spells(fig, df[(df["subkind"]=="DAMAGE") & (df["section"]!="")], players_damage, "value", True)
    plt.close()
    pp.savefig(fig)

    fig = plt.figure(figsize=(1920*px,1080*px))
    fig.suptitle("Section: Bosses (Healing)")
    BarPlots_Spells(fig, df[(df["subkind"]=="HEAL") & (df["section"]!="")], players_heal, "eheal", False)
    plt.close()
    pp.savefig(fig)

    # SECTION: BOSS
    sections_unique = df["section"].unique()
    for section in sections_unique:
        if section: # dont show empty section
            fig = plt.figure(figsize=(1920*px,1080*px))
            fig.suptitle("Section: " + section)

            gs = fig.add_gridspec(2,2)
            ax1 = fig.add_subplot(gs[0, 0])
            ax1.set_title('Damage')
            LinePlot(ax1, df[(df["subkind"]=="DAMAGE") & (df["section"]==section)], players_damage, "value", True, False)

            ax2 = fig.add_subplot(gs[1, 0])
            ax2.set_title('effective healing')
            LinePlot(ax2, df[(df["subkind"]=="HEAL") & (df["section"]==section)], players_heal, "eheal", False, False)

            ax3 = fig.add_subplot(gs[0, 1])
            ax3.set_title('Damage')
            BarPlot_Damage(ax3, df[(df["subkind"]=="DAMAGE") & (df["section"]==section)], players_damage, "value")

            ax4 = fig.add_subplot(gs[1, 1])
            ax4.set_title('effective healing')
            BarPlot_Heal(ax4, df[(df["subkind"]=="HEAL") & (df["section"]==section)], players_heal)
            plt.close()
            pp.savefig(fig)

            fig = plt.figure(figsize=(1920*px,1080*px))
            fig.suptitle("Section: " + section +  " (Damage)")
            BarPlots_Spells(fig, df[(df["subkind"]=="DAMAGE") & (df["section"]==section)], players_damage, "value", True)
            plt.close()
            pp.savefig(fig)

            fig = plt.figure(figsize=(1920*px,1080*px))
            fig.suptitle("Section: " + section +  " (Healing)")
            BarPlots_Spells(fig, df[(df["subkind"]=="HEAL") & (df["section"]==section)], players_heal, "eheal", False)
            plt.close()
            pp.savefig(fig)

    pp.close()