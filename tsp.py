from functools import lru_cache
import itertools

def tsp(adj_matrix, start_city_idx):
    n = len(adj_matrix)

    @lru_cache(None)
    def dp(mask, pos):
        if mask == (1 << n) - 1:
            return adj_matrix[pos][start_city_idx]

        min_cost = float('inf')
        for city in range(n):
            if mask & (1 << city) == 0:
                new_cost = adj_matrix[pos][city] + dp(mask | (1 << city), city)
                min_cost = min(min_cost, new_cost)
        return min_cost

    mask = 1 << start_city_idx
    min_cost = dp(mask, start_city_idx)

    # Reconstruct the path
    path = []
    mask = 1 << start_city_idx
    pos = start_city_idx

    while True:
        path.append(pos)
        if mask == (1 << n) - 1:
            break

        next_city = None
        for city in range(n):
            if mask & (1 << city) == 0:
                if next_city is None or \
                        adj_matrix[pos][city] + dp(mask | (1 << city), city) < \
                        adj_matrix[pos][next_city] + dp(mask | (1 << next_city), next_city):
                    next_city = city

        pos = next_city
        mask |= (1 << pos)

    path.append(start_city_idx)  # Return to start city
    return path, min_cost

# Example usage
# if __name__ == "__main__":
#     adj_matrix = [
#         [0, 10, 15, 20],
#         [10, 0, 35, 25],
#         [15, 35, 0, 30],
#         [20, 25, 30, 0]
#     ]
#     start_city_idx = 0
#     order, distance = tsp(adj_matrix, start_city_idx)
#
