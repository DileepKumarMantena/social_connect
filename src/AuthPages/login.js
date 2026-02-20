import React, { useState } from "react";
import { Box, Button, Container, TextField, Typography, FormControlLabel } from "@mui/material";
import '@fontsource/poppins';
import '@fontsource/nunito';
import '@fontsource/cookie';
import FormControl, { useFormControl } from '@mui/material/FormControl';
import OutlinedInput from '@mui/material/OutlinedInput';
import axios from 'axios'
import Swal from 'sweetalert2'
import { Link } from "react-router-dom";

const LoginPage = () => {
    const [payload, setPayload] = useState({ username: '', password: '' })

    const handler = (e) => {
        const { name, value } = e.target;
        setPayload({ ...payload, [name]: value })
    }
    const handleLogin = () => {
        axios.post(`${process.env.REACT_APP_API_LINKS}/api/v1/login`, payload, { withCredentials: true })
            .then((res) => {
                if (res.status === 200) {
                    Swal.fire({
                        title: 'Login Success',
                        text: 'User logged in',
                        icon: 'success',
                        width: 300,
                        heightAuto: false,
                        showConfirmButton: false,
                        timer: 1000,
                        timerProgressBar: true,
                        customClass: {
                            popup: 'swal-popup', 
                            title: 'swal-title',   
                            content: 'swal-text',    
                        }
                    });
                }
            })
            .catch(err => {
                const status = err.response?.status || 500;
                if (status === 500) {
                    Swal.fire({
                        title: 'The Internet?',
                        text: 'That thing is still around?',
                        icon: 'question',
                        width: 300,
                        heightAuto: false,
                        showConfirmButton: false,
                        timer: 1000,
                        timerProgressBar: true,
                        customClass: {
                            popup: 'swal-popup',
                            title: 'swal-title',
                            content: 'swal-text',
                        }
                    });
                } else {
                    Swal.fire({
                        title: 'Wrong Credentials Entered',
                        text: 'Password wrong',
                        icon: 'error',
                        width: 300,
                        heightAuto: false,
                        showConfirmButton: false,
                        timer: 1000,
                        timerProgressBar: true,
                        customClass: {
                            popup: 'swal-popup',
                            title: 'swal-title',
                            content: 'swal-text',
                        }
                    });
                }
            });
    };
    return (
        <Box sx={{ display: "flex", minHeight: "100vh", fontFamily: "Nunito, sans-serif", background: ' #f5f5f5' }}>
            {/* left side card */}
            <Box
                sx={{
                    width: { xs: "100%", md: "60%" },
                    px: { xs: 3, md: 5 },
                    py: { xs: 4, md: 4 },
                    display: "flex",
                    justifyContent: {
                        xs: "center",
                        md: "flex-start",
                    },
                    alignItems: {
                        xs: "center",
                        md: "start",
                    },
                    animation: "fadeSlideIn 0.8s ease forwards",
                    "@keyframes fadeSlideIn": {
                        "0%": { opacity: 0, transform: "translateY(-50px)" },
                        "100%": { opacity: 1, transform: "translateY(0)" },
                    },
                }}
            >
                <Box
                    sx={{
                        width: "100%",
                        maxWidth: "500px",
                    }}
                >
                    {/* Heading */}
                    <Typography

                        sx={{ fontFamily: "Cookie, cursive", mb: { xs: 2, md: 8 }, color: "#136aed", fontSize: '2.5rem' }}
                    >
                        Social Connect
                    </Typography>

                    {/* Subheading */}
                    <Typography
                        variant="h5"
                        sx={{
                            fontFamily: " poppins, sans-serif",
                            mb: 1,
                            animation: "fadeIn 0.6s ease forwards",
                            opacity: 0,
                            fontWeight: '700',
                            textShadow: 'none',
                            wordSpacing: '5px',
                            letterSpacing: '1.3px',
                            fontSize: '1.5rem',
                            "@keyframes fadeIn": {
                                "0%": { opacity: 0, transform: "translateY(20px)" },
                                "100%": { opacity: 1, transform: "translateY(0)" },
                            },
                        }}
                    >
                        Welcome Back
                    </Typography>
                    <Typography
                        variant="body2"
                        color="#636161"
                        sx={{
                            mb: 3,
                            animation: "fadeIn 0.6s ease forwards",
                            animationDelay: "0.2s",
                            opacity: 0,
                            fontFamily: 'nunito'
                        }}
                    >
                        Please enter your details to login.
                    </Typography>


                    <Box sx={{ width: '100%', maxWidth: '500px', mt: 2 }}>
                        <FormControl fullWidth variant="outlined" sx={{ mb: 3 }}>
                            <Typography
                                sx={{
                                    mb: 1,
                                    fontSize: '0.875rem',
                                    fontWeight: 600,
                                    letterSpacing: '1px',
                                    fontFamily: 'poppins',
                                    textShadow: 'none',
                                }}
                            >
                                Username
                            </Typography>
                            <OutlinedInput
                                placeholder="Please enter username"
                                name="username"
                                onChange={handler}
                                sx={{
                                    borderRadius: 1,
                                    height: '45px',
                                    background: '#f2f4f7',
                                    '& .MuiOutlinedInput-notchedOutline': {
                                        borderColor: '#ccc',
                                        borderWidth: '0.5px',
                                    },
                                    '&:hover .MuiOutlinedInput-notchedOutline': {
                                        borderColor: '#136aed',
                                        borderWidth: '0.5px',

                                    },
                                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                                        borderColor: '#136aed',
                                        borderWidth: '0.5px',

                                    },
                                }}
                            />
                        </FormControl>

                        <FormControl fullWidth variant="outlined" sx={{ mb: 2 }}>
                            <Typography
                                sx={{
                                    mb: 1,
                                    fontSize: '0.875rem',
                                    fontWeight: 600,
                                    letterSpacing: '1px',
                                    fontFamily: 'poppins',
                                    textShadow: 'none',
                                }}
                            >
                                Password
                            </Typography>
                            <OutlinedInput
                                type="password"
                                placeholder="Password"
                                onChange={handler}
                                name='password'
                                sx={{
                                    borderRadius: 1,
                                    height: '45px',
                                    background: '#f2f4f7',
                                    '& .MuiOutlinedInput-notchedOutline': {
                                        borderColor: '#ccc',
                                        borderWidth: '0.5px',
                                    },
                                    '&:hover .MuiOutlinedInput-notchedOutline': {
                                        borderColor: '#136aed',
                                        borderWidth: '0.5px',
                                    },
                                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                                        borderColor: '#136aed',
                                        borderWidth: '0.5px',
                                    },
                                }}
                            />
                        </FormControl>

                        <Button
                            variant="contained"
                            size="medium"
                            sx={{
                                width: '100%',
                                backgroundColor: '#136aed',
                                border: 'none',
                                borderRadius: 1,
                                boxShadow: 3,
                                color: 'white',
                                cursor: 'pointer',
                                fontFamily: 'poppins',
                            }}
                            onClick={handleLogin}
                        >
                            LOGIN
                        </Button>
                        <Link sx={{
                            textDecoration: 'none',
                            opacity: 0.7,
                            color: '#136aed',
                            '&:hover':
                            {
                                opacity: 1,
                            }
                        }}
                            to='/forgot'>
                            <Typography
                                sx={{ mt: 2, textAlign: 'right', fontFamily: 'poppins', textDecoration: 'none', }}>
                                Forgot Password?
                            </Typography>
                        </Link>
                    </Box>


                </Box>
            </Box>
            {/* right side card */}
            <Box
                sx={{
                    display: { xs: "none", md: "flex" },
                    width: "40%",
                    height: "100vh",
                    backgroundImage: "url('login_left.png')",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                    position: "relative",
                    animation: "fadeSlideRight 0.8s ease forwards",
                    "@keyframes fadeSlideRight": {
                        "0%": { opacity: 0, transform: "translateX(80px)" },
                        "100%": { opacity: 1, transform: "translateX(0)" },
                    },
                    "&::after": {
                        content: '""',
                        position: "absolute",
                        top: 0,
                        left: 0,
                        width: "100%",
                        height: "100%",
                        background: "rgba(0,0,0,0.2)",
                    },
                }}
            />
        </Box>
    );
};

export default LoginPage;