import { useState } from "react";
import { AuthContext } from "./AuthContext";
import { useEffect } from "react";
import axios from "axios";

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

export const AuthProvider = ({ children }) => {
    const [loggedin, setLoggedin] = useState(false);
    const [token, setToken] = useState(null)
    const [logindata, setLogindata] = useState({})
    const [permissions, setPermissions] = useState({
        analytics: {
            Create: false,
            Read: false,
            Update: false,
            Delete: false
        },
        campaigns: {
            Create: false,
            Read: false,
            Update: false,
            Delete: false
        },
        channels: {
            Create: false,
            Read: false,
            Update: false,
            Delete: false
        },
        leads: {
            Create: false,
            Read: false,
            Update: false,
            Delete: false
        },
        role_management: {
            Create: false,
            Read: false,
            Update: false,
            Delete: false
        },
        scheduler: {
            Create: false,
            Read: false,
            Update: false,
            Delete: false
        }
    });
    const cookie = getCookie('token');


    const verifyToken = async (token) => {
        if (!token) return;

        try {
            console.log("Verifying token with API:", `${process.env.REACT_APP_API_LINKS}/api/v1/verify-token`);
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/verify-token`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                    withCredentials: true,
                }
            );
            console.log("Verify token response:", response);
            console.log("Response status:", response.status);
            console.log("Response data:", response.data);
            
            if (response.status === 200) {
                var data = response.data.data;
                console.log("Token verification successful, setting data:", data);
                console.log("Setting permissions:", data.permissions);
                setLogindata(data);
                setPermissions(data.permissions);
            } else {
                console.log("Unexpected response status:", response.status);
            }

        } catch (error) {
            console.error("Token verification failed:", error);
            console.error("Error response:", error.response);
            setLoggedin(false);
            setToken(null);
            setPermissions({
                analytics: {
                    Create: false,
                    Read: false,
                    Update: false,
                    Delete: false
                },
                campaigns: {
                    Create: false,
                    Read: false,
                    Update: false,
                    Delete: false
                },
                channels: {
                    Create: false,
                    Read: false,
                    Update: false,
                    Delete: false
                },
                leads: {
                    Create: false,
                    Read: false,
                    Update: false,
                    Delete: false
                },
                role_management: {
                    Create: false,
                    Read: false,
                    Update: false,
                    Delete: false
                },
                scheduler: {
                    Create: false,
                    Read: false,
                    Update: false,
                    Delete: false
                }
            });
        }
    };

    useEffect(() => {
        const cookie = getCookie('token');
        console.log("AuthProvider useEffect - cookie found:", cookie);

        if (!cookie) {
            console.log("No token found, setting loggedin false");
            setLoggedin(false);
            setToken(null);
        } else {
            console.log("Token found, setting loggedin true and verifying token");
            setLoggedin(true);
            setToken(cookie);
            verifyToken(cookie);
        }
    }, []);

    return (
        <AuthContext.Provider value={{ token, loggedin, logindata,permissions }}>
            {children}
        </AuthContext.Provider>
    );
}
