#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <stdbool.h>

#define INF INT_MAX

/**
 * Simple Dijkstra implementation for presentation.
 * In the real app, we use a priority queue (min-heap), 
 * but this array-based version is easier to follow for presentations.
 */
void dijkstra(int n, int graph[n][n], int start_node) {
    int dist[n];
    bool visited[n];

    for (int i = 0; i < n; i++) {
        dist[i] = INF;
        visited[i] = false;
    }

    dist[start_node] = 0;

    for (int count = 0; count < n - 1; count++) {
        int u = -1;
        int min_dist = INF;

        // Find min distance node not yet visited
        for (int i = 0; i < n; i++) {
            if (!visited[i] && dist[i] <= min_dist) {
                min_dist = dist[i];
                u = i;
            }
        }

        if (u == -1) break;
        visited[u] = true;

        // Update neighbors
        for (int v = 0; v < n; v++) {
            if (!visited[v] && graph[u][v] && dist[u] != INF 
                && dist[u] + graph[u][v] < dist[v]) {
                dist[v] = dist[u] + graph[u][v];
            }
        }
    }

    printf("Node \t Distance from Source %d\n", start_node);
    for (int i = 0; i < n; i++) {
        printf("%d \t\t %d\n", i, dist[i]);
    }
}

int main() {
    int n = 5;
    int graph[5][5] = {
        {0, 10, 0, 0, 5},
        {0, 0, 1, 0, 2},
        {0, 0, 0, 4, 0},
        {7, 0, 0, 0, 0},
        {0, 3, 9, 2, 0}
    };

    dijkstra(n, graph, 0);
    return 0;
}
