class Routes: 
    root = "/"
    class Auth:
        root = "/api/auth"
        login = "/login"
        logout = "/logout"
        register = "/register"
        me = "/me"
        refresh = "/token/refresh"
        change_password = "/change-password"