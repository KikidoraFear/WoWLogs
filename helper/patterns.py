
def PreparePatterns(patterns):
    for idx in range(len(patterns)):
        patterns[idx][1] = patterns[idx][1].replace("%s", "(.+)")
        patterns[idx][1] = patterns[idx][1].replace("%d", "(\\d+)")
    return patterns

# dont add SELF (strings with You or Your) -> You and Your is replaced by source via InsertSource()
# Parse order is important!
patterns_base = [

    ################
    # PERIODICAURA #
    ################
    # DAMAGE
    ["PERIODICAURADAMAGEOTHEROTHER", "%s suffers %d %s damage from %s's %s.", ["target", "value", "school", "source", "spell"], "PERIODICAURA", "DAMAGE"],
    # HEAL - added eheal
    ["PERIODICAURAHEALOTHEROTHER", "%s gains %d health from %s's %s.", ["target", "value", "source", "spell"], "PERIODICAURA", "HEAL"],

    #########
    # POWER #
    #########
    # GAIN
    ["POWERGAINOTHEROTHER", "%s gains %d %s from %s's %s.", ["target", "value", "school", "source", "spell"], "POWER", "GAIN"],
    ["POWERGAINSELFOTHER", "%s gains %d %s from %s.", ["target", "value", "school", "spell"], "POWER", "GAIN"], # source has to be added later (=data_source)

    ########
    # AURA #
    ########
    # ADDED
    ["AURAADDEDOTHERHARMFUL", "%s is afflicted by %s.", ["target", "spell"], "AURA", "ADDED"],
    ["AURAADDEDOTHERHELPFUL", "%s gains %s.", ["target", "spell"], "AURA", "ADDED"],
    # REMOVED
    ["AURAREMOVEDOTHER", "%s fades from %s.", ["spell", "target"], "AURA", "REMOVED"],
    # DISPEL
    ["AURADISPELOTHER", "%s's %s is removed.", ["source", "spell"], "AURA", "DISPEL"],

    #########
    # SPELL #
    #########
    # CAST
    ["SPELLCASTOTHERSTART", "%s begins to cast %s.", ["source", "spell"], "SPELL", "CAST"],
    ["SPELLCASTGOOTHERTARGETTED", "%s casts %s on %s.", ["source", "spell", "target"], "SPELL", "CAST"],
    ["SPELLCASTGOOTHER", "%s casts %s.", ["source", "spell"], "SPELL", "CAST"],
    # PERFORM
    ["SPELLPERFORMOTHERSTART", "%s begins to perform %s.", ["source", "spell"], "SPELL", "PERFORM"],
    ["SPELLTERSEPERFORM_OTHER", "%s performs %s.", ["source", "spell"], "SPELL", "PERFORM"],
    # RESIST
    ["SPELLRESISTOTHEROTHER", "%s's %s was resisted by %s.", ["source", "spell", "target"], "SPELL", "RESIST"],
    ["SPELLRESISTOTHERSELF", "%s's %s was resisted.", ["source", "spell"], "SPELL", "RESISTED"],
    # DODGED
    ["SPELLDODGEDOTHEROTHER", "%s's %s was dodged by %s.", ["source", "spell", "target"], "SPELL", "DODGED"],
    ["SPELLDODGEDOTHERSELF", "%s's %s was dodged.", ["source", "spell"], "SPELL", "DODGED"],
    # PARRIED
    ["SPELLPARRIEDOTHEROTHER", "%s's %s was parried by %s.", ["source", "spell", "target"], "SPELL", "PARRIED"],
    ["SPELLPARRIEDOTHERSELF", "%s's %s was parried.", ["source", "spell"], "SPELL", "PARRIED"],
    # FAILCAST
    ["SPELLFAILCASTOTHER", "%s fails to cast %s: %s.", ["source", "spell", "school"], "SPELL", "FAILCAST"],
    # IMMUNE
    ["SPELLIMMUNEOTHEROTHER", "%s's %s fails. %s is immune.", ["source", "spell", "target"], "SPELL", "IMMUNE"],
    ["SPELLIMMUNESELFOTHER", "%s's %s failed. %s is immune.", ["source", "spell", "target"], "SPELL", "IMMUNE"], # MODIFIED "Your %s failed. %s is immune."
    # MISS
    ["SPELLMISSOTHEROTHER", "%s's %s missed %s.", ["source", "spell", "target"], "SPELL", "MISS"],
    # BLOCK
    ["SPELLBLOCKEDOTHEROTHER", "%s's %s was blocked by %s.", ["source", "spell", "target"], "SPELL", "BLOCK"],
    # INTERRUPT
    ["SPELLINTERRUPTOTHEROTHER", "%s interrupts %s's %s.", ["source", "target", "spell"], "SPELL", "INTERRUPT"],
    # DISMISSPET
    ["SPELLDISMISSPETOTHER", "%s's %s is dismissed.", ["source", "school"], "SPELL", "DISMISSPET"],
    # FAILPERFORM
    ["SPELLFAILPERFORMOTHER", "%s fails to perform %s: %s.", ["source", "spell", "school"], "SPELL", "FAILPERFORM"],
    # EVADE
    ["SPELLEVADEDOTHEROTHER", "%s's %s was evaded by %s.", ["source", "spell", "target"], "SPELL", "EVADED"],
    # REFLECT
    ["SPELLREFLECTOTHEROTHER", "%s's %s is reflected back by %s.", ["source", "spell", "target"], "SPELL", "EVADED"],

    ##############
    # SPELLPOWER #
    ##############
    # DRAIN
    ["SPELLPOWERDRAINOTHEROTHER", "%s's %s drains %d %s from %s.", ["source", "spell", "value", "school", "target"], "SPELLPOWER", "DRAIN"],
    
    ##########
    # IMMUNE #
    ##########
    ["IMMUNESPELLOTHEROTHER", "%s is immune to %s's %s.", ["target", "source", "spell"], "IMMUNE", "SPELL"],

    #########
    # INSTA #
    #########
    # KILL
    ["INSTAKILLOTHER", "%s is killed by %s.", ["target", "source"], "INSTA", "KILL"],

    ########
    # UNIT #
    ########
    # DIES
    ["UNITDIESOTHER", "%s dies.", ["source"], "UNIT", "DIES"],
    # DESTROYED
    ["UNITDESTROYEDOTHER", "%s is destroyed.", ["source"], "UNIT", "DESTROYED"],

    ############
    # SPELLLOG #
    ############
    # LOG
    ["SPELLLOGSCHOOLOTHEROTHER", "%s's %s hits %s for %d %s damage.", ["source", "spell", "target", "value", "school"], "SPELLLOG", "DAMAGE"], # parse before COMBATHITSCHOOLOTHEROTHER
    ["SPELLLOGCRITSCHOOLOTHEROTHER", "%s's %s crits %s for %d %s damage.", ["source", "spell", "target", "value", "school"], "SPELLLOG", "DAMAGE"], # parse before COMBATHITCRITSCHOOLOTHEROTHER
    ["SPELLLOGOTHEROTHER", "%s's %s hits %s for %d.", ["source", "spell", "target", "value"], "SPELLLOG", "DAMAGE"], # parse before COMBATHITOTHEROTHER
    ["SPELLLOGCRITOTHEROTHER", "%s's %s crits %s for %d.", ["source", "spell", "target", "value"], "SPELLLOG", "DAMAGE"], # parse before COMBATHITCRITOTHEROTHER
    # ABSORB
    ["SPELLLOGABSORBOTHEROTHER", "%s's %s is absorbed by %s.", ["source", "spell", "target"], "SPELLLOG", "ABSORB"],

    ##############
    # SPELLSPLIT #
    ##############
    ["SPELLSPLITDAMAGEOTHEROTHER", "%s's %s causes %s %d damage.", ["source", "spell", "target", "value"], "SPELLSPLIT", "DAMAGE"],

    ##########
    # HEALED #
    ##########
    ["HEALEDCRITOTHEROTHER", "%s's %s critically heals %s for %d.", ["source", "spell", "target", "value"], "HEALED", "HEAL"], # parse before HEALEDOTHEROTHER
    ["HEALEDOTHEROTHER", "%s's %s heals %s for %d.", ["source", "spell", "target", "value"], "HEALED", "HEAL"],

    #########
    # TRADE #
    #########
    # SKILL
    ["TRADESKILL_LOG_THIRDPERSON", "%s creates %s.", ["source", "school"], "TRADE", "SKILL"],

    ########
    # FEED #
    ########
    # PET
    ["FEEDPET_LOG_THIRDPERSON", "%s's pet begins eating a %s.", ["source", "school"], "FEED", "PET"],
   
    ##########
    # COMBAT #
    ##########
    # HIT
    ["COMBATHITOTHEROTHER", "%s hits %s for %d.", ["source", "target", "value"], "COMBAT", "DAMAGE"],
    ["COMBATHITSCHOOLOTHEROTHER", "%s hits %s for %d %s damage.", ["source", "target", "value", "school"], "COMBAT", "DAMAGE"],
    # HITCRIT
    ["COMBATHITCRITOTHEROTHER", "%s crits %s for %d.", ["source", "target", "value"], "COMBAT", "DAMAGE"],
    ["COMBATHITCRITSCHOOLOTHEROTHER", "%s crits %s for %d %s damage.", ["source", "target", "value", "school"], "COMBAT", "DAMAGE"],

    ##########
    # MISSED #
    ##########
    ["MISSEDOTHEROTHER", "%s misses %s.", ["source", "target"], "MISSED", ""],

    ######
    # VS #
    ######
    # PARRY
    ["VSPARRYOTHEROTHER", "%s attacks. %s parries.", ["source", "target"], "VS", "PARRY"],
    # ABSORB
    ["VSABSORBOTHEROTHER", "%s attacks. %s absorbs all the damage.", ["source", "target"], "VS", "ABSORB"],
    # DODGE
    ["VSDODGEOTHEROTHER", "%s attacks. %s dodges.", ["source", "target"], "VS", "DODGE"],
    # BLOCK
    ["VSBLOCKOTHEROTHER", "%s attacks. %s blocks.", ["source", "target"], "VS", "BLOCK"],
    # IMMUNE
    ["VSIMMUNEOTHEROTHER", "%s attacks but %s is immune.", ["source", "target"], "VS", "IMMUNE"],
    # ENVIRONMENTALDAMAGE_FALLING
    ["VSENVIRONMENTALDAMAGE_FALLING_OTHER", "%s falls and loses %d health.", ["target", "value"], "VS", "ENVIRONMENTALDAMAGE_FALLING"],
    # ENVIRONMENTALDAMAGE_LAVA
    ["VSENVIRONMENTALDAMAGE_LAVA_OTHER", "%s loses %d health for swimming in lava.", ["target", "value"], "VS", "ENVIRONMENTALDAMAGE_LAVA"],
    # ENVIRONMENTALDAMAGE_FIRE
    ["VSENVIRONMENTALDAMAGE_FIRE_OTHER", "%s suffers %d points of fire damage.", ["target", "value"], "VS", "ENVIRONMENTALDAMAGE_FIRE"],

    ##########
    # DAMAGE #
    ##########
    # SHIELD
    ["DAMAGESHIELDOTHEROTHER", "%s reflects %d %s damage to %s.", ["target", "value", "school", "source"], "DAMAGESHIELD", "DAMAGE"],

    #########
    # PARTY #
    #########
    # KILL
    ["PARTYKILLOTHER", "%s is slain by %s!", ["target", "source"], "PARTY", "KILL"],



    # | MODIFIED   |
    # | BECAUSE OF |
    # | YOU/YOUR   |
    # v            v

    ###########
    # FACTION #
    ###########
    # INCREASED
    ["FACTION_STANDING_INCREASED", "%s's %s reputation has increased by %d.", ["source", "school", "value"], "FACTION", "INCREASED"], # FACTION_STANDING_INCREASED only possible for Your %s -> changed to %s's %s

    ##############
    # DURABILITY #
    ##############
    ["DURABILITYDAMAGE_DEATH", "%s's equipped items suffer a 10% durability loss.", ["source"], "DURABILITY", "DAMAGE_DEATH"],

    ############
    # SPELLLOG #
    ############
    # ABSORB
    ["SPELLLOGABSORBOTHERSELF", "%s absorbs %s's %s.", ["target", "source", "spell"], "SPELLLOG", "ABSORB"],

    #########
    # PARTY #
    #########
    # KILL
    ["SELFKILLOTHER", "%s has slain %s!", ["source", "target"], "PARTY", "KILL"],

]

patterns_trailer = [
    #########
    # EMPTY #
    #########
    ["EMPTY_TRAILER", "", [], "EMPTY"],

    #########
    # BLOCK #
    #########
    ["BLOCK_TRAILER", " (%d blocked)", ["value"], "BLOCK"],
]