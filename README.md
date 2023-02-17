# Restaurants recommendations

## Solution

```sh
$ python recommendation.py
returns list of restaurents ids in orders based on set of following logics:

1. Featured restaurants of primary cuisine and primary cost bracket. If none, then all featured restaurants of primary cuisine, secondary cost and secondary cuisine, primary cost
2. All restaurants of Primary cuisine, primary cost bracket with rating >= 4
3. All restaurants of Primary cuisine, secondary cost bracket with rating >= 4.5
4. All restaurants of secondary cuisine, primary cost bracket with rating >= 4.5
5. Top 4 newly created restaurants by rating
6. All restaurants of Primary cuisine, primary cost bracket with rating < 4
7. All restaurants of Primary cuisine, secondary cost bracket with rating < 4.5
8. All restaurants of secondary cuisine, primary cost bracket with rating < 4.5
```

## Modules Documentation 

```sh
$ open doc/_build/html/index.html
```


## Mocks
> Please refer following file for creating fresh mocks of orders.json, restaurants.json
```sh
$ python mock.py 
```
