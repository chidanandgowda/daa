#include <stdio.h>
#include <limits.h>

#define INF 999999
#define N 4

/**
 * TSP Held-Karp using Dynamic Programming and Bitmasking.
 * Complexity: O(n^2 * 2^n)
 */

int dist[N][N] = {
    {0, 10, 15, 20},
    {5, 0, 9, 10},
    {6, 13, 0, 12},
    {8, 8, 9, 0}
};

int memo[1 << N][N];

int tsp(int mask, int pos) {
    if (mask == (1 << N) - 1) {
        return dist[pos][0];
    }

    if (memo[mask][pos] != -1) {
        return memo[mask][pos];
    }

    int ans = INF;

    for (int city = 0; city < N; city++) {
        if ((mask & (1 << city)) == 0) {
            int newAns = dist[pos][city] + tsp(mask | (1 << city), city);
            if (newAns < ans) {
                ans = newAns;
            }
        }
    }

    return memo[mask][pos] = ans;
}

int main() {
    for (int i = 0; i < (1 << N); i++) {
        for (int j = 0; j < N; j++) {
            memo[i][j] = -1;
        }
    }

    printf("The minimum travel cost is %d\n", tsp(1, 0));
    return 0;
}
