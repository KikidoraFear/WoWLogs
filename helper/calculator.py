bosses = [
    # Ahn'Qiraj
    "Arygos", "Battleguard Sartura", "C'Thun", "Emperor Vek'lor", "Emperor Vek'nilash", "Eye of C'Thun", "Fankriss the Unyielding", "Lord Kri",
        "Merithra of the Dream", "Ouro", "Princess Huhuran", "Princess Yauj", "The Master's Eye", "The Prophet Skeram", "Vem", "Viscidus",
    # Naxxramas
    "Anub'Rekhan", "Grand Widow Faerlina", "Maexxna", "Patchwerk", "Grobbulus", "Gluth", "Thaddius", "Noth the Plaguebringer", "Heigan the Unclean", "Loatheb",
        "Instructor Razuvious", "Gothik the Harvester", "Sapphiron", "Kel'Thuzad", "Lady Blaumeux", #"Thane Korth'azz", "Highlord Mograine", "Sir Zeliek",
    # Zul'Gurub
    "High Priestess Jeklik", "High Priest Venoxis", "High Priestess Mar'li", "High Priest Thekal", "High Priestess Arlokk",
        "Hakkar", "Bloodlord Mandokir", "Jin'do the Hexxer", "Gahz'ranka",
    # The Molten Core
    "Baron Geddon", "Garr", "Gehennas", "Golemagg the Incinerator", "Lucifron", "Magmadar", "Shazzrah", "Sulfuron Harbinger", "Majordomo Executus", "Ragnaros",
    # Blackwing Lair
    "Broodlord Lashlayer", "Chromaggus", "Ebonroc", "Firemaw", "Flamegor", "Lord Victor Nefarius", "Razorgore the Untamed", "Vaelastrasz the Corrupt"
]

def CalcStuff(list_log, t_cd_section):
    # Init
    # Calc Sections
    inp_calc_sections = {
        "incombat": False,
        "t_incombat": 0,
        "section": "",
        "attempt": {}, # attempt[Ouro] = 1
        "t_section": 0,
        "t_cd_section": t_cd_section
    }

    print("Calculate stuff...")
    print("###### if fight starts and boss is detected later, section should still be marked with boss")
    for idx in range(len(list_log)):
        if (idx%1000==0) or (idx==len(list_log)-1):
            print("Line", idx+1, "/", len(list_log), end="\r")

        # Calc Sections
        CalcSections(list_log[idx], inp_calc_sections)

    print()

def CalcSections(line_log, inp):

    # incombat
    if line_log["subkind"] == "DAMAGE":
        inp["incombat"] = True
        inp["t_incombat"] = line_log["timestamp"]
    if line_log["timestamp"] > inp["t_incombat"]+inp["t_cd_section"]:
        inp["incombat"] = False
    line_log["incombat"] = inp["incombat"]

    # sections (bosses)
    # -> sometimes boss is in logs without incombat (e.g. hunter's mark) -> no boss section
    # ToDo: -> sometimes boss fight starts with boss being in the logs (Nefarian, Thaddius) -> boss section
    if (line_log["source"] in bosses) and inp["incombat"]:
        boss = line_log["source"]
        if not boss in inp["attempt"]:
            inp["attempt"][boss] = 1
        inp["section"] = boss
        inp["t_section"] = line_log["timestamp"]
    elif (line_log["target"] in bosses) and inp["incombat"]:
        boss = line_log["target"]
        if not boss in inp["attempt"]:
            inp["attempt"][boss] = 1
        inp["section"] = boss
        inp["t_section"] = line_log["timestamp"]
    if (line_log["timestamp"] > inp["t_section"]+inp["t_cd_section"]) and not inp["incombat"]:
        if inp["section"] in inp["attempt"]:
            inp["attempt"][inp["section"]] += 1
        inp["section"] = ""

    if inp["section"] in inp["attempt"]:
        line_log["section"] = inp["section"] + " (" + str(inp["attempt"][inp["section"]]) + ")"
    else:
        line_log["attempt"] = inp["section"]


# def CalcSections(df, t_cd_section):
#     print("Calculate sections...")
#     flg_combat = False
#     flg_combat_t = 0
#     flg_boss = False
#     flg_boss_t = 0
#     df_dict = df.to_dict()
#     incombat = {}
#     section = {}
#     for idx in range(len(df)):
#         if (idx%1000==0) or (idx==len(df)-1):
#             print("Line", idx+1, "/", len(df), end="\r")
#         if df.loc[idx, "subkind"] == "DAMAGE":
#             flg_combat = True
#             flg_combat_t = df.loc[idx, "timestamp"]
#         if df.loc[idx, "source"] in bosses:
#             boss = df.loc[idx, "source"]
#             flg_boss = True
#             flg_boss_t = df.loc[idx, "timestamp"]
#         elif df.loc[idx, "target"] in bosses:
#             boss = df.loc[idx, "target"]
#             flg_boss = True
#             flg_boss_t = df.loc[idx, "timestamp"]
#         if df.loc[idx, "timestamp"] > flg_combat_t+t_cd_section:
#             flg_combat = False
#         if df.loc[idx, "timestamp"] > flg_boss_t+t_cd_section:
#             flg_boss = False
        # if flg_combat:
        #     df.loc[idx, "incombat"] = True
        # if flg_boss:
        #     df.loc[idx, "section"] = boss

    # 10 | DAMAGE
    # 12 | HEAL
    # 14 | DAMAGE
    # 30 | HEAL
    # 31 | DAMAGE