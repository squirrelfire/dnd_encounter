from copy import deepcopy
from handbook import HandBook as HB

class PC():
    """
    Provides the basic building blocks of the Player Characters (PC) for the party. Every
    class has their unique skills, which is why 
    """
    def __init__(self, level):
        self.level = level
        self.base_stats = [17, 14, 14, 12, 12, 9]
        self.proficiency = [2,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0]
        self.pro = sum(self.proficiency[0:self.level+1])

    def adjust_stats(self):
        # At certain level points characters gain bonuses to their stats
        if self.level >= 17:
            self.base_stats[0] += 3
            self.base_stats[1] += 3
            self.base_stats[4] += 2
        elif self.level < 17 and self.level >= 14:
            self.base_stats[0] += 3
            self.base_stats[1] += 2
            self.base_stats[4] += 1
        elif self.level < 14 and self.level >= 8:
            self.base_stats[0] += 3
            self.base_stats[1] += 1
        elif self.level < 8 and self.level >= 4:
            self.base_stats[0] += 2

class Wizard(PC, HB):
    """
    The class for building wizards. The only function of note here is cast_spell, which
    handles the rules for casting spells by the PC.
    """

    def assign_stats(self):
        # generates the PC stats based on the template
        self.stats = {
            'int': self.base_stats[0],
            'wis': self.base_stats[1],
            'con': self.base_stats[2],
            'cha': self.base_stats[3],
            'dex': self.base_stats[4],
            'str': self.base_stats[5]
        }
    
    def assign_bonus(self):
        # creates the stats bonuses
        self.bonus = {
            'int': self.get_bonus(self.stats['int']),
            'wis': self.get_bonus(self.stats['wis']),
            'cha': self.get_bonus(self.stats['cha']),
            'str': self.get_bonus(self.stats['str']),
            'dex': self.get_bonus(self.stats['dex']),
            'con': self.get_bonus(self.stats['con']),
        }
    
    def assign_saves(self):
        # creates the saving throws
        self.saves = {
            'str': self.bonus['str'],
            'dex': self.bonus['dex'],
            'con': self.bonus['con'],
            'int': self.bonus['int'],
            'wis': self.bonus['wis'],
            'cha': self.bonus['cha']
        }

    def build(self):
        # builds the wizard PC
        self.adjust_stats()
        self.assign_stats()
        self.assign_bonus()
        self.assign_saves()
        self.saves['int'] += self.pro
        self.saves['wis'] += self.pro
        self.name = 'wizard'
        self.status = 'normal'
        self.stats_save = None
        self.status_dc = 0
        self.actions = 1
        self.hp = 6 + self.bonus['con'] 
        self.hp += self.roll_dice(self.level,6) + self.level * self.bonus['con']
        self.base_hp = self.hp
        self.spell_atk = self.pro + self.bonus['int']
        self.dc = 8 + self.spell_atk
        self.ac = 17 + self.bonus['dex']
        self.atk = self.pro + self.bonus['str']
        self.dodge = False

        self.spell_slots = deepcopy(self.spell_book[self.level])

        if self.level == 20:
            self.spell_slots[3] += 2
            self.spell_slots[0] += 1
            self.spell_slots[1] += 1
        elif self.level >= 18:
            self.spell_slots[0] += 1
            self.spell_slots[1] += 1
    
    def make_save(self, dc, stype, damage=0, status=None):
        # handles the saving throws
        save = self.save_roll(dc, self.saves[stype])
        if damage and save and status:
            self.hp -= int(damage/2) + 1
        if damage and save and not status:
            self.hp -= int(damage/2) + 1
        elif damage and status and not save:
            self.hp -= damage
            self.status = status
            self.status_dc = dc
            self.status_save = stype
        elif status and not damage and not save:
            self.status = status
            self.status = status
            self.status_dc = dc
            self.status_save = stype
    
    def cast_spell(self):
        # chooses spells and handles the casting mechanics
        wiz = HB.wizard_spells
        spell_level = len(self.spell_slots) - 1
        if len(HB.monsters) > 2 and spell_level > 2:
            spell = wiz['all'][spell_level]
            dmg = spell['dmg'] + self.spell_atk
            for v in HB.monsters.values():
                v.make_save(self.dc, spell['save'], dmg)
            self.is_dead()
        else:
            t = self.get_target([m for m in HB.monsters.keys()])
            target = HB.monsters[t]
            spell = wiz['one'][spell_level]
            dmg = wiz['one'][spell_level]['dmg'] + self.spell_atk
            if spell['type'] == 'attack':
                self.make_attack(target, self.spell_atk, dmg)
            else:
                s_throw = wiz['one'][spell_level]['save']
                target.make_save(self.dc, s_throw, dmg)
                self.is_dead()
        
        if self.spell_slots[-1] == 1:
            self.spell_slots.pop()
        else:
            self.spell_slots[-1] -= 1
    
    def take_action(self):
        if self.spell_slots:
            self.cast_spell()
        elif self.level >= 13:
            dmg = 30 + self.spell_atk + self.roll_dice(7,8)
            t = self.get_target([m for m in HB.monsters.keys()])
            target = HB.monsters[t]
            target.make_save(self.dc, 'con', damage=dmg)
        else:
            t = self.get_target([m for m in HB.monsters.keys()])
            target = HB.monsters[t]
            self.make_attack(target, self.atk, self.roll_dice(1,8))

class Fighter(PC, HB):
    """
    Builds the fighter PC and handles their actions
    """

    def assign_stats(self):
        # generates the PC stats based on the template
        self.stats = {
            'int': self.base_stats[5],
            'wis': self.base_stats[4],
            'con': self.base_stats[1],
            'cha': self.base_stats[3],
            'dex': self.base_stats[2],
            'str': self.base_stats[0]
        }
    
    def assign_bonus(self):
        # creates the stats bonuses
        self.bonus = {
            'int': self.get_bonus(self.stats['int']),
            'wis': self.get_bonus(self.stats['wis']),
            'cha': self.get_bonus(self.stats['cha']),
            'str': self.get_bonus(self.stats['str']),
            'dex': self.get_bonus(self.stats['dex']),
            'con': self.get_bonus(self.stats['con']),
        }
    
    def assign_saves(self):
        # creates the saving throws
        self.saves = {
            'str': self.bonus['str'] + self.pro,
            'dex': self.bonus['dex'],
            'con': self.bonus['con'] + self.pro,
            'int': self.bonus['int'],
            'wis': self.bonus['wis'],
            'cha': self.bonus['cha']
        }

    def build(self):
        # handles the building of the fighter character
        self.adjust_stats()
        self.assign_stats()
        self.assign_bonus()
        self.assign_saves()
        self.name = 'fighter'
        self.status = 'normal'
        self.stats_save = None
        self.status_dc = 0
        self.actions = 1
        self.hp = 8 + self.bonus['con'] 
        self.hp += self.roll_dice(self.level,8) + self.level * self.bonus['con']
        self.base_hp = self.hp
        self.ac = 14 + self.bonus['dex'] + 2 + 1
        self.atk = self.pro + self.bonus['str']
        self.crit = 20
        self.reroll = 0
        self.surge = 0
        self.heal = 0
        self.dodge = False

        if self.level == 20:
            self.ac = 18 + self.bonus['dex'] + 2 + 2
            self.surge = 2
            self.actions += 3
            self.heal = self.roll_dice(1,10) + self.level
            self.reroll = 3
            self.crit = 18
        elif self.level >= 17:
            self.ac = 18 + self.bonus['dex'] + 2 + 2
            self.reroll = 3
            self.actions += 2
            self.surge = 1
            self.crit = 18
        elif self.level >= 15:
            self.ac = 18 + self.bonus['dex'] + 2 + 2
            self.reroll = 2
            self.actions += 2
            self.surge = 1
            self.crit = 18
        elif self.level >= 13:
            self.ac = 17 + self.bonus['dex'] + 2 + 2
            self.reroll = 2
            self.actions += 2
            self.surge = 1
            self.crit = 19
        elif self.level >= 11:
            self.ac = 17 + self.bonus['dex'] + 2 + 2
            self.reroll = 1
            self.actions += 2
            self.surge = 1
            self.crit = 19
        elif self.level >= 10:
            self.ac = 17 + self.bonus['dex'] + 2 + 2
            self.reroll = 1
            self.actions += 1
            self.surge = 1
            self.crit = 19
        elif self.level >= 9:
            self.ac = 16 + self.bonus['dex'] + 2 + 1
            self.reroll = 1
            self.actions += 1
            self.surge = 1
            self.crit = 19
        elif self.level >= 5:
            self.ac = 16 + self.bonus['dex'] + 2 + 1
            self.actions += 1
            self.surge = 1
            self.crit = 19
        elif self.level >= 3:
            self.surge = 1
            self.crit = 19
        elif self.level >= 2:
            self.surge = 1

    def make_save(self, dc, stype, damage=0, status=None):
        # handles saving throws for the fighter
        save = self.save_roll(dc, self.saves[stype])

        # uses rerolls on failed saving throws
        while self.reroll and not save:
            save = self.save_roll(dc, self.saves[stype])
            self.reroll -= 1

        if damage and save and status:
            self.hp -= int(damage/2) + 1
        if damage and save and not status:
            self.hp -= int(damage/2) + 1
        elif damage and status and not save:
            self.hp -= damage
            self.status = status
            self.status_dc = dc
            self.status_save = stype
        elif status and not damage and not save:
            self.status = status
            self.status = status
            self.status_dc = dc
            self.status_save = stype

    def take_action(self):
        # chooses each action for the fighter and executes the action
        # fighter can have more than one action per turn
        acts = 0

        # checks and uses the healing surge
        if self.level >= 18 and self.hp < self.base_hp / 2:
            if self.base_hp < self.hp + self.bonus['con'] + 5:
                self.hp = self.base_hp
            else:
                self.hp += self.bonus['con'] + 5

        while acts < self.actions:
            if self.surge and acts > 0:
                acts -= 1
                self.surge -= 1

            if self.hp < self.base_hp and self.heal:
                if self.hp + self.heal > self.base_hp:
                    self.hp = self.base_hp
                else:
                    self.hp += self.heal
                self.heal = 0
            # makes an attack
            elif HB.monsters:
                t = self.get_target([m for m in HB.monsters.keys()])
                target = HB.monsters[t]
                self.make_attack(target, self.atk, self.roll_dice(1,10), self.crit)
            
            acts += 1

class Cleric(PC, HB):
    """
    Builds the cleric PC and handles all the mechanics for healing players.
    """

    def assign_stats(self):
        # generates the PC stats based on the template
        self.stats = {
            'int': self.base_stats[4],
            'wis': self.base_stats[0],
            'con': self.base_stats[1],
            'cha': self.base_stats[2],
            'dex': self.base_stats[5],
            'str': self.base_stats[3]
        }
    
    def assign_bonus(self):
        # creates stat bonuses
        self.bonus = {
            'int': self.get_bonus(self.stats['int']),
            'wis': self.get_bonus(self.stats['wis']),
            'cha': self.get_bonus(self.stats['cha']),
            'str': self.get_bonus(self.stats['str']),
            'dex': self.get_bonus(self.stats['dex']),
            'con': self.get_bonus(self.stats['con']),
        }
    
    def assign_saves(self):
        # creates the saving throws
        self.saves = {
            'str': self.bonus['str'],
            'dex': self.bonus['dex'],
            'con': self.bonus['con'] + self.pro,
            'int': self.bonus['int'],
            'wis': self.bonus['wis'] + self.pro,
            'cha': self.bonus['cha']
        }

    def build(self):
        # builds the cleric
        self.adjust_stats()
        self.assign_stats()
        self.assign_bonus()
        self.assign_saves()
        self.name = 'cleric'
        self.status = 'normal'
        self.stats_save = None
        self.status_dc = 0
        self.actions = 1
        self.hp = 8 + self.bonus['con'] 
        self.hp += self.roll_dice(self.level,8) + self.level * self.bonus['con']
        self.base_hp = self.hp
        self.ac = 14 + self.bonus['dex'] + 2 + 2
        self.spell_atk = self.pro + self.bonus['wis']
        self.dc = 8 + self.spell_atk
        self.atk = self.pro + self.bonus['str']
        self.crit = 20
        self.reroll = 0
        self.x_dmg = 0
        self.dodge = False

        self.spell_slots = deepcopy(HB.divine[self.level])

        if self.level >= 14:
            self.x_dmg = 14
        elif self.level >= 8:
            self.x_dmg = 8

    def make_save(self, dc, stype, damage=0, status=None):
        # handles saving throws
        save = self.save_roll(dc, self.saves[stype])
        if damage and save and status:
            self.hp -= int(damage/2) + 1
        if damage and save and not status:
            self.hp -= int(damage/2) + 1
        elif damage and status and not save:
            self.hp -= damage
            self.status = status
            self.status_dc = dc
            self.status_save = stype
        elif status and not damage and not save:
            self.status = status
            self.status = status
            self.status_dc = dc
            self.status_save = stype

    def revive(self):
        # resurects dead PCs
        pgrave = []
        resurect = 1

        for k,v in HB.dead.items():
            if resurect:
                v.hp = 1
                HB.party[k] = v
                pgrave.append(k)
                resurect = 0

        for p in pgrave:
            del HB.dead[p]

    def need_healing(self):
        # determine who needs healing
        return [x for x in HB.party.keys() if HB.party[x].hp < HB.party[x].base_hp]
    
    def get_spell_slots(self):
        return [x for x,y in enumerate(self.spell_slots) if y]
    
    def most_dead(self, patients):
        # returns the most injured PC for healng
        worst = patients[0]
        for p in patients:
            if HB.party[p].hp < HB.party[worst].hp:
                worst = p
        return worst
    
    def cast_heal(self, target, heal):
        # handles the mechanics of healing other PCs
        if HB.party[target].hp + heal + self.spell_atk > HB.party[target].base_hp:
            HB.party[target].hp = HB.party[target].base_hp
        else:
            HB.party[target].hp += heal + self.spell_atk

    def take_action(self):
        # chooses the cleric's action for the turn and then executes the action

        # checks to see who needs healing and if the cleric has available spell slots
        patients = self.need_healing()
        slots = self.get_spell_slots()

        if len(self.spell_slots) > 4 and self.spell_slots[4] and HB.dead:
            t = self.get_target([m for m in HB.monsters.keys()])
            target = HB.monsters[t]
            self.make_attack(target, self.spell_atk, self.roll_dice(1,8))
            self.revive()
            self.spell_slots[4] -= 1

        # chooses spells to cast
        elif self.level >= 3:
            if slots and patients:
                sl = slots[-1]
                if len(patients) > 2 and sl > 2:
                    spell = HB.cleric_spells['heal_all'][sl]['heal']
                    for patient in patients:
                        self.cast_heal(patient, spell)
                    self.spell_slots[sl] -= 1   
                else:
                    spell = HB.cleric_spells['heal_one_action'][sl]['heal']
                    patient = self.most_dead(patients)
                    self.cast_heal(patient, spell)
                    self.spell_slots[sl] -= 1  
                    
                t = self.get_target([m for m in HB.monsters.keys()])
                target = HB.monsters[t]
                self.make_attack(target, self.atk, self.roll_dice(1,8), crit=20,
                                    extra=self.x_dmg)        

            # makes a basic attack
            else:
                attack = 1
                while HB.monsters and attack <= 2:
                    t = self.get_target([m for m in HB.monsters.keys()])
                    target = HB.monsters[t]
                    self.make_attack(target, self.atk, self.roll_dice(1,8), crit=20,
                                        extra=self.x_dmg)
                    attack += 1

        else:
            # does healing
            if slots and patients:
                sl = slots[-1]
                spell = HB.cleric_spells['heal_one_action'][sl]['heal']
                t = self.most_dead(patients)
                self.cast_heal(t, spell)
                self.spell_slots[sl] -= 1
            else:
                t = self.get_target([m for m in HB.monsters.keys()])
                target = HB.monsters[t]
                self.make_attack(target, self.atk, self.roll_dice(1,8))
                
class Rogue(PC, HB):
    """
    Builds a rogue character of the specified level
    """

    def assign_stats(self):
        # generates the PC stats based on the template
        self.stats = {
            'int': self.base_stats[4],
            'wis': self.base_stats[5],
            'con': self.base_stats[2],
            'cha': self.base_stats[3],
            'dex': self.base_stats[0],
            'str': self.base_stats[1]
        }
    
    def assign_bonus(self):
        # creates the stat bonuses for the PC
        self.bonus = {
            'int': self.get_bonus(self.stats['int']),
            'wis': self.get_bonus(self.stats['wis']),
            'cha': self.get_bonus(self.stats['cha']),
            'str': self.get_bonus(self.stats['str']),
            'dex': self.get_bonus(self.stats['dex']),
            'con': self.get_bonus(self.stats['con']),
        }
    
    def assign_saves(self):
        # generates the saving throw for the character
        self.saves = {
            'str': self.bonus['str'],
            'dex': self.bonus['dex'] + self.pro,
            'con': self.bonus['con'],
            'int': self.bonus['int'] + self.pro,
            'wis': self.bonus['wis'],
            'cha': self.bonus['cha']
        }

    def build(self):
        # builds the rogue character and creates all the stats and abilities
        self.adjust_stats()
        self.assign_stats()
        self.assign_bonus()
        self.assign_saves()
        self.name = 'rogue'
        self.status = 'normal'
        self.stats_save = None
        self.status_dc = 0
        self.actions = 1
        self.hp = 8 + self.bonus['con'] 
        self.hp += self.roll_dice(self.level,8) + self.level * self.bonus['con']
        self.base_hp = self.hp
        self.ac = 12 + self.bonus['dex']
        self.atk = self.pro + self.bonus['dex']
        self.crit = 20
        self.reroll = 0
        self.x_dmg = self.roll_dice(1,6) + self.atk
        self.dodge = False

        if self.level == 20:
            self.reroll = 1
            self.saves['wis'] += self.pro
            self.dodge = True
            self.x_dmg = self.roll_dice(10,6) + self.atk
        elif self.level >= 19:
            self.saves['wis'] += self.pro
            self.dodge = True  
            self.x_dmg = self.roll_dice(10,6) + self.atk  
        elif self.level >= 17:
            self.saves['wis'] += self.pro
            self.dodge = True  
            self.x_dmg = self.roll_dice(9,6) + self.atk         
        elif self.level >= 15:
            self.saves['wis'] += self.pro
            self.dodge = True
            self.x_dmg = self.roll_dice(8,6) + self.atk
        elif self.level >= 13:
            self.dodge = True
            self.x_dmg = self.roll_dice(7,6) + self.atk 
        elif self.level >= 11:
            self.dodge = True
            self.x_dmg = self.roll_dice(6,6) + self.atk
        elif self.level >= 9:
            self.dodge = True
            self.x_dmg = self.roll_dice(5,6) + self.atk
        elif self.level >= 7:
            self.dodge = True
            self.x_dmg = self.roll_dice(4,6) + self.atk
        elif self.level >= 5:
            self.dodge = True
            self.x_dmg = self.roll_dice(3,6) + self.atk
        elif self.level >= 3:
            self.x_dmg = self.roll_dice(2,6) + self.atk

    def make_save(self, dc, stype, damage=0, status=None):
        # handles the saving throw for the PC when affected by a status
        save = self.save_roll(dc, self.saves[stype])
        if self.level >= 7 and stype == 'dex':
            if damage and save and status:
                self.hp -= int(damage/2) + 1
            if damage and save and not status:
                self.hp -= int(damage/2) + 1
            elif damage and status and not save:
                self.hp -= damage
                self.status = status
                self.status_dc = dc
                self.status_save = stype
            elif status and not damage and not save:
                self.status = status
                self.status = status
                self.status_dc = dc
                self.status_save = stype
        else:
            if damage and save and status:
                self.hp -= int(damage/2) + 1
            if damage and save and not status:
                self.hp -= int(damage/2) + 1
            elif damage and status and not save:
                self.hp -= damage
                self.status = status
                self.status_dc = dc
                self.status_save = stype
            elif status and not damage and not save:
                self.status = status
                self.status = status
                self.status_dc = dc
                self.status_save = stype

    def take_action(self):
        # picks the action for the PC to take on this turn then executes their action
        if HB.round == 0 and self.level >= 17:
            attacks = 2
            while HB.monsters and attacks > 0:
                t = self.get_target([m for m in HB.monsters.keys()])
                target = HB.monsters[t]
                self.make_attack(target, self.atk, self.roll_dice(1,8), crit=self.crit, 
                                    extra=self.x_dmg)
                attacks -= 1
        else:
            t = self.get_target([m for m in HB.monsters.keys()])
            target = HB.monsters[t]
            self.make_attack(target, self.atk, self.roll_dice(1,8), crit=self.crit, 
                                extra=self.x_dmg)