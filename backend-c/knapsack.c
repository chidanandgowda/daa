#include <stdio.h>

#define MAX(a, b) ((a) > (b) ? (a) : (b))

/**
 * 0/1 Knapsack Implementation
 * Solves the optimal cargo loading problem.
 */
int knapsack(int W, int weights[], int values[], int n) {
    int i, w;
    int K[n + 1][W + 1];

    for (i = 0; i <= n; i++) {
        for (w = 0; w <= W; w++) {
            if (i == 0 || w == 0)
                K[i][w] = 0;
            else if (weights[i - 1] <= w)
                K[i][w] = MAX(values[i - 1] + K[i - 1][w - weights[i - 1]], K[i - 1][w]);
            else
                K[i][w] = K[i - 1][w];
        }
    }

    return K[n][W];
}

int main() {
    int values[] = {60, 100, 120};
    int weights[] = {10, 20, 30};
    int W = 50;
    int n = sizeof(values) / sizeof(values[0]);
    
    printf("Maximum value that can be put in a knapsack of capacity %d is %d\n", W, knapsack(W, weights, values, n));
    return 0;
}
