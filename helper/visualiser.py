
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

def GetPlayersSep(df, players): # separate players by damage/heal
    df_damage = df[df["subkind"]=="DAMAGE"]
    df_heal = df[df["subkind"]=="HEAL"]
    players_sep = {
        "DAMAGE": {},
        "HEAL": {}
    }
    for source in players:
        idx_damage = df_damage["source"]==source
        idx_heal = df_heal["source"]==source
        val_sum = df_damage[idx_damage]["value"].sum() + df_heal[idx_heal]["value"].sum()
        if (val_sum>0) and (df_damage[idx_damage]["value"].sum()/val_sum*100 > 10): # if damage > x% of total values -> damage dealer (careful: Shadow Priest does healing and damage)
            players_sep["DAMAGE"][source] = {
                "class": players[source]["class"],
                "pet": players[source]["pet"]
            }
        if (val_sum>0) and (df_heal[idx_heal]["value"].sum()/val_sum*100 > 10): # if heal > x% of total values -> healer
            players_sep["HEAL"][source] = {
                "class": players[source]["class"],
                "pet": players[source]["pet"]
            }
    return players_sep


def LinePlot(ax, df, subkind, section, players_sep):
    dff = df[df["subkind"]==subkind]

    if section == "All":
        dff = dff
        draw_section = True
    elif section == "Bosses":
        dff = dff[dff["section"] != ""]
        draw_section = True
    elif section == "Trash":
        dff = dff[(dff["section"] == "") & (dff["incombat"])]
        draw_section = True
    else:
        dff = dff[dff["section"] == section]
        draw_section = False

    players = players_sep[subkind]
    for source in players:
        line_color = class_colours[players[source]["class"]]
        if subkind=="DAMAGE":
            val_col = "value"
            idx = (dff["source"]==source) & (dff["target"]!=source) # damage to self shouldnt add to damage (warlock hellfire,...)
            pet_name = players[source]["pet"]
            if pet_name:
                idx = idx | ((dff["source"]==pet_name) & (dff["target"]!=pet_name)) # add pet to damage
        elif subkind=="HEAL":
            val_col = "eheal"
            idx = (dff["source"]==source)
        time = np.array(dff[idx]["timestamp"])
        val = np.array(np.nancumsum(dff[idx][val_col])) #nancumsum since eheal sum can generate nan (if not logged by Kikilogs) -> treat as 0
        if np.size(time) > 0:
            ax.plot(time, val, color=line_color)
            ax.text(time[-1], val[-1], source, fontsize=FONT_SIZE, color=line_color)
    if draw_section:
        df_sections = df["section"].unique()
        for section in df_sections:
            if section != "":
                idx_section = df["section"]==section
                y_min, y_max = ax.get_ylim()
                ax.fill_between(df["timestamp"], y_min, y_max, where=idx_section, label=section, alpha=0.5)
                ax.set_ylim(y_min, y_max) # ylim is changed when using fill_between -> set it back to previous values
        ax.legend(prop={'size': 6})

def BarPlot(ax, df, subkind, section, players_sep, oheal=False):
    dff = df[df["subkind"]==subkind]
    if section == "All":
        dff = dff
    elif section == "Bosses":
        dff = dff[dff["section"] != ""]
    elif section == "Trash":
        dff = dff[(dff["section"] == "") & (dff["incombat"])]
    else:
        dff = dff[dff["section"] == section]

    players = players_sep[subkind]
    x_bar = np.array([])
    y_bar = np.array([])
    y_bar_tot = np.array([])
    bar_colors = np.array([])
    for source in players:
        if subkind=="DAMAGE":
            val_col = "value"
            idx = (dff["source"]==source) & (dff["target"]!=source) # damage to self shouldnt add to damage (warlock hellfire,...)
            pet_name = players[source]["pet"]
            if pet_name:
                idx = idx | ((dff["source"]==pet_name) & (dff["target"]!=pet_name)) # add pet to damage
        elif subkind=="HEAL":
            if oheal:
                val_col = "oheal"
            else:
                val_col = "eheal"
            idx = (dff["source"]==source)
            y_bar_tot = np.append(y_bar_tot, dff[idx]["value"].sum() - dff[idx]["oheal"].sum() - dff[idx]["eheal"].sum())
        x_bar = np.append(x_bar, source)
        y_bar = np.append(y_bar, dff[idx][val_col].sum())
        bar_colors = np.append(bar_colors, class_colours[players[source]["class"]])
    idx_s = np.argsort(y_bar)
    ax.barh(x_bar[idx_s], y_bar[idx_s], color=bar_colors[idx_s])
    for idxs in idx_s:
        if subkind=="DAMAGE":
            ax.text(y_bar[idxs], x_bar[idxs], "{:.0f}".format(y_bar[idxs]), fontsize=FONT_SIZE, va="center")
        elif subkind=="HEAL":
            ax.text(y_bar[idxs], x_bar[idxs], "{:.0f} | {:.0f}".format(y_bar[idxs], y_bar_tot[idxs]), fontsize=FONT_SIZE, va="center")

    ax.tick_params(labelbottom=False)

def BarPlot_Spells(fig, df, subkind, section, players_sep):
    dff = df[df["subkind"]==subkind]
    if section == "All":
        dff = dff
    elif section == "Bosses":
        dff = dff[dff["section"] != ""]
    elif section == "Trash":
        dff = dff[(dff["section"] == "") & (dff["incombat"])]
    else:
        dff = dff[dff["section"] == section]

    players = players_sep[subkind]

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
        if subkind=="DAMAGE":
            val_col = "value"
            idx = (dff["source"]==source) & (dff["target"]!=source) # damage to self shouldnt add to damage (warlock hellfire,...)
            pet_name = players[source]["pet"]
            if pet_name:
                idx = idx | ((dff["source"]==pet_name) & (dff["target"]!=pet_name)) # add pet to damage
        elif subkind=="HEAL":
            val_col = "eheal"
            idx = (dff["source"]==source)
        dff_player = dff[idx]
        spell_unique = dff_player["spell"].unique()
        x_bar = np.array([])
        y_bar = np.array([])
        for spell in spell_unique:
            idx_spell = (dff_player["spell"]==spell)
            x_bar = np.append(x_bar, spell)
            y_bar = np.append(y_bar, dff_player[idx_spell][val_col].sum())
        idx_s = list(np.argsort(y_bar))
        top_spells_max = np.minimum(np.size(y_bar), 4)
        idx_s4 = idx_s[-top_spells_max:]
        ax.barh(x_bar[idx_s4], y_bar[idx_s4])
        for x_txt, y_txt in enumerate(y_bar[idx_s4]):
            ax.text(0, x_txt, "{:.0f}".format(y_txt), fontsize=FONT_SIZE, va="center", ha="left")
        ax.tick_params(labelbottom=False)

def GenSectionPlots(pp, df, players_sep, section):
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches

    fig = plt.figure(figsize=(1920*px,1080*px))
    fig.suptitle("Section: " + section)
    gs = fig.add_gridspec(4,2)
    # Damage Lines
    ax1 = fig.add_subplot(gs[0:2, 0])
    ax1.set_title('Damage')
    LinePlot(ax1, df, "DAMAGE", section, players_sep)
    # Heal Lines
    ax2 = fig.add_subplot(gs[2:4, 0])
    ax2.set_title('Effective Healing')
    LinePlot(ax2, df, "HEAL", section, players_sep)
    # Damage Bars
    ax3 = fig.add_subplot(gs[0:2, 1])
    ax3.set_title('Damage')
    BarPlot(ax3, df, "DAMAGE", section, players_sep)
    # eHeal Bars
    ax4 = fig.add_subplot(gs[2, 1])
    ax4.set_title('Effective Healing')
    BarPlot(ax4, df, "HEAL", section, players_sep)
    # oHeal Bars
    ax5 = fig.add_subplot(gs[3, 1])
    ax5.set_title('Over Healing')
    BarPlot(ax5, df, "HEAL", section, players_sep, oheal=True)
    plt.close()
    pp.savefig(fig)

    # Damage Spells
    fig = plt.figure(figsize=(1920*px,1080*px))
    fig.suptitle("Section: " + section + " (Damage)")
    BarPlot_Spells(fig, df, "DAMAGE", section, players_sep)
    plt.close()
    pp.savefig(fig)
    # Heal Spells
    fig = plt.figure(figsize=(1920*px,1080*px))
    fig.suptitle("Section: " + section + " (Healing)")
    BarPlot_Spells(fig, df, "DAMAGE", section, players_sep)
    plt.close()
    pp.savefig(fig)
   

def Visualise(df, players, folder):
    players_sep = GetPlayersSep(df, players)
    pp = PdfPages(folder + ".pdf")

    # SECTION: ALL
    print("Plot Section: All")
    GenSectionPlots(pp, df, players_sep, "All")

    # SECTION: TRASH
    print("Plot Section: Trash")
    GenSectionPlots(pp, df, players_sep, "Trash")

    # SECTION: BOSSES
    print("Plot Section: Bosses")
    GenSectionPlots(pp, df, players_sep, "Bosses")

    # SECTION: BOSS
    print("Plot Section: Boss")
    sections_unique = df["section"].unique()
    for section in sections_unique:
        if section: # dont show empty section
            GenSectionPlots(pp, df, players_sep, section)

    print("Add Death summary for each player (analyse seconds after as well (death sometimes registered first))\n\
          https://matplotlib.org/stable/gallery/lines_bars_and_markers/timeline.html#sphx-glr-gallery-lines-bars-and-markers-timeline-py")

    pp.close()