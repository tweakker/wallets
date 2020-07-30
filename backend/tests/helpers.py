
async def user_auth(cli, user_name, user_password):
    login_url = cli.app.router['user-login'].url_for()
    resp = await cli.post(login_url, json={'name': user_name, 'password': user_password})
    assert resp.status == 200
