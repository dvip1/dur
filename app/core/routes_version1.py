class Routes: 
    root = "/"
    class Auth:
        root = "/auth"
        login = "/login"
        logout = "/logout"
        register = "/register"
        me = "/me"
        refresh = "/token/refresh"
        change_password = "/change-password"

    class Packages: 
        root = "/api/v1/packages"
        default ="/"
        get_by_name = "/{package_name}"
