"""
Application configuration for Cold-Chain Logistics Optimizer.
"""

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
DEBUG = True

# Algorithm Limits
MAX_TSP_CITIES = 20  # Held-Karp becomes infeasible beyond this
MAX_KNAPSACK_CAPACITY = 100000  # kg

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8080",
]
