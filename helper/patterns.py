
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
    ["PERIODICAURADAMAGEOTHEROTHER", "%s suffers %d %s damage from %s's %s.", ["target", "value", "school", "source", "spell"], "DAMAGE", "HIT"],
    # HEAL - added eheal
    ["PERIODICAURAHEALOTHEROTHER", "%s gains %d health from %s's %s.", ["target", "value", "source", "spell"], "HEAL", "HIT"],

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
    ["SPELLPERFORMGOOTHER", "%s performs %s.", ["source", "spell"], "SPELL", "PERFORM"],
    # RESIST
    ["SPELLRESISTOTHEROTHER", "%s's %s was resisted by %s.", ["source", "spell", "target"], "DAMAGE", "RESISTED"],
    ["SPELLRESISTOTHERSELF", "%s's %s was resisted.", ["source", "spell"], "DAMAGE", "RESISTED"],
    # DODGED
    ["SPELLDODGEDOTHEROTHER", "%s's %s was dodged by %s.", ["source", "spell", "target"], "DAMAGE", "DODGED"],
    ["SPELLDODGEDOTHERSELF", "%s's %s was dodged.", ["source", "spell"], "DAMAGE", "DODGED"],
    # PARRIED
    ["SPELLPARRIEDOTHEROTHER", "%s's %s was parried by %s.", ["source", "spell", "target"], "DAMAGE", "PARRIED"],
    ["SPELLPARRIEDOTHERSELF", "%s's %s was parried.", ["source", "spell"], "DAMAGE", "PARRIED"],
    ["SPELLPARRIEDSELFOTHER", "%s's %s is parried by %s.", [], "DAMAGE", "PARRIED"], # MODIFIED "Your %s is parried by %s."
    # FAILCAST
    ["SPELLFAILCASTOTHER", "%s fails to cast %s: %s.", ["source", "spell", "school"], "SPELL", "FAILCAST"],
    # IMMUNE
    ["SPELLIMMUNEOTHEROTHER", "%s's %s fails. %s is immune.", ["source", "spell", "target"], "DAMAGE", "IMMUNE"],
    ["SPELLIMMUNESELFOTHER", "%s's %s failed. %s is immune.", ["source", "spell", "target"], "DAMAGE", "IMMUNE"], # MODIFIED "Your %s failed. %s is immune."
    # MISS
    ["SPELLMISSOTHEROTHER", "%s's %s missed %s.", ["source", "spell", "target"], "DAMAGE", "MISSED"],
    # BLOCK
    ["SPELLBLOCKEDOTHEROTHER", "%s's %s was blocked by %s.", ["source", "spell", "target"], "DAMAGE", "BLOCKED"],
    # INTERRUPT
    ["SPELLINTERRUPTOTHEROTHER", "%s interrupts %s's %s.", ["source", "target", "spell"], "SPELL", "INTERRUPT"],
    # DISMISSPET
    ["SPELLDISMISSPETOTHER", "%s's %s is dismissed.", ["source", "school"], "SPELL", "DISMISSPET"],
    # FAILPERFORM
    ["SPELLFAILPERFORMOTHER", "%s fails to perform %s: %s.", ["source", "spell", "school"], "SPELL", "FAILPERFORM"],
    # EVADE
    ["SPELLEVADEDOTHEROTHER", "%s's %s was evaded by %s.", ["source", "spell", "target"], "DAMAGE", "EVADED"],
    # REFLECT
    ["SPELLREFLECTOTHEROTHER", "%s's %s is reflected back by %s.", ["source", "spell", "target"], "SPELL", "REFLECTED"],

    ##############
    # SPELLPOWER #
    ##############
    # DRAIN
    ["SPELLPOWERDRAINOTHEROTHER", "%s's %s drains %d %s from %s.", ["source", "spell", "value", "school", "target"], "SPELLPOWER", "DRAIN"],
    
    ##########
    # IMMUNE #
    ##########
    ["IMMUNESPELLOTHEROTHER", "%s is immune to %s's %s.", ["target", "source", "spell"], "DAMAGE", "IMMUNE"],

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
    ["SPELLLOGSCHOOLOTHEROTHER", "%s's %s hits %s for %d %s damage.", ["source", "spell", "target", "value", "school"], "DAMAGE", "HIT"], # parse before COMBATHITSCHOOLOTHEROTHER
    ["SPELLLOGCRITSCHOOLOTHEROTHER", "%s's %s crits %s for %d %s damage.", ["source", "spell", "target", "value", "school"], "DAMAGE", "CRIT"], # parse before COMBATHITCRITSCHOOLOTHEROTHER
    ["SPELLLOGOTHEROTHER", "%s's %s hits %s for %d.", ["source", "spell", "target", "value"], "DAMAGE", "HIT"], # parse before COMBATHITOTHEROTHER
    ["SPELLLOGCRITOTHEROTHER", "%s's %s crits %s for %d.", ["source", "spell", "target", "value"], "DAMAGE", "CRIT"], # parse before COMBATHITCRITOTHEROTHER
    # ABSORB
    ["SPELLLOGABSORBOTHEROTHER", "%s's %s is absorbed by %s.", ["source", "spell", "target"], "SPELLLOG", "ABSORB"],

    ##############
    # SPELLSPLIT #
    ##############
    ["SPELLSPLITDAMAGEOTHEROTHER", "%s's %s causes %s %d damage.", ["source", "spell", "target", "value"], "DAMAGE", "HIT"],

    ##########
    # HEALED #
    ##########
    ["HEALEDCRITOTHEROTHER", "%s's %s critically heals %s for %d.", ["source", "spell", "target", "value"], "HEAL", "CRIT"], # parse before HEALEDOTHEROTHER
    ["HEALEDOTHEROTHER", "%s's %s heals %s for %d.", ["source", "spell", "target", "value"], "HEAL", "HIT"],

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
    ["COMBATHITOTHEROTHER", "%s hits %s for %d.", ["source", "target", "value"], "DAMAGE", "HIT"],
    ["COMBATHITSCHOOLOTHEROTHER", "%s hits %s for %d %s damage.", ["source", "target", "value", "school"], "DAMAGE", "HIT"],
    # HITCRIT
    ["COMBATHITCRITOTHEROTHER", "%s crits %s for %d.", ["source", "target", "value"], "DAMAGE", "CRIT"],
    ["COMBATHITCRITSCHOOLOTHEROTHER", "%s crits %s for %d %s damage.", ["source", "target", "value", "school"], "DAMAGE", "CRIT"],

    ##########
    # MISSED #
    ##########
    ["MISSEDOTHEROTHER", "%s misses %s.", ["source", "target"], "DAMAGE", "MISS"],

    ######
    # VS #
    ######
    # PARRY
    ["VSPARRYOTHEROTHER", "%s attacks. %s parries.", ["source", "target"], "DAMAGE", "PARRY"],
    # ABSORB
    ["VSABSORBOTHEROTHER", "%s attacks. %s absorbs all the damage.", ["source", "target"], "DAMAGE", "ABSORB"],
    # DODGE
    ["VSDODGEOTHEROTHER", "%s attacks. %s dodges.", ["source", "target"], "DAMAGE", "DODGE"],
    # BLOCK
    ["VSBLOCKOTHEROTHER", "%s attacks. %s blocks.", ["source", "target"], "DAMAGE", "BLOCK"],
    # IMMUNE
    ["VSIMMUNEOTHEROTHER", "%s attacks but %s is immune.", ["source", "target"], "DAMAGE", "IMMUNE"],
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
    ["DAMAGESHIELDOTHEROTHER", "%s reflects %d %s damage to %s.", ["target", "value", "school", "source"], "DAMAGE", "REFLECTS"],

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
    ["SPELLLOGABSORBOTHERSELF", "%s absorbs %s's %s.", ["target", "source", "spell"], "DAMAGE", "ABSORB"],

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