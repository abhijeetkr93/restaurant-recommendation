from mock_service import ALL_ORDERS, RESTAURANTS, NEW_TOP_RATING_RESTAURANTS


class UserRestaurantOrders:
    def __init__(self, user_id) -> None:
        self.user_id = user_id

    def get_user_orders(self) -> list:
        """
        Get all the user's order from all orders
        :return: user's order list
        """

        user_orders = []
        for val in ALL_ORDERS.values():
            if val["userId"] == self.user_id:
                user_orders.append(val)
        return user_orders


class UserCuisines:
    def __init__(self, user_orders) -> None:
        self.user_orders = user_orders
        self.primary_cuisine = None
        self.secondary_cuisine = None

    def calculate_user_cuisines(self) -> None:
        """
        calculates the user primary and secondary cuisines based on
        numbers of orders he placed
        """

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

    def primary_cuisines(self) -> list:
        """
        :return: user's primary cuisine
        """

        if not self.primary_cuisine:
            self.calculate_user_cuisines()
        return self.primary_cuisine

    def secondary_cuisines(self) -> list:
        """
        :return: user's secondary cuisines
        """

        if not self.secondary_cuisine or not self.primary_cuisine:
            self.calculate_user_cuisines()
        return self.secondary_cuisine


class UserCostBracket:
    def __init__(self, user_orders) -> None:
        self.user_orders = user_orders
        self.primary_cost_bracket = None
        self.secondary_cost_bracket = None

    def calculate_user_cost_brackets(self) -> None:
        """
        calculates the user primary and secondary costBracket based on
        numbers of orders he placed
        """

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

    def primary_cost_brackets(self) -> list:
        """
        :return: user's primary cost bracket
        """

        if not self.primary_cost_bracket:
            self.calculate_user_cost_brackets()
        return self.primary_cost_bracket

    def secondary_cost_brackets(self) -> list:
        """
        :return: user's secondary cost bracket
        """

        if not self.secondary_cost_bracket or not self.primary_cost_bracket:
            self.calculate_user_cost_brackets()
        return self.secondary_cost_bracket


class UserRestaurantRecommendation:
    LOGIC_TYPES = [
        "get_featured_restaurants",
        "get_high_ratings_restaurants",
        "get_new_created_restaurants",
        "get_low_rating_restaurants",
        "get_all_restaurants",
    ]

    def __init__(self, user_id) -> None:
        self.user_orders = UserRestaurantOrders(user_id).get_user_orders()
        self.user_cuisines = UserCuisines(self.user_orders)
        self.user_cost_brackets = UserCostBracket(self.user_orders)

    def get_restaurants_recommendations(self) -> list:
        """
        Get final recommendation ordered list of restaurants using set of
        multiple logics

        :return: list of restaurants
        """

        user_details = {
            "prim_cuisines": self.user_cuisines.primary_cuisines(),
            "secondary_cuisines": self.user_cuisines.secondary_cuisines(),
            "primary_cost_brackets": self.user_cost_brackets.primary_cost_brackets(),
            "secondary_cost_brackets": self.user_cost_brackets.secondary_cost_brackets(),
        }
        recommendations_priorities = [
            getattr(UserRestaurantRecommendation, f"{logic}")(self, **user_details)
            for logic in self.LOGIC_TYPES
        ]
        return self.get_ordered_unique_recommendation(recommendations_priorities)

    def get_featured_restaurants(self, **kwargs) -> list:
        """
        Get featured restaurants of primary cuisine and primary cost bracket.
        If none, then all featured restaurants of primary cuisine, secondary cost
        and secondary cuisine, primary cost

        :param kwargs: user details viz. (primary/sec cuisines, costBrackets)
        :return: list of restaurants
        """

        prim_cuisines = kwargs["prim_cuisines"]
        secondary_cuisines = kwargs["secondary_cuisines"]
        primary_cost_brackets = kwargs["primary_cost_brackets"]
        secondary_cost_brackets = kwargs["secondary_cost_brackets"]
        recommendations = []
        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in prim_cuisines),
                    (v["costBracket"] in primary_cost_brackets),
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
                        (v["cuisine"] in prim_cuisines),
                        (v["costBracket"] in secondary_cost_brackets),
                        (v["isRecommended"]),
                        (int(restaurant_id) not in recommendations[0]),
                    ]
                ):
                    recommendations[0].append(int(restaurant_id))

                if all(
                    [
                        (v["cuisine"] in secondary_cuisines),
                        (v["costBracket"] in primary_cost_brackets),
                        (v["isRecommended"]),
                        (int(restaurant_id) not in recommendations[1]),
                    ]
                ):
                    recommendations[1].append(int(restaurant_id))
                return self.get_ordered_unique_recommendation(recommendations)
        else:
            return recommendations

    def get_high_ratings_restaurants(self, **kwargs) -> list:
        """
        Get restaurant using following logics in order:
            - All restaurants of Primary cuisine, primary cost bracket with rating >= 4
            - All restaurants of Primary cuisine, secondary cost bracket with rating >= 4.5
            - All restaurants of secondary cuisine, primary cost bracket with rating >= 4.5

        :param kwargs: user details viz. (primary/sec cuisines, costBrackets)
        :return: list of restaurants
        """

        prim_cuisines = kwargs["prim_cuisines"]
        secondary_cuisines = kwargs["secondary_cuisines"]
        primary_cost_brackets = kwargs["primary_cost_brackets"]
        secondary_cost_brackets = kwargs["secondary_cost_brackets"]
        logic_counts = 3
        recommendations = [[] for _ in range(logic_counts)]
        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in prim_cuisines),
                    (v["costBracket"] in primary_cost_brackets),
                    (v["rating"] >= 4),
                    (int(restaurant_id) not in recommendations[0]),
                ]
            ):
                recommendations[0].append(int(restaurant_id))

            if all(
                [
                    (v["cuisine"] in prim_cuisines),
                    (v["costBracket"] in secondary_cost_brackets),
                    (v["rating"] >= 4.5),
                    (int(restaurant_id) not in recommendations[1]),
                ]
            ):
                recommendations[1].append(int(restaurant_id))

            if all(
                [
                    (v["cuisine"] in secondary_cuisines),
                    (v["costBracket"] in primary_cost_brackets),
                    (v["rating"] >= 4.5),
                    (int(restaurant_id) not in recommendations[2]),
                ]
            ):
                recommendations[2].append(int(restaurant_id))
        return self.get_ordered_unique_recommendation(recommendations)

    def get_new_created_restaurants(self, **kwargs) -> list:
        """
        Get Top 4 newly created restaurants by rating

        :param kwargs: user details viz. (primary/sec cuisines, costBrackets)
        :return: list of restaurants
        """

        recommendations = []
        for restaurant in NEW_TOP_RATING_RESTAURANTS:
            if restaurant["restaurantId"] not in recommendations:
                recommendations.append(restaurant["restaurantId"])
        return recommendations

    def get_low_rating_restaurants(self, **kwargs) -> list:
        """
        Get restaurant using following logics in order:
            All restaurants of Primary cuisine, primary cost bracket with rating < 4
            All restaurants of Primary cuisine, secondary cost bracket with rating < 4.5
            All restaurants of secondary cuisine, primary cost bracket with rating < 4.5

        :param kwargs: user details viz. (primary/sec cuisines, costBrackets)
        :return: list of restaurants
        """

        prim_cuisines = kwargs["prim_cuisines"]
        secondary_cuisines = kwargs["secondary_cuisines"]
        primary_cost_brackets = kwargs["primary_cost_brackets"]
        secondary_cost_brackets = kwargs["secondary_cost_brackets"]
        logic_counts = 3
        recommendations = [[] for _ in range(logic_counts)]
        for restaurant_id, v in RESTAURANTS.items():
            if all(
                [
                    (v["cuisine"] in prim_cuisines),
                    (v["costBracket"] in primary_cost_brackets),
                    (v["rating"] < 4.5),
                    (int(restaurant_id) not in recommendations[0]),
                ]
            ):
                recommendations[0].append(int(restaurant_id))

            if all(
                [
                    (v["cuisine"] in prim_cuisines),
                    (v["costBracket"] in secondary_cost_brackets),
                    (v["rating"] < 4.5),
                    (int(restaurant_id) not in recommendations[1]),
                ]
            ):
                recommendations[1].append(int(restaurant_id))

            if all(
                [
                    (v["cuisine"] in secondary_cuisines),
                    (v["costBracket"] in primary_cost_brackets),
                    (v["rating"] < 4.5),
                    (int(restaurant_id) not in recommendations[2]),
                ]
            ):
                recommendations[2].append(int(restaurant_id))
        return self.get_ordered_unique_recommendation(recommendations)

    def get_all_restaurants(self, **kwargs) -> list:
        """
        Get All restaurants of any cuisine, any cost bracket

        :param kwargs: user details viz. (primary/sec cuisines, costBrackets)
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
