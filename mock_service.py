import json
from datetime import datetime


class RestaurantsService:
    def __init__(self) -> None:
        self.restaurants = None
        self.new_restaurants = []

    def __call__(self):
        return self.get_all_restaurants()

    def get_all_restaurants(self) -> dict:
        """
        get all the restaurant from restaurants.json file in memory
        :return: dict of all restaurants
        """
        if not self.restaurants:
            with open("restaurants.json") as res:
                self.restaurants = json.load(res)
        return self.restaurants

    def filter_new_restaurants(self):
        """
        filters all restaurants that are onboarded in last 48 Hours
        :return: list of restaurants
        """

        current = datetime.now()
        for _, v in self.restaurants.items():
            onboard_datetime = datetime.fromisoformat(v["onBoardedTime"])
            diff = (current - onboard_datetime).total_seconds()
            if round(diff / 3600) < 48:
                self.new_restaurants.append(v)
        return self

    def get_top_four_by_ratings(self) -> list:
        """
        get top four restaurants from list of new restaurants
        :return: list of restaurants
        """

        return sorted(self.new_restaurants, key=lambda x: x["rating"], reverse=True)[
            0:3
        ]


class OrdersService:
    def __init__(self) -> None:
        self.orders = []
        self.get_all_orders()

    def __call__(self):
        return self.get_all_orders()

    def get_all_orders(self) -> dict:
        """
        get all the orders from orders.json file in memory
        :return: dict of all orders
        """
        if not self.orders:
            with open("orders.json") as orders:
                self.orders = json.load(orders)
        return self.orders


restaurant_service_instance = RestaurantsService()
RESTAURANTS = restaurant_service_instance()
NEW_TOP_RATING_RESTAURANTS = (
    restaurant_service_instance.filter_new_restaurants().get_top_four_by_ratings()
)
ALL_ORDERS = OrdersService()()
