import json
from datetime import datetime
from enum import Enum


class Cuisine(Enum):
    SOUTH_INDIAN = 1
    NORTH_INDIAN = 2
    CHINESE = 3

    def __repr__(self):
        return f"Cuisine.{self.name}"


class Restaurants:
    def __init__(self) -> None:
        self.restaurants = None
        self.new_restaurants = []

    def __call__(self):
        return self.get_all_restaurants()

    def get_all_restaurants(self):
        if not self.restaurants:
            with open("restaurants.json") as res:
                self.restaurants = json.load(res)
        return self.restaurants

    def filter_new_restaurants(self):
        current = datetime.now()
        for _, v in self.restaurants.items():
            onboard_datetime = datetime.fromisoformat(v["onBoardedTime"])
            diff = (current - onboard_datetime).total_seconds()
            if round(diff / 3600) < 48:
                self.new_restaurants.append(v)
        return self

    def get_top_four_by_ratings(self):
        return sorted(
            self.new_restaurants, key=lambda x: x["rating"], reverse=True
        )[0:3]


class Orders:
    def __init__(self) -> None:
        self.orders = []
        self.get_all_orders()

    def __call__(self):
        return self.get_all_orders()

    def get_all_orders(self):
        if not self.orders:
            with open("orders.json") as orders:
                self.orders = json.load(orders)
        return self.orders


all_restaurants = Restaurants()
RESTAURANTS = all_restaurants()
NEW_TOP_RATING_RESTAURANTS = (
    all_restaurants.filter_new_restaurants().get_top_four_by_ratings()
)
ALL_ORDERS = Orders()()


class UserCuisines:
    def __init__(self, user_orders) -> None:
        self.user_orders = user_orders
        self.primary_cuisine = None
        self.secondary_cuisine = None

    def calculate_user_cuisines(self):
        if self.user_orders:
            cuisine_count = {}
            for v in self.user_orders:
                if v["cuisine"] in cuisine_count.keys():
                    cuisine_count[v["cuisine"]] += 1
                else:
                    cuisine_count.update({v["cuisine"]: 1})
            cuisines = sorted(cuisine_count)
            self.primary_cuisine = cuisines[0:1]
            self.secondary_cuisine = cuisines[1:]

    def primary_cuisines(self):
        if not self.primary_cuisine:
            self.calculate_user_cuisines()
        return self.primary_cuisine

    def secondary_cuisines(self):
        if not self.secondary_cuisine or not self.primary_cuisine:
            self.calculate_user_cuisines()
        return self.secondary_cuisine


class UserCostBracket:
    def __init__(self, user_orders) -> None:
        self.user_orders = user_orders
        self.primary_cost_bracket = None
        self.secondary_cost_bracket = None

    def calculate_user_cost_brackets(self):
        if self.user_orders:
            bracket_count = {}
            for v in self.user_orders:
                if v["costBracket"] in bracket_count.keys():
                    bracket_count[v["costBracket"]] += 1
                else:
                    bracket_count.update({v["costBracket"]: 1})
            cost_brackets = sorted(bracket_count)
            self.primary_cost_bracket = cost_brackets[0:1]
            self.secondary_cost_bracket = cost_brackets[1:3]

    def primary_cost_brackets(self):
        if not self.primary_cost_bracket:
            self.calculate_user_cost_brackets()
        return self.primary_cost_bracket

    def secondary_cost_brackets(self):
        if not self.secondary_cost_bracket or not self.primary_cost_bracket:
            self.calculate_user_cost_brackets()
        return self.secondary_cost_bracket


class UserRestaurantOrders:
    def __init__(self, user_id) -> None:
        self.user_id = user_id

    def get_user_orders(self):
        user_orders = []
        for _, val in ALL_ORDERS.items():
            if val["userId"] == self.user_id:
                user_orders.append(val)
        return user_orders


class UserRestaurantRecommendation:
    def __init__(self, user_id) -> None:
        self.user_orders = UserRestaurantOrders(user_id).get_user_orders()
        self.user_cuisines = UserCuisines(self.user_orders)
        self.user_cost_brackets = UserCostBracket(self.user_orders)
        self.recommendations = []

    def add_restaurants_logic_1(self):
        """ """

        prim_cuisines = self.user_cuisines.primary_cuisines()
        secondary_cuisines = self.user_cuisines.secondary_cuisines()
        primary_cost_brackets = self.user_cost_brackets.primary_cost_brackets()
        secondary_cost_brackets = self.user_cost_brackets.secondary_cost_brackets()

        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in prim_cuisines),
                    (v["costBracket"] in primary_cost_brackets),
                    (v["isRecommended"]),
                    (restaurant_id not in self.recommendations),
                ]
            ):
                self.recommendations.append(restaurant_id)

        if not self.recommendations:
            for restaurant_id, v in RESTAURANTS.items():
                if all(
                    [
                        (v["cuisine"] in prim_cuisines),
                        (v["costBracket"] in secondary_cost_brackets),
                        (v["isRecommended"]),
                        (restaurant_id not in self.recommendations),
                    ]
                ):
                    self.recommendations.append(restaurant_id)

                if all(
                    [
                        (v["cuisine"] in secondary_cuisines),
                        (v["costBracket"] in primary_cost_brackets),
                        (v["isRecommended"]),
                        (restaurant_id not in self.recommendations),
                    ]
                ):
                    self.recommendations.append(restaurant_id)
        return self

    def add_restaurants_logic_2(self):
        """ """

        prim_cuisines = self.user_cuisines.primary_cuisines()
        secondary_cuisines = self.user_cuisines.secondary_cuisines()
        primary_cost_brackets = self.user_cost_brackets.primary_cost_brackets()
        secondary_cost_brackets = self.user_cost_brackets.secondary_cost_brackets()
        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in prim_cuisines),
                    (v["costBracket"] in primary_cost_brackets),
                    (v["rating"] >= 4),
                    (restaurant_id not in self.recommendations),
                ]
            ):
                self.recommendations.append(restaurant_id)

        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in prim_cuisines),
                    (v["costBracket"] in secondary_cost_brackets),
                    (v["rating"] >= 4.5),
                    (restaurant_id not in self.recommendations),
                ]
            ):
                self.recommendations.append(restaurant_id)

        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in secondary_cuisines),
                    (v["costBracket"] in primary_cost_brackets),
                    (v["rating"] >= 4.5),
                    (restaurant_id not in self.recommendations),
                ]
            ):
                self.recommendations.append(restaurant_id)
        
        for restaurant in NEW_TOP_RATING_RESTAURANTS:
            if (restaurant['restaurantId'] not in self.recommendations):
                self.recommendations.append(restaurant['restaurantId'])
        
        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in prim_cuisines),
                    (v["costBracket"] in primary_cost_brackets),
                    (v["rating"] < 4.5),
                    (restaurant_id not in self.recommendations),
                ]
            ):
                self.recommendations.append(restaurant_id)
        
        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in prim_cuisines),
                    (v["costBracket"] in secondary_cost_brackets),
                    (v["rating"] < 4.5),
                    (restaurant_id not in self.recommendations),
                ]
            ):
                self.recommendations.append(restaurant_id)
        
        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in secondary_cuisines),
                    (v["costBracket"] in primary_cost_brackets),
                    (v["rating"] < 4.5),
                    (restaurant_id not in self.recommendations),
                ]
            ):
                self.recommendations.append(restaurant_id)
        
        for restaurant_id, v in RESTAURANTS.items():
            if restaurant_id not in self.recommendations:
                self.recommendations.append(restaurant_id)
        


def get_user_rest_recommendations(user_id):
    user_recommendations = UserRestaurantRecommendation(user_id)
    user_recommendations.add_restaurants_logic_1().add_restaurants_logic_2()
    return user_recommendations.recommendations


print(get_user_rest_recommendations(1))