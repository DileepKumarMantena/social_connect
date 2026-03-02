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
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/verify-token`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                    withCredentials: true,
                }
            );
            if (response.status === 200) {
                var data = response.data.data;
                setLogindata(data);
                setPermissions(data.permissions);
            }

        } catch (error) {
            console.error("Token verification failed:");
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

        if (!cookie) {
            setLoggedin(false);
            setToken(null);
        } else {
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
