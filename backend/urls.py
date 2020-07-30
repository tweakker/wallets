from backend.apps.wallets.urls import routes as wallets_routes
from backend.apps.users.urls import routes as users_routes

routes = [
    *wallets_routes,
    *users_routes,
]