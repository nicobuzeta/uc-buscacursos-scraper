import re
from os import path, listdir
import json
import copy


class Spell:
    words_not_capitalize = ['and', 'of', 'from', 'or']

    base_json = {
        "Spell_Name": None,
        "Spell_ID": None,
        "Spell_Edition": None,
        "Spell_Source": None,
        "Spell_Source_Date": None,
        "Spell_Level": None,
        "Spell_School": None,
        "Is_Ritual": None,
        "Spell_Classes": None,
        "Spell_Casting_Time": None,
        "Spell_Range": [
            None
        ],
        "Spell_Duration": [
            None
        ],
        "Concentration": False,
        "Spell_Verbal_Component": False,
        "Spell_Somatic_Component": False,
        "Spell_Material_Component": False,
        "Spell_MC_Description": None,
        "Spell_Area": None,
        "Spell_Saving_Throw": None,
        "Spell_Saving_Throw_Success": None,
        "Spell_Damage": None,
        "Spell_Damage_Types": None,
        "Spell_Effects": None,
        "Spell_Description": [''],
        "Spell_OL": None,
        "Spell_UL": None,
        "Spell_Tables": None
    }

    def __init__(self, name, level_type, required_classes, casting_time, spell_range, components, duration):
        self.name = self.process_name(name)
        self.level, self.school, self.ritual = self.process_level_type(level_type)
        self.required_classes = self.process_required_classes(required_classes)
        self.casting_time = self.process_casting_time(casting_time)
        self.spell_range = self.process_spell_range(spell_range)
        self.components, self.m_description = self.process_components(components)
        self.duration, self.concentration = self.process_duration(duration)

    @property
    def spell_id(self):
        return self.name.replace(' ', '_').replace('/', '-')

    def process_name(self, name):
        new_name = []
        name = name.split(' ')
        separator = ' '
        if len(name) == 1:
            name = name[0].split('/')
            separator = '/'

        for word in name:
            if word.lower() not in self.words_not_capitalize:
                new_name.append(word.capitalize())
            else:
                new_name.append(word.lower())
        return separator.join(new_name)

    @staticmethod
    def process_level_type(level_type):
        level_type = level_type.split(' ')
        ritual = False
        if level_type[0][0].isnumeric():
            level = int(level_type[0][0])
            school = level_type[1].capitalize()
            if len(level_type) == 3:
                ritual = True
        else:
            level = 0
            school = level_type[0].capitalize()

        return level, school, ritual

    @staticmethod
    def process_required_classes(required_classes):
        dnd_classes = []
        required_classes = required_classes.split(':', 1)
        classes = required_classes[1].strip().split(',')
        for dnd_class in classes:
            dnd_classes.append(dnd_class.strip())
        return dnd_classes

    @staticmethod
    def process_casting_time(casting_time):
        casting_time = casting_time.split(':', 1)
        return casting_time[1].strip()

    @staticmethod
    def process_spell_range(spell_range):
        spell_range = spell_range.split(':', 1)
        return spell_range[1].strip()

    @staticmethod
    def process_components(components):
        components = components.split(':', 1)[1]
        separated_components = []
        m_description = None
        last = 0
        for i, letter in enumerate(components):
            if letter == '(' or letter == ',':
                component = components[last:i].strip()
                separated_components.append(component)
                last = i + 1
                if letter == '(':
                    m_description = components[i + 1:-1]
                    break
            if i == len(components) - 1:
                component = components[last:].strip()
                separated_components.append(component)

        return separated_components, m_description

    @staticmethod
    def process_duration(duration):
        duration = duration.split(':', 1)[1].strip()
        concentration = False
        if 'Concentration' in duration:
            concentration = True
        return duration, concentration

    def generate_sql(self):
        return f'INSERT INTO Spells_5e_PHB (Spell_Name, Spell_Level, Spell_School, Spell_Address) VALUES ' \
               f'("{self.name}", {self.level}, "{self.school}", "json_files/Spells/5e/PHB/{self.spell_id}.json");'

    def generate_json(self):
        spell_json = copy.deepcopy(self.base_json)

        spell_json['Spell_Name'] = self.name
        spell_json['Spell_ID'] = self.spell_id
        spell_json['Spell_Edition'] = EDITION
        spell_json['Spell_Source'] = [
            '',
            ''
        ]
        spell_json['Spell_Source_Date'] = SOURCE_DATE
        spell_json['Spell_Level'] = self.level
        spell_json['Spell_School'] = [self.school]
        spell_json['Is_Ritual'] = self.ritual
        spell_json['Spell_Classes'] = self.required_classes
        spell_json['Spell_Casting_Time'] = self.casting_time
        spell_json['Spell_Range'] = [self.spell_range]
        spell_json['Spell_Duration'] = [self.duration]
        spell_json['Concentration'] = self.concentration
        if 'V' in self.components:
            spell_json['Spell_Verbal_Component'] = True
        if 'S' in self.components:
            spell_json['Spell_Somatic_Component'] = True
        if 'M' in self.components:
            spell_json['Spell_Material_Component'] = True
        spell_json['Spell_MC_Description'] = self.m_description

        return spell_json


    def __str__(self):
        return ' - '.join(
            [self.spell_id, self.name, str(self.level), self.school, str(self.ritual), str(self.required_classes),
             self.casting_time, self.spell_range, str(self.components), str(self.m_description), self.duration,
             str(self.concentration)])


EDITION = '5e'
SOURCE_DATE = '8/19/2014'

files = '/home/nicobuzeta/Desktop/PHB'

spells = []

spells_classes = []

for spell in listdir(files):
    with open(path.join(files, spell)) as f:
        spells.append(list(filter(None, f.read().splitlines()))[:7])

for spell in spells:
    spell_class = Spell(*spell)
    spells_classes.append(spell_class)

# list(map(lambda x: print(x.generate_sql()), sorted(spells_classes, key=lambda x: x.spell_id)))

for spell in sorted(spells_classes, key=lambda x: x.spell_id):

    with open(path.join('jsons', spell.spell_id + '.json'), 'w') as f:
        dict_form = spell.generate_json()
        json.dump(dict_form, f, indent=2)


