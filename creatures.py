import json
from random import randint
from handbook import HandBook as HB

class CreatureFeature(HB):
    """
    This class is used to build the monsters for the encounter using information from the
    monbs.json file. Each type of monster is passed to this class, which is a subclass of
    the Handbook, and generates the appropriate number of monsters of that type. This class
    is only called from encounter.py
    """
    def __init__(self, mob, number):
        self.mob = mob
        self.number = number

    def assign_stats(self):
        # generates the stats for the monster from the information in the JSON file
        self.stats = self.mob['stats']
    
    def assign_name(self):
        # gives the created monster a unique identifier
        self.name = self.name + str(self.number)
    
    def assign_bonus(self):
        # gives the monster bonuses for its stats
        self.bonus = {
            'int': self.get_bonus(self.stats['int']),
            'wis': self.get_bonus(self.stats['wis']),
            'cha': self.get_bonus(self.stats['cha']),
            'str': self.get_bonus(self.stats['str']),
            'dex': self.get_bonus(self.stats['dex']),
            'con': self.get_bonus(self.stats['con']),
        }
    
    def assign_saves(self):
        # generates the saveing throws for the monster
        self.saves = {
            'str': self.bonus['str'] + self.mob['saves']['str'],
            'dex': self.bonus['dex'] + self.mob['saves']['dex'],
            'con': self.bonus['con'] + self.mob['saves']['con'],
            'int': self.bonus['int'] + self.mob['saves']['int'],
            'wis': self.bonus['wis'] + self.mob['saves']['wis'],
            'cha': self.bonus['cha'] + self.mob['saves']['cha']
        }

    def build(self):
        # handles the building of the monster and all the stats
        self.assign_stats()
        self.assign_bonus()
        self.assign_saves()
        self.ac = self.mob['ac']
        self.hp = self.mob['hp']
        self.base_hp = self.mob['hp']
        self.status = self.mob['status']['current']
        self.status_dc = self.mob['status']['dc']
        self.status_save = self.mob['status']['save']
        self.atk = self.mob['atk']
        self.spell_dc = self.mob['spell_dc']
        self.spell_atk = self.mob['spell_atk']
        self.actions = self.mob['actions']['number']
        self.attacks = self.mob['actions']['attack'] # dict
        self.special = self.mob['actions']['special']

        if self.mob['dodge'] == 'True':
            self.dodge = True
        else:
            self.dodge = False

    def make_save(self, dc, stype, damage=0, status=False):
        # used to roll saving throws
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

    def take_action(self):
        # used to choose and then take the monster's action
        if (self.special['name'] and HB.round % self.special['cooldown'] == 0
                and self.special['targets'] != 'self'):
            if self.special['targets'] == 'all':
                for p in HB.party.values():
                    p.make_save(self.special['dc'], self.special['save'], 
                                damage=self.special['dmg'], status=self.special['effect'])
            else:
                t = self.get_target([p for p in HB.party.keys()])
                target = HB.party[t]
                target.make_save(self.special['dc'], self.special['save'], 
                                damage=self.special['dmg'], status=self.special['effect'])                       
            self.is_dead()
        elif (self.special['name'] and self.special['targets'] == 'self' and 
                self.hp <= int(self.base_hp/2)):
                if self.hp + self.special['dmg'] > self.base_hp:
                    self.hp = self.base_hp
                else:
                    self.hp += self.special['dmg']
        else:
            acts = 1
            while acts < self.actions + 1 and HB.party:
                a = self.attacks[str(acts)]
                t = self.get_target([p for p in HB.party.keys()])
                target = HB.party[t]
                self.make_attack(target, self.atk, a)
                acts += 1

    