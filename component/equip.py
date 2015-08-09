from functools import partial
import component
from component.base import MenuComponent, component_method


class Equippable(MenuComponent):
    data = {
        'slot': None,
        'slots': None,
        'equipped': False
    }

    @component_method
    def get_slots(self):
        return self.data.slots or [self.data.slot]

    @component_method
    def get_menu(self, ent):
        # if self.data.equipped and
        if (
            component.c.Equipped not in self.entity and
            component.c.EquipmentUser in ent and
            ent.EquipmentUser.can_equip(self.entity)
        ):
            return {
                'wear': ('Wear {}'.format(self.entity.name), partial(ent.EquipmentUser.equip, self))
            }

        return {}

    @component_method
    def wear(self, ent):
        print(ent, 'tried to wear')
        if component.c.Position in ent:
            ent.Position.destroy()

        ent.add_component(component.c.Equipped, )

class Equipped(MenuComponent):
    @component_method
    def get_menu(self, ent):
        pass

class EquipmentUser(component.BaseComponent):
    data = {
        'slots': {}
    }

    @component_method
    def initialize(self):
        if not self.data.slots:  # copy
            self.data.slots = {}

    @component_method
    def can_equip(self, equippable):
        return True

    @component_method
    def equip(self, eq, caller):
        if not self.can_equip(eq):
            return

        if component.c.Position in eq.entity:
            eq.entity.Position.destroy()

        for slot in eq.get_slots():
            self.data.slots[slot] = eq.entity

        self.entity.add_component(component.c.Equipped)
