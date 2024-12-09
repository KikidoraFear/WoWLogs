
import pandas as pd
import numpy as np
import math
# import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

FONT_SIZE = 6

class_colours = {
    "WARRIOR": "peru",
    "PRIEST": "darkgrey",
    "SHAMAN": "royalblue",#"mediumblue",
    "PALADIN": "lightpink",
    "DRUID": "orange",
    "WARLOCK": "mediumorchid",
    "MAGE": "deepskyblue",
    "ROGUE": "gold",
    "HUNTER": "lawngreen"
}

# def GetPlayersSep(df, players): # separate players by damage/heal
#     df_damage = df[df["kind"]=="DAMAGE"]
#     df_heal = df[df["kind"]=="HEAL"]
#     players_sep = {
#         "DAMAGE": {},
#         "HEAL": {}
#     }
#     for source in players:
#         idx_damage = df_damage["source"]==source
#         idx_heal = df_heal["source"]==source
#         val_sum = df_damage[idx_damage]["value"].sum() + df_heal[idx_heal]["value"].sum()
#         if (val_sum>0) and (df_damage[idx_damage]["value"].sum()/val_sum*100 > 10): # if damage > x% of total values -> damage dealer (careful: Shadow Priest does healing and damage)
#             players_sep["DAMAGE"][source] = {
#                 "class": players[source]["class"],
#                 "pet": players[source]["pet"]
#             }
#         if (val_sum>0) and (df_heal[idx_heal]["value"].sum()/val_sum*100 > 10): # if heal > x% of total values -> healer
#             players_sep["HEAL"][source] = {
#                 "class": players[source]["class"],
#                 "pet": players[source]["pet"]
#             }
#     return players_sep

def GetPlayersSep(df, players): # separate players by damage/heal
    df_damage = df[df["kind"]=="DAMAGE"]
    df_heal = df[df["kind"]=="HEAL"]
    players_sep = {
        "DAMAGE": {},
        "HEAL": {}
    }
    for source in players:
        idx_damage = df_damage["source"]==source
        idx_heal = df_heal["source"]==source
        val_sum = df_damage[idx_damage]["value"].sum() + df_heal[idx_heal]["value"].sum()
        if df_damage[idx_damage]["value"].sum() > 10: # if damage > x% of total values -> damage dealer (careful: Shadow Priest does healing and damage)
            players_sep["DAMAGE"][source] = {
                "class": players[source]["class"],
                "pet": players[source]["pet"]
            }
        if (val_sum>0) and (df_heal[idx_heal]["value"].sum()/val_sum*100 > 10): # if heal > x% of total values -> healer
            players_sep["HEAL"][source] = {
                "class": players[source]["class"],
                "pet": players[source]["pet"]
            }
    # sort by class (so barplot_spell is sorted by class)        
    players_sep["DAMAGE"] = dict(sorted(players_sep["DAMAGE"].items(), key=lambda item: item[1]["class"]))
    players_sep["HEAL"] = dict(sorted(players_sep["HEAL"].items(), key=lambda item: item[1]["class"]))
    return players_sep


def LinePlot(ax, df, kind, section, players_sep):
    dff = df[df["kind"]==kind]

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

    players = players_sep[kind]
    for source in players:
        line_color = class_colours[players[source]["class"]]
        if kind=="DAMAGE":
            val_col = "value"
            idx = (dff["source"]==source) & (dff["target"]!=source) # damage to self shouldnt add to damage (warlock hellfire,...)
            pet_name = players[source]["pet"]
            if pet_name:
                idx = idx | ((dff["source"]==pet_name) & (dff["target"]!=pet_name)) # add pet to damage
        elif kind=="HEAL":
            val_col = "eheal"
            idx = (dff["source"]==source)
        time = np.array(dff[idx]["timestamp"])
        dff = dff.replace({None: np.nan})
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
    
    ax.tick_params(which="both", left=False, labelleft=False)
    ax.tick_params(axis="x", labelsize=FONT_SIZE)

def BarPlot(ax, df, kind, section, players_sep, oheal=False):
    dff = df[df["kind"]==kind]
    if section == "All":
        dff = dff
    elif section == "Bosses":
        dff = dff[dff["section"] != ""]
    elif section == "Trash":
        dff = dff[(dff["section"] == "") & (dff["incombat"])]
    else:
        dff = dff[dff["section"] == section]

    players = players_sep[kind]
    x_bar = np.array([])
    y_bar = np.array([])
    y_bar_heal_prz = np.array([])
    y_bar_est_heal = np.array([])
    bar_colors = np.array([])
    for source in players:
        if kind=="DAMAGE":
            val_col = "value"
            idx = (dff["source"]==source) & (dff["target"]!=source) # damage to self shouldnt add to damage (warlock hellfire,...)
            pet_name = players[source]["pet"]
            if pet_name:
                idx = idx | ((dff["source"]==pet_name) & (dff["target"]!=pet_name)) # add pet to damage
        elif kind=="HEAL":
            if oheal:
                val_col = "oheal"
            else:
                val_col = "eheal"
            idx = (dff["source"]==source)
            heal_add = dff[idx]["value"].sum() - dff[idx]["oheal"].sum() - dff[idx]["eheal"].sum()
            if dff[idx]["oheal"].sum()+dff[idx]["eheal"].sum()>0:
                heal_fac = dff[idx][val_col].sum()/(dff[idx]["oheal"].sum()+dff[idx]["eheal"].sum())
            else:
                heal_fac = 1
            y_bar_heal_prz = np.append(y_bar_heal_prz, heal_fac*100)
            y_bar_est_heal = np.append(y_bar_est_heal, heal_add*heal_fac)
        x_bar = np.append(x_bar, source)
        y_bar = np.append(y_bar, dff[idx][val_col].sum())
        bar_colors = np.append(bar_colors, class_colours[players[source]["class"]])
    idx_s = np.argsort(y_bar)
    ax.barh(x_bar[idx_s], y_bar[idx_s], color=bar_colors[idx_s])
    if kind=="HEAL":
        ax.barh(x_bar[idx_s], y_bar_est_heal[idx_s], left=y_bar[idx_s], color=bar_colors[idx_s], alpha=0.5)
    for idxs in idx_s:
        if kind=="DAMAGE":
            ax.text(y_bar[idxs], x_bar[idxs], "{:.0f}".format(y_bar[idxs]), fontsize=FONT_SIZE, va="center")
        elif kind=="HEAL":
            ax.text(y_bar[idxs], x_bar[idxs], "{:.0f} ({:.0f}%) | {:.0f}".format(
                y_bar[idxs], y_bar_heal_prz[idxs], y_bar_est_heal[idxs]), fontsize=FONT_SIZE, va="center")

    ax.tick_params(which="both", bottom=False, labelbottom=False)
    ax.tick_params(axis="y", labelsize=FONT_SIZE)

def BarPlot_Spells(fig, df, kind, section, players_sep):
    dff = df[df["kind"]==kind]
    if section == "All":
        dff = dff
    elif section == "Bosses":
        dff = dff[dff["section"] != ""]
    elif section == "Trash":
        dff = dff[(dff["section"] == "") & (dff["incombat"])]
    else:
        dff = dff[dff["section"] == section]

    players = players_sep[kind]

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
        if kind=="DAMAGE":
            val_col = "value"
            idx = (dff["source"]==source) & (dff["target"]!=source) # damage to self shouldnt add to damage (warlock hellfire,...)
            pet_name = players[source]["pet"]
            if pet_name:
                idx = idx | ((dff["source"]==pet_name) & (dff["target"]!=pet_name)) # add pet to damage
        elif kind=="HEAL":
            val_col = "eheal"
            idx = (dff["source"]==source)
        dff_player = dff[idx]
        spell_unique = dff_player["spell"].unique()
        x_bar = np.array([])
        y_bar = np.array([])
        y_bar_cnt = np.array([])
        y_bar_crit = np.array([])
        y_bar_hit = np.array([])
        y_bar_avg = np.array([])
        y_bar_max = np.array([])
        for spell in spell_unique:
            idx_spell = (dff_player["spell"]==spell)
            if not spell:
                x_bar = np.append(x_bar, "Hit")
            else:
                x_bar = np.append(x_bar, spell)
            y_bar = np.append(y_bar, dff_player[idx_spell][val_col].sum())
            y_bar_cnt = np.append(y_bar_cnt, dff_player[idx_spell].shape[0])
            y_bar_crit = np.append(y_bar_crit, dff_player[idx_spell & (dff_player["subkind"]=="CRIT")].shape[0])
            y_bar_hit = np.append(y_bar_hit, dff_player[idx_spell & ((dff_player["subkind"]=="HIT") | (dff_player["subkind"]=="CRIT"))].shape[0])
            y_bar_avg = np.append(y_bar_avg, dff_player[idx_spell][val_col].sum()/dff_player[idx_spell].shape[0])
            y_bar_max = np.append(y_bar_max, dff_player[idx_spell][val_col].max())
        idx_s = list(np.argsort(y_bar))
        top_spells_max = np.minimum(np.size(y_bar), 4)
        idx_s4 = idx_s[-top_spells_max:]

        ax.barh(x_bar[idx_s4], y_bar[idx_s4])
        for x_txt, y_txt in enumerate(y_bar[idx_s4]):
            ax.text(0, x_txt, "{:.0f} (#:{:.0f} AVG:{:.0f} M:{:.0f} H:{:.2f}% C:{:.2f}%)".format(
                    y_txt,
                    y_bar_cnt[idx_s4][x_txt],
                    y_bar_avg[idx_s4][x_txt],
                    y_bar_max[idx_s4][x_txt],
                    y_bar_hit[idx_s4][x_txt]/y_bar_cnt[idx_s4][x_txt]*100,
                    y_bar_crit[idx_s4][x_txt]/y_bar_cnt[idx_s4][x_txt]*100
                ), fontsize=FONT_SIZE/2, va="center", ha="left")
        ax.tick_params(which="both", bottom=False, labelbottom=False)
        ax.tick_params(axis="y", labelsize=FONT_SIZE)

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
    fig.suptitle("Section: " + section + " (Effective Healing)")
    BarPlot_Spells(fig, df, "HEAL", section, players_sep)
    plt.close()
    pp.savefig(fig)

def GenDeathBarPlots(pp, df, players, section):
    if section == "All":
        dff = df
    elif section == "Bosses":
        dff = df[df["section"] != ""]
    elif section == "Trash":
        dff = df[(df["section"] == "") & (df["incombat"])]
    else:
        dff = df[df["section"] == section]
    dff.reset_index(inplace=True)

    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    fig = plt.figure(figsize=(1920*px,1080*px))
    fig.suptitle("Section: " + section + " (Deaths)")
    ax = fig.subplots()

    dict_deaths = {}
    for idx_player, player in enumerate(players):
        idxs_deaths = dff[(dff["source"]==player) & (dff["subkind"]=="DIES")].index
        for idx_death in idxs_deaths:
            timestamp_death = dff.loc[idx_death, "timestamp"]
            idx_ext = idx_death
            while (dff.loc[idx_ext, "timestamp"] < timestamp_death + 1) & (idx_ext < len(dff)-1): # include events 1 second after death (sometimes death first, hit taken logged later)
                idx_ext += 1
            while idx_ext>=0: # find last 4 entries,
                if (dff.loc[idx_ext, "timestamp"] < timestamp_death - 20): # maximum of x seconds in the past
                    break
                if (dff.loc[idx_ext, "target"] == player) & (dff.loc[idx_ext, "kind"] == "DAMAGE"):
                    source = dff.loc[idx_ext, "source"]
                    spell = dff.loc[idx_ext, "spell"]
                    if not spell:
                        spell = "Hit"
                    if not source in dict_deaths:
                        dict_deaths[source] = {}
                    if not spell in dict_deaths[source]:
                        dict_deaths[source][spell] = {}
                    if not player in dict_deaths[source][spell]:
                        dict_deaths[source][spell][player] = 1
                    else:
                        dict_deaths[source][spell][player] += 1
                    break
                idx_ext -= 1

    bar_width = 0.25
    bar_mult = 0
    for source in dict_deaths:
        for spell in dict_deaths[source]:
            death_cause = "{}: {}".format(source, spell)
            bar_mult_start = bar_mult
            for player in dict_deaths[source][spell]:
                death_counter = dict_deaths[source][spell][player]
                class_col = class_colours[players[player]["class"]]
                ax.barh(bar_width*bar_mult, death_counter, bar_width, color=class_col)
                ax.text(0.1, bar_width*bar_mult, "{}: {:.0f}".format(player, death_counter), fontsize=FONT_SIZE, va="center", ha="left")
                bar_mult += 1
            bar_mult_end = bar_mult-1
            ax.text(0, bar_width*(bar_mult_start+bar_mult_end)/2, death_cause, fontsize=FONT_SIZE, va="center", ha="right")
            bar_mult += 1

    ax.tick_params(which="both", left=False, labelleft=False)
    ax.tick_params(axis="x", labelsize=FONT_SIZE)
    plt.close()
    pp.savefig(fig)

def GenDeathTables(pp, df, players, section):
    if section == "All":
        dff = df
    elif section == "Bosses":
        dff = df[df["section"] != ""]
    elif section == "Trash":
        dff = df[(df["section"] == "") & (df["incombat"])]
    else:
        dff = df[df["section"] == section]
    dff.reset_index(inplace=True)

    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    fig = plt.figure(figsize=(1920*px,1080*px))
    fig.suptitle("Section: " + section)

    players_amount = len(players)
    rows = math.ceil(math.sqrt(players_amount))
    cols = math.ceil(players_amount/rows)
    gs = fig.add_gridspec(rows,cols)

    for idx_player, player in enumerate(players):
        row = math.floor(idx_player/cols)
        col = idx_player%cols
        ax = fig.add_subplot(gs[row, col])
        class_col = class_colours[players[player]["class"]]
        ax.set_title(player, color=class_col)
        ax.axis("off")
        ax.axis("tight")
        
        idxs_deaths = dff[(dff["source"]==player) & (dff["subkind"]=="DIES")].index
        labels = np.array([])
        timestamps = np.array([])
        for idx_death in idxs_deaths:
            timestamp_death = dff.loc[idx_death, "timestamp"]
            labels = np.append(labels, "{:.2f}: {}".format(timestamp_death, dff.loc[idx_death, "line_mod"]))
            timestamps = np.append(timestamps, timestamp_death)
            idx_ext = idx_death
            while (dff.loc[idx_ext, "timestamp"] < timestamp_death + 1) & (idx_ext < len(dff)-1): # include events 1 second after death (sometimes death first, hit taken logged later)
                idx_ext += 1
            ct_entries = 0
            while (idx_ext>=0) & (ct_entries < 3): # find last 4 entries,
                if (dff.loc[idx_ext, "timestamp"] < timestamp_death - 20): # maximum of x seconds in the past
                    break
                if (dff.loc[idx_ext, "target"] == player) & (dff.loc[idx_ext, "kind"] == "DAMAGE"):
                    timestamps = np.append(timestamps, dff.loc[idx_ext, "timestamp"])
                    labels = np.append(labels, "{:.2f}: {}".format(dff.loc[idx_ext, "timestamp"], dff.loc[idx_ext, "line_mod"]))
                    ct_entries += 1
                idx_ext -= 1
        if np.size(idxs_deaths) > 0:
            idx_s = np.argsort(timestamps)
            tbl_entries = np.transpose(np.array([labels[idx_s]]))
            tbl = ax.table(cellText = tbl_entries,
                rowLoc="left",
                loc="center"
            )
            for j in range(0,len(tbl_entries)):
                tbl[(j,0)].set_height(.08)
    pp.savefig(fig)

def GenDeathPlots(pp, df, players, section):
    if section == "All":
        dff = df
    elif section == "Bosses":
        dff = df[df["section"] != ""]
    elif section == "Trash":
        dff = df[(df["section"] == "") & (df["incombat"])]
    else:
        dff = df[df["section"] == section]
    dff.reset_index(inplace=True)

    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    fig = plt.figure(figsize=(1920*px,1080*px))
    fig.suptitle("Section: " + section + " (Deaths)")

    timestamps = np.array([])
    labels = np.array([])
    lin_cols = np.array([])
    ann_size = np.array([])
    for player in players:
        class_col = class_colours[players[player]["class"]]
        idxs_deaths = dff[(dff["source"]==player) & (dff["subkind"]=="DIES")].index
        for idx_death in idxs_deaths:
            timestamp_death = dff.loc[idx_death, "timestamp"] + 1 # add 1 second so "...dies." comes last (sometimes hit is logged after death)
            timestamps = np.append(timestamps, timestamp_death)
            labels = np.append(labels, dff.loc[idx_death, "line_mod"])
            lin_cols = np.append(lin_cols, class_col)
            ann_size = np.append(ann_size, 2)
            idx_ext = idx_death
            while (dff.loc[idx_ext, "timestamp"] < timestamp_death + 1) & (idx_ext < len(dff)-1): # include events 1 second after death (sometimes death first, hit taken logged later)
                idx_ext += 1
            ct_entries = 0
            while (idx_ext>=0) & (ct_entries < 3): # find last 4 entries,
                if (dff.loc[idx_ext, "timestamp"] < timestamp_death - 20): # maximum of x seconds in the past
                    break
                if (dff.loc[idx_ext, "target"] == player) & (dff.loc[idx_ext, "kind"] == "DAMAGE"):
                    timestamps = np.append(timestamps, dff.loc[idx_ext, "timestamp"])
                    labels = np.append(labels, dff.loc[idx_ext, "line_mod"])
                    lin_cols = np.append(lin_cols, class_col)
                    ann_size = np.append(ann_size, 1)
                    ct_entries += 1
                idx_ext -= 1
    
    idx_s = np.argsort(timestamps)
    levels = np.linspace(10, 100, np.size(timestamps))
    ax = plt.gca()
    ax.vlines(timestamps[idx_s], 0, levels[idx_s], color=lin_cols[idx_s], linewidth=0.1, alpha=0.1)  # The vertical stems.
    ax.plot(timestamps[idx_s], np.zeros_like(timestamps), "-o",
        color="k", markerfacecolor="w")  # Baseline and markers on it.
    # ax.scatter(timestamps[idx_s], levels, c=lin_cols[idx_s])

    if np.size(timestamps) > 0:
        ann_size_mult = np.maximum(np.minimum(200/np.size(timestamps),10),1)
    else:
        ann_size_mult = 1
    # annotate lines
    for d, l, r, c, s in zip(timestamps[idx_s], levels[idx_s], labels[idx_s], lin_cols[idx_s], ann_size[idx_s]*ann_size_mult):
        ax.annotate(r, xy=(d, l),
            # xytext=(-3, np.sign(l)*3), textcoords="offset points",
            horizontalalignment="center",
            verticalalignment="bottom",
            size=s,
            color=c)
    # text
    # for d, l, r, c, s in zip(timestamps[idx_s], levels[idx_s], labels[idx_s], lin_cols[idx_s], ann_size[idx_s]):
    #     plt.text(d, l, r,
    #         # xytext=(-3, np.sign(l)*3), textcoords="offset points",
    #         horizontalalignment="center",
    #         verticalalignment="bottom",
    #         size=s,
    #         color=c)
        
    ax.yaxis.set_visible(False)
    # ax.xaxis.set_visible(False)
    ax.spines[["left", "top", "right"]].set_visible(False)

    plt.close()
    pp.savefig(fig)
   

def Visualise(df, players, folder):
    players_sep = GetPlayersSep(df, players)
    pp = PdfPages(folder + ".pdf")

    # SECTION: ALL
    print("Plot Section: All")
    GenSectionPlots(pp, df, players_sep, "All")

    # SECTION: BOSSES
    print("Plot Section: Bosses")
    GenSectionPlots(pp, df, players_sep, "Bosses")

    # SECTION: TRASH
    print("Plot Section: Trash")
    GenSectionPlots(pp, df, players_sep, "Trash")
    GenDeathPlots(pp, df, players, "Trash")   
    # GenDeathTables(pp, df, players, "Trash")
    GenDeathBarPlots(pp, df, players, "Trash")

    # SECTION: BOSS
    print("Plot Section: Boss")
    sections_unique = df["section"].unique()
    for section in sections_unique:
        if section: # dont show empty section
            print("Section: " + section)
            GenSectionPlots(pp, df, players_sep, section)
            GenDeathPlots(pp, df, players, section)
            # GenDeathTables(pp, df, players, section)
            GenDeathBarPlots(pp, df, players, section)
    print()

    pp.close()