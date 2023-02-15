import json
from calendar import monthrange
from random import randint, uniform, choice
from enum import Enum
from datetime import datetime


class PopulateData:
    def __init__(self) -> None:
        self.rest = {}
        self.orders = {}
    
    def get_random_date_range(self):
        year = randint(2022, 2023)
        month = randint(1,2) if year>2022 else randint(1,12)
        day = randint(*monthrange(year, month))
        hour = randint(1, 23)
        minute = randint(1, 59)
        second = randint(1, 59)
        return datetime(year, month, day, hour, minute, second).isoformat()

    def populate_restaurants(self):
        for id in range(1, 101):
            rating = round(uniform(1,5), 2)
            self.rest.update({
                id: {
                "restaurantId": id,
                "cuisine": randint(1,3),
                "costBracket": randint(1,5),
                "rating": rating,
                "isRecommended": choice([True, False]) if rating > 4 else False,
                "onBoardedTime": self.get_random_date_range(),
            }
            })
        with open('restaurants.json', 'w') as f:
            json.dump(self.rest, f, indent=2)
        return self

    def populate_orders(self):
        restaurants = {}
        with open('restaurants.json') as rest:
            restaurants = json.load(rest)
        for order in range(1, 50001):
            restaurantId = randint(1,100)
            self.orders.update({
                order: {
                    'orderId': order,
                    'userId': randint(1,500),
                    'restaurantId': restaurantId,
                    'cuisine': restaurants.get(str(restaurantId), {}).get('cuisine'),
                    'costBracket': restaurants.get(str(restaurantId), {}).get('costBracket')
                }
            })
        with open('orders.json', 'w') as f:
            json.dump(self.orders, f, indent=2)


p = PopulateData()
p.populate_restaurants().populate_orders()
