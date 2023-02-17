from functools import cached_property
from mock_service import ALL_ORDERS, RESTAURANTS, NEW_TOP_RATING_RESTAURANTS


class CostTracking:
    def __init__(self, cost_type: str, orders_count: int) -> None:
        """
        :param cost_type: type of cost bracket cheapest to costly (1,5)
        :param orders_count: count of orders
        """

        self.type = cost_type
        self.no_of_orders = orders_count


class CuisineTracking:
    def __init__(self, cuisine_type: str, orders_count: int) -> None:
        """
        :param cuisine_type: type of Cuisine (SouthIndian, NorthIndian, Chinese, Continental)
        :param orders_count: count of orders
        """

        self.type = cuisine_type
        self.no_of_orders = orders_count


class User:
    def __init__(self, cost_tracking: list = [], cuisine_tracking: list = []) -> None:
        """
        :param cost_tracking: list of user's costs tracking
        :param cuisine_tracking: list of user's cuisines tracking
        """

        self.costTracking = cost_tracking
        self.cuisineTracking = cuisine_tracking

    @cached_property
    def primary_cuisines(self) -> list:
        """
        user's primary cuisine based on no_of_orders
        """
        return self.get_primary_type(self.cuisineTracking)

    @property
    def secondary_cuisines(self) -> list:
        """
        user's secondary cuisines based on no_of_orders
        """

        return [
            cuisine.type
            for cuisine in self.cuisineTracking
            if cuisine.type not in self.primary_cuisines
        ]

    @cached_property
    def primary_cost_brackets(self) -> list:
        """
        user's primary cost brackets based on no_of_orders
        """

        return self.get_primary_type(self.costTracking)

    @property
    def secondary_cost_brackets(self) -> list:
        """
        user's secondary cost brackets based on no_of_orders
        """

        return [
            cost_bracket.type
            for cost_bracket in self.costTracking
            if cost_bracket.type not in self.primary_cost_brackets
        ]

    @staticmethod
    def get_primary_type(records):
        """
        return primary type based on count of orders

        :param records: list of cuisines or cost bracket
        :return: primary type
        """

        primary = None
        index = 0
        max_no_of_orders = 0
        while index < len(records):
            if records[index].no_of_orders > max_no_of_orders:
                primary = records[index]
                max_no_of_orders = records[index].no_of_orders
            index += 1
        return [primary.type]


class UsersOrderService:
    def __init__(self, user_id) -> None:
        self.user_id = user_id
        self.user_orders = []
        self.cuisine_tracking = []
        self.cost_tracking = []

    def populate_user_orders(self):
        """
        populates user's orders from all orders
        """

        for val in ALL_ORDERS.values():
            if val["userId"] == self.user_id:
                self.user_orders.append(val)
        return self

    def populate_user_cuisines(self):
        """
        populates user's cuisines tracking from user's orders
        """

        if self.user_orders:
            cuisines = {}
            for v in self.user_orders:
                if v["cuisine"] in cuisines.keys():
                    cuisines[v["cuisine"]] += 1
                else:
                    cuisines.update({v["cuisine"]: 1})
            self.cuisine_tracking = [
                CuisineTracking(cuisine_type=cuisine_type, orders_count=orders_count)
                for cuisine_type, orders_count in cuisines.items()
            ]
        return self

    def populate_user_cost_bracket(self):
        """
        populates user's cost tracking from user's orders
        """

        if self.user_orders:
            cost_bracket = {}
            for v in self.user_orders:
                if v["costBracket"] in cost_bracket.keys():
                    cost_bracket[v["costBracket"]] += 1
                else:
                    cost_bracket.update({v["costBracket"]: 1})
            self.cost_tracking = [
                CostTracking(cost_type=cost_type, orders_count=orders_count)
                for cost_type, orders_count in cost_bracket.items()
            ]
        return self

    def get_user_details(self):
        self.populate_user_orders().populate_user_cuisines().populate_user_cost_bracket()
        return User(
            cost_tracking=self.cost_tracking, cuisine_tracking=self.cuisine_tracking
        )


class UserRestaurantRecommendation:
    LOGIC_TYPES = [
        "get_featured_restaurants",
        "get_high_ratings_restaurants",
        "get_new_created_restaurants",
        "get_low_rating_restaurants",
        "get_all_restaurants",
    ]

    def __init__(self, user_id) -> None:
        self.user = UsersOrderService(user_id=user_id).get_user_details()

    def get_restaurants_recommendations(self) -> list:
        """
        Get final recommendation ordered list of restaurants using set of
        multiple logics

        :return: list of restaurants
        """

        recommendations_priorities = [
            getattr(UserRestaurantRecommendation, f"{logic}")(self)
            for logic in self.LOGIC_TYPES
        ]
        return self.get_ordered_unique_recommendation(recommendations_priorities)

    def get_featured_restaurants(self) -> list:
        """
        Get featured restaurants of primary cuisine and primary cost bracket.
        If none, then all featured restaurants of primary cuisine, secondary cost
        and secondary cuisine, primary cost

        :return: list of restaurants
        """

        recommendations = []
        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in self.user.primary_cuisines),
                    (v["costBracket"] in self.user.primary_cost_brackets),
                    (v["isRecommended"]),
                    (int(restaurant_id) not in recommendations),
                ]
            ):
                recommendations.append(int(restaurant_id))

        if not recommendations:
            recommendations = [[] for _ in range(2)]
            for restaurant_id, v in RESTAURANTS.items():
                if all(
                    [
                        (v["cuisine"] in self.user.primary_cuisines),
                        (v["costBracket"] in self.user.secondary_cost_brackets),
                        (v["isRecommended"]),
                        (int(restaurant_id) not in recommendations[0]),
                    ]
                ):
                    recommendations[0].append(int(restaurant_id))

                if all(
                    [
                        (v["cuisine"] in self.user.secondary_cuisines),
                        (v["costBracket"] in self.user.primary_cost_brackets),
                        (v["isRecommended"]),
                        (int(restaurant_id) not in recommendations[1]),
                    ]
                ):
                    recommendations[1].append(int(restaurant_id))
                return self.get_ordered_unique_recommendation(recommendations)
        else:
            return recommendations

    def get_high_ratings_restaurants(self) -> list:
        """
        Get restaurant using following logics in order:
            - All restaurants of Primary cuisine, primary cost bracket with rating >= 4
            - All restaurants of Primary cuisine, secondary cost bracket with rating >= 4.5
            - All restaurants of secondary cuisine, primary cost bracket with rating >= 4.5

        :return: list of restaurants
        """

        logic_counts = 3
        recommendations = [[] for _ in range(logic_counts)]
        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in self.user.primary_cuisines),
                    (v["costBracket"] in self.user.primary_cost_brackets),
                    (v["rating"] >= 4),
                    (int(restaurant_id) not in recommendations[0]),
                ]
            ):
                recommendations[0].append(int(restaurant_id))

            if all(
                [
                    (v["cuisine"] in self.user.primary_cuisines),
                    (v["costBracket"] in self.user.secondary_cost_brackets),
                    (v["rating"] >= 4.5),
                    (int(restaurant_id) not in recommendations[1]),
                ]
            ):
                recommendations[1].append(int(restaurant_id))

            if all(
                [
                    (v["cuisine"] in self.user.secondary_cuisines),
                    (v["costBracket"] in self.user.primary_cost_brackets),
                    (v["rating"] >= 4.5),
                    (int(restaurant_id) not in recommendations[2]),
                ]
            ):
                recommendations[2].append(int(restaurant_id))
        return self.get_ordered_unique_recommendation(recommendations)

    def get_new_created_restaurants(self) -> list:
        """
        Get Top 4 newly created restaurants by rating

        :return: list of restaurants
        """

        recommendations = []
        for restaurant in NEW_TOP_RATING_RESTAURANTS:
            if restaurant["restaurantId"] not in recommendations:
                recommendations.append(restaurant["restaurantId"])
        return recommendations

    def get_low_rating_restaurants(self) -> list:
        """
        Get restaurant using following logics in order:
            All restaurants of Primary cuisine, primary cost bracket with rating < 4
            All restaurants of Primary cuisine, secondary cost bracket with rating < 4.5
            All restaurants of secondary cuisine, primary cost bracket with rating < 4.5

        :return: list of restaurants
        """

        logic_counts = 3
        recommendations = [[] for _ in range(logic_counts)]
        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in self.user.primary_cuisines),
                    (v["costBracket"] in self.user.primary_cost_brackets),
                    (v["rating"] < 4.5),
                    (int(restaurant_id) not in recommendations[0]),
                ]
            ):
                recommendations[0].append(int(restaurant_id))

            if all(
                [
                    (v["cuisine"] in self.user.primary_cuisines),
                    (v["costBracket"] in self.user.secondary_cost_brackets),
                    (v["rating"] < 4.5),
                    (int(restaurant_id) not in recommendations[1]),
                ]
            ):
                recommendations[1].append(int(restaurant_id))

            if all(
                [
                    (v["cuisine"] in self.user.secondary_cuisines),
                    (v["costBracket"] in self.user.primary_cost_brackets),
                    (v["rating"] < 4.5),
                    (int(restaurant_id) not in recommendations[2]),
                ]
            ):
                recommendations[2].append(int(restaurant_id))
        return self.get_ordered_unique_recommendation(recommendations)

    def get_all_restaurants(self) -> list:
        """
        Get All restaurants of any cuisine, any cost bracket

        :return: list of all restaurants
        """

        recommendations = []
        for restaurant_id, v in RESTAURANTS.items():
            recommendations.append(int(restaurant_id))
        return recommendations

    @staticmethod
    def get_ordered_unique_recommendation(recommendations: list) -> list:
        """
        Spread list of lists into single list maintaining order of values

        :param recommendations: List of restaurants
        :return: list of restaurants
        """

        ordered_priorities = []
        for rec in recommendations:
            for rest in rec:
                if rest not in ordered_priorities:
                    ordered_priorities.append(rest)
        return ordered_priorities


user_recommendations = UserRestaurantRecommendation(
    user_id=1
)  # taking sample user with user_id=1
restaurants_recommendation = user_recommendations.get_restaurants_recommendations()
print(restaurants_recommendation)
