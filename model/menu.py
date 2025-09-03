from typing import List, Dict, Any

class MenuItem:
    def __init__(self, name: str, tags: List[str], price: float, description: str):
        self.name = name
        self.tags = tags
        self.price = price
        self.description = description

    def __repr__(self):
        return f"MenuItem(name={self.name}, tags={self.tags}, price={self.price}, description={self.description})"

class MenuSection:
    def __init__(self, name: str, items: List[MenuItem]):
        self.name = name
        self.items = items

    def __repr__(self):
        return f"MenuSection(name={self.name}, items={self.items})"

class Restaurant:
    def __init__(self, restaurant_id: str, name: str, location: str, opening_hours: str, menu: List[MenuSection]):
        self.restaurant_id = restaurant_id
        self.name = name
        self.location = location
        self.opening_hours = opening_hours
        self.menu = menu

    def __repr__(self):
        return f"Restaurant({self.restaurant_id}, {self.name}, {self.location}, {self.opening_hours}, {self.menu})"