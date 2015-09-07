from functools import partial
import component
from component.base import MenuComponent
from entity import Entity


class Equippable(MenuComponent):
    data = {
        'slot': None,
        'slots': None,
        'equipped': False
    }

    def get_slots(self):
        return self.data.slots or [self.data.slot]

    def get_menu(self, ent):
        # if self.data.equipped and
        if (
                            'Equipped' not in self.entity and
                            'EquipmentUser' in ent and
                    ent.EquipmentUser.can_equip(self.entity)
        ):
            return {
                'wear': ('Wear {}'.format(self.entity.name), partial(ent.EquipmentUser.equip, self))
            }

        return {}

    def wear(self, ent):
        print(ent, 'tried to wear')
        if 'Position' in ent:
            ent.Position.destroy()

        ent.add_component(component.c.Equipped, )


class Equipped(MenuComponent):
    def get_menu(self, ent):
        return {
            'remove': ('Remove {}'.format(ent.name), partial(ent.EquipmentUser.remove, self))
        }


class EquipmentUser(component.BaseComponent):
    data = {
        'slots': {}
    }

    def initialize(self):
        self.data.slots = {k: Entity.get(v) for k, v in self.data.slots.items()}

    def can_equip(self, equippable):
        return True

    def equip(self, eq):
        if not self.can_equip(eq):
            return

        if component.c.Position in eq.entity:
            eq.entity.Position.destroy()

        for slot in eq.get_slots():
            self.data.slots[slot] = eq.entity

        self.entity.add_component(component.c.Equipped)

    def remove(self, eq):
        return
