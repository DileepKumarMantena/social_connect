import { useState } from "react";
import { AuthContext } from "./AuthContext";
import { useEffect } from "react";

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

export const AuthProvider = ({ children }) => {
    const [loggedin, setLoggedin] = useState(false);
    const [token, setToken] = useState(null);
    const [logindata, setLogindata] = useState({
        "username": "superadmin",
        "email": "superadmin@company.com",
        "name": "Super Admin",
        "role": "super_admin",
        "companyid": 0,
        "activitystatus": true,
    })
    const cookie = getCookie('token');

    useEffect(() => {
        if (!cookie) {
            setLoggedin(false)
            setToken(cookie)
        }
        else {
            setLoggedin(true)
            setToken(null)
        }
    }, [loggedin])
    return (
        <AuthContext.Provider value={{ token, loggedin ,logindata}}>
            {children}
        </AuthContext.Provider>
    );
}
