from random import randint

class HandBook():
    """
    The Handbook class is used to create the template for all aspects of the D&D encounter
    system for both player characters and monsters providing all the base stats and methods
    for determining and executing actions.

    Note: the random module must be installed for this program to work.
    """

    # Holds the PC party and their opponents and tracks initiative order for the round
    monsters = {}
    party = {}
    initiative = []

    # Tracks the PCs and Monsters killed in combat
    dead = {}
    killed = {}

    # Tracks the round number and whose turn it is within the round
    round = 0
    turn = 0

    # A list where the wizard level is the index for the spellboox list which sets the
    # number of spells a wizard has of each level
    spell_book =    [[0],[3,1],[3,2],[3,2,2],[4,2,3,2],[4,2,3,3],
                    [4,2,3,3],[4,2,3,3,1],[4,2,3,3,2],[4,2,3,3,3,1],[5,2,3,3,3,2],
                    [5,2,3,3,3,2,1],[5,2,3,3,3,2,1],[5,2,3,3,3,2,1,1],[5,2,3,3,3,2,1,1],
                    [5,2,3,3,3,2,1,1,1],[5,2,3,3,3,2,1,1,1],[5,2,3,3,3,2,1,1,1,1],
                    [5,2,3,3,3,3,1,1,1,1],[5,2,3,3,3,3,2,1,1,1],[5,2,3,3,3,3,2,2,1,1]]

    # Divided into spells that target all enemies or just a single enemy with the optimal
    # spell for damage at each level. 
    wizard_spells ={
        'all': {
            2: {'name': 'Shatter', 'dmg': 14, 'save': 'con'},
            3: {'name': 'Fireball', 'dmg': 28, 'save': 'dex'},
            4: {'name': 'Fireball', 'dmg': 31, 'save': 'dex'},
            5: {'name': 'Cone of Cold', 'dmg': 36, 'save': 'con'},
            6: {'name': 'Cone of Cold', 'dmg': 40,'save': 'con'},
            7: {'name': 'Delayed Blast Fireball', 'dmg': 49, 'save': 'dex'},
            8: {'name': 'Delayed Blast Fireball', 'dmg': 63, 'save': 'dex'},
            9: {'name': 'Meteor Swarm', 'dmg': 140, 'save': 'dex'}
        },
        'one': {
            0: {'name': 'Fire Bolt', 'dmg': 6, 'type': 'attack'},
            1: {'name': 'Magic Missile', 'dmg': 12, 'type': 'attack'},
            2: {'name': 'Acid Arrow', 'dmg': 15, 'type': 'attack'},
            3: {'name': 'Acid Arrow', 'dmg': 20, 'type': 'attack'},
            4: {'name': 'Blight', 'dmg': 36, 'type': 'save', 'save': 'con'},
            5: {'name': 'Blight', 'dmg': 41, 'type': 'save', 'save': 'con'},
            6: {'name': 'Disintegrate', 'dmg': 75, 'type': 'save', 'save': 'dex'},
            7: {'name': 'Disintegrate', 'dmg': 85, 'type': 'save', 'save': 'dex'},
            8: {'name': 'Disintegrate', 'dmg': 96, 'type': 'save', 'save': 'dex'},
            9: {'name': 'Disintegrate', 'dmg': 107, 'type': 'save', 'save': 'dex'}
        }}
    
    # Same as the spellbook but for Cleric charachters
    divine = [[0],[3,2],[3,3],[3,4,2],[4,4,3],[4,4,3,2],[4,4,3,3],[4,4,3,3,1],[4,4,3,3,2],
            [4,4,3,3,3],[5,4,3,3,3,1],[5,4,3,3,3,1,1],[5,4,3,3,3,1,1],[5,4,3,3,3,1,1,1],
            [5,4,3,3,3,1,1,1],[5,4,3,3,3,1,1,1,1],[5,4,3,3,3,1,1,1,1],[5,4,3,3,3,1,1,1,1,1],
            [5,4,3,3,3,2,1,1,1,1],[5,4,3,3,3,2,2,1,1,1],[5,4,3,3,3,2,2,2,1,1]]

    # Same as Wizard spells, divided into healing and other cleric spells
    cleric_spells = {
        'heal_all': {
            3: {'name': 'Mass Healing Word', 'heal': 3, 'speed': 0},
            4: {'name': 'Mass Healing Word', 'heal': 5, 'speed': 0},
            5: {'name': 'Mass Cure Wounds', 'heal': 14, 'speed': 1},
            6: {'name': 'Mass Cure Wounds', 'heal': 18, 'speed': 1},
            7: {'name': 'Mass Cure Wounds', 'heal': 23, 'speed': 1},
            8: {'name': 'Mass Cure Wounds', 'heal': 27, 'speed': 1},
            9: {'name': 'Mass Heal', 'heal': 700, 'speed': 1},
        },
        'heal_one_bonus': {
            1: {'name': 'Healing Word', 'heal': 3},
            2: {'name': 'Healing Word', 'heal': 5},
            3: {'name': 'Healing Word', 'heal': 8},
            4: {'name': 'Healing Word', 'heal': 10},
            5: {'name': 'Healing Word', 'heal': 13},
            6: {'name': 'Healing Word', 'heal': 15},
            7: {'name': 'Healing Word', 'heal': 18},
            8: {'name': 'Healing Word', 'heal': 20},
            9: {'name': 'Healing Word', 'heal': 23},
        },
        'heal_one_action': {
            0: {'name': 'Virtue', 'heal': 3},
            1: {'name': 'Cure Wounds', 'heal': 5},
            2: {'name': 'Cure Wounds', 'heal': 9},
            3: {'name': 'Cure Wounds', 'heal': 14},
            4: {'name': 'Cure Wounds', 'heal': 18},
            5: {'name': 'Cure Wounds', 'heal': 23},
            6: {'name': 'Heal', 'heal': 70},
            7: {'name': 'Heal', 'heal': 80},
            8: {'name': 'Heal', 'heal': 90},
            9: {'name': 'Heal', 'heal': 100},
        },
        'other': {
            2: 'Spiritual Weapon: 1d8 + self.spell_atk + 1d8/level - Bonus',
            3: 'Revivify: Dead creature restored to 1hp - Action',
            5: 'Holy Weapon: +2d8 weapon damage - Bonus'
        }
    }

    def roll_dice(self, n, s):
        """
        Rolls the dice.

        Attributes:
            n: int, number of sides on the dice
            s: int, side on each dice

        Returns:
            int, total of all dice rolled
        """
        return sum([randint(1,s) for num in range(1,n+1)])

    def save_roll(self, dc, bonus):
        """
        Used for making save throws against things like poison and paralysis.

        Attributes:
            dc: int, the number the player/moster must roll against to make their save
            bonus: int, any bonuses the player/monster gets on their saving throw.

        Return:
            boolean, True if the save roll + bous is greater than the DC
        """
        save = self.roll_dice(1,20)
        if save == 20 or save + bonus >= dc:
            return True

    def get_bonus(self, stat):
        """
        Part of the building process for creating PCs and monsters from the template
        this function takes a stat and returns the bonus that the PC/monster will get
        when using abilities and saving throws related to that stat.

        Attribute:
            stat: int, the stat being checked.

        Return:
            int, the positive or negative modifier for the stat
        """
        if stat == 1: 
            return -5
        elif stat > 1 and stat < 4: 
            return -4
        elif stat > 3 and stat < 6: 
            return -3
        elif stat > 5 and stat < 8:
            return -2
        elif stat > 7 and stat < 10: 
            return -1
        elif stat > 9 and stat < 12: 
            return 0
        elif stat > 11 and stat < 14: 
            return 1
        elif stat > 13 and stat < 16: 
            return 2
        elif stat > 15 and stat < 18:
            return 3
        elif stat > 17 and stat < 20:
            return 4
        elif stat > 19:
            return 5

    def is_dead(self):
        """
        Goes through all PCs and Monsters after every action and round to check if there
        are any entities with HP at or lower than 0, then moves them into the correct
        grave list and takes them out of the innitiative order.
        """
        mgrave = []
        pgrave = []

        if HandBook.monsters:
            for k,v in HandBook.monsters.items():
                if v.hp <= 0:
                    HandBook.killed[k] = v
                    mgrave.append(k)
        
        if HandBook.party:
            for k,v in HandBook.party.items():
                if v.hp <= 0:
                    HandBook.dead[k] = v
                    pgrave.append(k)
        
        if mgrave:
            for m in mgrave:
                del HandBook.monsters[m]
        
        if pgrave:
            for p in pgrave:
                del HandBook.party[p]

    def get_target(self, enemies):
        """
        Uses randome number to pick a target for the action (spell or attack) to be used
        by the PC or monster when using single target actions.
        """
        if len(enemies) == 1:
            return enemies[0]
        else:
            return enemies[randint(0,len(enemies) - 1)]

    def make_attack(self, enemy, bonus, damage, crit=20, extra=0):
        """
        Takes a target, makes an attack roll vs the target's armor class, and then applies
        damage to the target's HP on a successfull attack. At the end of the attack, checks
        if any targets are now dead.

        Attributes:
            enemy: dict, the target of the attack
            bonus: int, the modifier to the entity's rolls for the action
            damage: int, the ammount of damage dealt to the enemy on a successful attack
            crit: int, the number that if rolled deals critical damage
        """
        attack = self.roll_dice(1,20)
        if attack >= crit:
            if not enemy.dodge:
                enemy.hp -= damage + bonus + extra
            else:
                enemy.hp -= int((damage + bonus + extra)/2) + 1
        elif attack == 1:
            enemy.hp -= 0
        elif attack + bonus >= enemy.ac:
            if not enemy.dodge:
                enemy.hp -= damage + bonus + extra
            else:
                enemy.hp -= int((damage + bonus + extra)/2) + 1

        self.is_dead()
