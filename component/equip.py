from component.base import MenuComponent, component_method


class Wearable(MenuComponent):
    @component_method
    def get_menu(self, ent):
        return {
            'wear': ('Wear {Backpack}', self.wear)
        }

    @component_method
    def wear(self, ent):
        print ent, 'tried to wear'
