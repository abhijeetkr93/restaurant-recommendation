import json
from calendar import monthrange
from random import randint, uniform, choice
from enum import Enum
from datetime import datetime


class Cuisines(Enum):
    SOUTH_INDIAN = "SouthIndian"
    NORTH_INDIAN = "NorthIndian"
    CHINESE = "Chinese"
    CONTINENTAL = "Continental"


class Restaurant:
    def __init__(
        self,
        restaurantId: int,
        cuisine: str,
        costBracket: int,
        rating: float,
        isRecommended: bool,
        onBoardedTime: str,
    ) -> None:
        self.restaurantId = restaurantId
        self.cuisine = cuisine
        self.costBracket = costBracket
        self.rating = rating
        self.isRecommended = isRecommended
        self.onBoardedTime = onBoardedTime


class Order:
    def __init__(self, orderId: int, userId: int, restaurant: Restaurant) -> None:
        self.orderId = orderId
        self.userId = userId
        self.restaurantId = restaurant.restaurantId
        self.cuisine = restaurant.cuisine
        self.costBracket = restaurant.costBracket


class MockData:
    def __init__(self) -> None:
        self.rest = {}
        self.orders = {}

    @staticmethod
    def get_random_date_range():
        year = randint(2022, 2023)
        month = randint(1, 2) if year > 2022 else randint(1, 12)
        day = randint(*monthrange(year, month))
        hour = randint(1, 23)
        minute = randint(1, 59)
        second = randint(1, 59)
        return datetime(year, month, day, hour, minute, second).isoformat()

    def mock_restaurants_in_json(self):
        """
        creates mock restaurants.json file by considering

        | 1. cuisine: Cuisine (SouthIndian, NorthIndian, Chinese, Continental).
        | 2. costBrackets: cheapest to costly (1,5).
        | 3. ratings: average user rating for the restaurant (1,5).
        | 4. isRecommended: restaurants which are officially tested by our app and recommended.
        | 5. onBoardedTime: restaurants onboarded time.
        """

        for index in range(1, 101):
            rating = round(uniform(1, 5), 2)
            restaurant = Restaurant(
                restaurantId=index,
                cuisine=choice([cuisine.value for cuisine in Cuisines]),
                costBracket=randint(1, 5),
                rating=rating,
                isRecommended=choice([True, False]) if rating > 4 else False,
                onBoardedTime=self.get_random_date_range(),
            )
            self.rest.update({index: restaurant.__dict__})
        with open("restaurants.json", "w") as f:
            json.dump(self.rest, f, indent=2)
        return self

    def mock_orders_in_json(self):
        """
        creates mock orders.json file by considering orderId, userId, restaurantId,
        cuisine, costBracket
        """

        with open("restaurants.json") as rest:
            restaurants = json.load(rest)
        for order in range(1, 50001):
            restaurant_instance = Restaurant(
                **restaurants.get(str(randint(1, 100)), {})
            )
            orderInstance = Order(
                orderId=order, userId=randint(1, 500), restaurant=restaurant_instance
            )
            self.orders.update({order: orderInstance.__dict__})
        with open("orders.json", "w") as f:
            json.dump(self.orders, f, indent=2)


mock = MockData()
mock.mock_restaurants_in_json().mock_orders_in_json()
