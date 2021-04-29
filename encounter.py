import json
from random import randint
from handbook import HandBook as HB
import party, creatures

class Encounter(HB):
    """
    The encounter child class creates an instance of an encounter of a player charachter
    (PC) party of a given level and one or more creatures using the Dungeons & Dragons
    5th Eddition basic rules.

    Note: the given names used for character classes are taken from Angry Birds Epic
        based on the classes of the Angry Birds characters

    Attributes:
        protagonists: a list of the character classes to be used in the player party; at
            this time only the four "basic" classes of cleric, fighter, rogue, and wizard
            are available for the PC party
        level: an integer of the party level for the encounter
        antagonists: a dictionary of the creatures that the party will be facing using
            the format {creature1: number[, creature2: number...]}
    """
    
    def __init__(self, protagonists, level, antagonists):
        """Initiates the encounter with protagonists, level, and antagonists"""
        self.antagonists = antagonists
        self.level = level
        self.protagonists = protagonists

    def make_wizard(self):
        """
        Uses the template from the party.py module to build a wizard charachter of the
        party level, including all stats, spells, and available actions.

        Returns:
            chuck: an instance of the Wizard class
        """
        chuck = party.Wizard(self.level)
        chuck.build()
        return chuck

    def make_fighter(self):
        """
        Uses the template from the party.py module to build a fighter charachter of the
        party level, including all stats, abilities, and available actions.

        Returns:
            red: an instance of the Fighter class
        """
        red = party.Fighter(self.level)
        red.build()
        return red

    def make_cleric(self):
        """
        Uses the template from the party.py module to build a Cleric charachter of the
        party level, including all stats, spells, healing, and available actions.

        Returns:
            matilda: an instance of the Cleric class
        """
        matilda = party.Cleric(self.level)
        matilda.build()
        return matilda

    def make_rogue(self):
        """
        Uses the template from the party.py module to build a rogue charachter of the
        party level, including all stats, abilities, and available actions.

        Returns:
            blues: an instance of the Rogue class
        """
        blues = party.Rogue(self.level)
        blues.build()
        return blues

    def build_party(self):
        """
        Initializes the PC party and launches the build functions from the Handbook
        """
        self.new_party = {}
        for protagonist in self.protagonists:
            if protagonist.lower() == 'wizard':
                self.new_party['wizard'] = self.make_wizard()
            elif protagonist.lower() == 'fighter':
                self.new_party['fighter'] = self.make_fighter()
            elif protagonist.lower() == 'cleric':
                self.new_party['cleric'] = self.make_cleric()
            elif protagonist.lower() == 'rogue':
                self.new_party['rogue'] = self.make_rogue()

    def load_creatures(self):
        """
        Opens the JSON file of the monsters and loads it into memory.
        """
        filepath = 'mobs.json'
        with open(filepath) as monster_manual:
            self.creature_dict = json.load(monster_manual)

    def build_monsters(self):
        """
        Initiates the creation of the monster list.
        """
        self.new_monsters = {}
        for a, n in self.antagonists.items():
            for i in range(0, n):
                nom = a + " (" + str(i) + ")"
                critter = creatures.CreatureFeature(self.creature_dict[a], i)
                critter.build()
                self.new_monsters[nom] = critter

    def build_initiative(self):
        """
        Generates the initiative order for the round from PC party and monsters
        """
        base_list = []
        final_list = []
        for p in HB.party.keys():
            base_list.append(p)
        for m in HB.monsters.keys():
            base_list.append(m)
        while base_list:
            final_list.append(
                base_list.pop(
                    randint(0,len(base_list) - 1)
                    ))
        return final_list

    def build_encounter(self):
        """
        Handles the work of loading in all the characters, monsters, and other information
        needed to run the encounter.
        """
        self.load_creatures()
        self.build_party()
        self.build_monsters()
        HB.round = 0
        HB.turn = 0
        HB.dead = {}
        HB.initiative = self.build_initiative()
        HB.injured = {}
        HB.party = self.new_party
        HB.monsters = self.new_monsters

    def combat(self):
        """
        Handles the bulk of the work of of running the encounter. Loads the monsters from
        the JSON file, builds the PC party an monsters, then runs each round of combat
        through the initiative order until all the PCs or all the monsters are killed.
        """
        self.build_encounter()

        # checks to make sure there are living PCs and Monsters before continuing
        while HB.party and HB.monsters:
            current = HB.initiative[HB.turn]

            if current in HB.monsters.keys():
                # starts the turn for a Monster
                active = HB.monsters[current]
                # checks to see if the monster can take an action
                if active.status != 'charmed' or active.status != 'stunned':
                    HB.monsters[current].take_action()
                elif active.status == 'dead':
                    active.hp = 0
                    self.is_dead
                # makes the saving rolls for ongoing conditions
                elif active.status != 'normal':
                    stype = active.status_save
                    newsave = self.save_roll(active.status_dc, active['saves'][stype])
                    if newsave:
                        active.status = 'normal'
                        active.status_dc = 0
                        active.status_save = None
                        HB.monsters[current].take_action()
                    else:
                        # makes the attack
                        targets = [m for m in HB.monsters.keys()]
                        if active.status == 'charmed' and len(targets) > 1:
                            t = active.name
                            while t == active.name:
                                t = active.get_target(targets)
                            target = HB.monsters[t]
                            active.make_attack(target, active.atk, active.attacks[1])

            elif current in HB.party.keys():
                # starts the turn of a PC
                active = HB.party[current]
                # checks to see if the PC can take an action
                if active.status != 'charmed' or active.status != 'stunned':
                    HB.party[current].take_action()
                # makes saving throws
                elif active.status != 'normal':
                    stype = active.status_save
                    newsave = self.save_roll(active.status_dc, active['saves'][stype])
                    if newsave:
                        active.status = 'normal'
                        active.status_dc = 0
                        active.status_save = None
                        HB.party[current].take_action()
                    else:
                        # takes the action
                        targets = [p for p in HB.party.keys()]
                        if active.status == 'charmed' and len(targets) > 1:
                            t = active.name
                            while t == active.name:
                                t = active.get_target(targets)
                            target = HB.party[t]
                            active.make_attack(target, active.atk, 5)
            
            # checks for any newly deceased PCs or monsters
            self.is_dead()

            # manages the round - finished the current turn, moves on to the next entity
            # in the innitiiative order until the end of the round, the starts the next
            if HB.turn == len(HB.initiative) - 1:
                HB.turn = 0
                HB.round += 1
            else:
                HB.turn += 1
        
        # handles victory conditions
        if HB.party and not HB.monsters:
            vic = HB.party
            return {x: (vic[x].hp, vic[x].base_hp) for x in vic.keys() if vic[x].hp > 0}

if __name__ == "__main__":
    # Sample version of the encounter using a 4th level party to fight wargs and goblins
    # Note: at 10k iterations the encounter can take a couple of minutes

    with open('creature_list.json') as c_list:
        mob_list = json.load(c_list)

    characters = ['cleric', 'fighter', 'rogue', 'wizard']

    results = []

    lvl = 4
    mob = {'Worg': 3, 'Goblin': 7}
    iterator = 1000
    for i in range(0,iterator):
        fight = Encounter(characters, lvl, mob)
        fight.build_encounter()
        win = fight.combat()
        if win:
            results.append(win)
    
    spacer='--------------------------------------------------------'
    opposition = []
    for k,v in mob.items():
        opposition.append(f'{v} {k}')
    opps = ' & '.join(opposition)
    outs = f'''
    Level {lvl} Party vs {opps}  ({iterator/1000}k iterations)
    {spacer}
    Overall Win Percentage: {(len(results)/iterator)*100:6.2f}%

    100% Survival Rate: {(len([x for x in results if len(x)==4])/iterator)*100:6.2f}%
    75% Survival Rate: {(len([x for x in results if len(x)==3])/iterator)*100:6.2f}%
    50% Survival Rate: {(len([x for x in results if len(x)==2])/iterator)*100:6.2f}%
    25% Survival Rate: {(len([x for x in results if len(x)==1])/iterator)*100:6.2f}%

    Cleric Survival Rate: {(len([x for x in results if 'cleric' in x.keys()])/iterator)*100:6.2f}%
    Fighter Survival Rate: {(len([x for x in results if 'fighter' in x.keys()])/iterator)*100:6.2f}%
    Rogue Survival Rate: {(len([x for x in results if 'rogue' in x.keys()])/iterator)*100:6.2f}%
    Wizard Survival Rate: {(len([x for x in results if 'wizard' in x.keys()])/iterator)*100:6.2f}%
    '''

    print(outs)
