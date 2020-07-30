from .views import login, logout, register

routes = [
    {'method': 'POST', 'path': '/api/user/register/', 'handler': register, 'name': 'user-register'},
    {'method': 'POST', 'path': '/api/user/login/', 'handler': login, 'name': 'user-login'},
    {'method': 'GET', 'path': '/api/user/logout/', 'handler': logout, 'name': 'user-logout'},
]
