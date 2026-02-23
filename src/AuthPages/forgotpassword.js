import React, { useState, useEffect, useRef } from "react";
import { Box, Button, Typography, FormControl, OutlinedInput } from "@mui/material";
import '@fontsource/nunito';
import '@fontsource/cookie';
import axios from 'axios';
import Swal from 'sweetalert2';
import { useNavigate } from "react-router-dom";

const ForgotPasswordPage = () => {
    const [step, setStep] = useState(1);
    const [payload, setPayload] = useState({ email: '', otp: ['', '', '', ''], newPassword: '', confirmPassword: '' });
    const navigate = useNavigate();

    const otpRefs = useRef([]);

    const handler = (e) => {
        const { name, value } = e.target;

        if (name.startsWith('otp')) {
            const index = parseInt(name.split('-')[1]);
            const newOtp = [...payload.otp];

            const char = value.slice(-1);
            newOtp[index] = char;

            setPayload({ ...payload, otp: newOtp });

            if (char && index < 3) {
                otpRefs.current[index + 1].focus();
            }
        } else {
            setPayload({ ...payload, [name]: value });
        }
    };

    const handleOtpKeyDown = (e, index) => {
        if (e.key === 'Backspace') {
            if (!payload.otp[index] && index > 0) {
                otpRefs.current[index - 1].focus();
            }
        }
    };

    const handlePaste = (e) => {
        e.preventDefault();
        const data = e.clipboardData.getData("text").slice(0, 4).split("");
        const newOtp = [...payload.otp];

        data.forEach((char, index) => {
            if (index < 4) newOtp[index] = char;
        });

        setPayload({ ...payload, otp: newOtp });

        const lastIndex = Math.min(data.length, 3);
        otpRefs.current[lastIndex].focus();
    };

    const handleSendEmail = () => {
        axios.post(`${process.env.REACT_APP_API_LINKS}/api/v1/forgot-password`, { email: payload.email })
            .then(res => {
                Swal.fire({
                    title: 'OTP Sent',
                    text: 'Check your email',
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
                setStep(2);
            })
            .catch(err => {
                Swal.fire({
                    title: 'Error',
                    text: 'Email not found',
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
            });
    };

    const handleVerifyOTP = () => {
        const otpvalue = payload?.otp?.join('')

        axios.post(`${process.env.REACT_APP_API_LINKS}/api/v1/verify-otp`, { email: payload.email, otp: otpvalue })
            .then(res => {
                Swal.fire({
                    title: 'OTP Verified',
                    text: 'You can reset your password now',
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
                setStep(3);
            })
            .catch(err => {
                Swal.fire({
                    title: 'Error',
                    text: 'Invalid OTP',
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
            });
    };

    const handleResetPassword = () => {
        if (payload.newPassword !== payload.confirmPassword) {
            Swal.fire({
                title: 'Error',
                text: 'Passwords do not match',
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
            return;
        }

        axios.post(`${process.env.REACT_APP_API_LINKS}/api/v1/reset-password`, { email: payload.email, password: payload.newPassword })
            .then(res => {
                Swal.fire({
                    title: 'Success',
                    text: 'Password reset successfully',
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
                navigate('/');
            })
            .catch(err => {
                Swal.fire({
                    title: 'Error',
                    text: 'Something went wrong',
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
            });
    };

    useEffect(() => {
        if (step === 2 && otpRefs.current[0]) {
            otpRefs.current[0].focus();
        }
    }, [step]);

    return (
        <Box sx={{ display: "flex", minHeight: "100vh", fontFamily: "Nunito, sans-serif", background: '#f5f5f5' }}>
            {/* Left Side - Image */}
            <Box
                sx={{
                    display: { xs: "none", md: "flex" },
                    width: "40%",
                    height: "100vh",
                    backgroundImage: "url('login_left.png')",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                    position: "relative",
                    animation: "fadeSlideLeft 1s ease forwards",
                    "@keyframes fadeSlideLeft": {
                        "0%": { opacity: 0, transform: "translateX(100%)" },
                        "100%": { opacity: 1, transform: "translateX(0)" },
                    },
                    "&::after": {
                        content: '""',
                        position: "absolute",
                        top: 0, left: 0, width: "100%", height: "100%",
                        background: "rgba(0,0,0,0.2)",
                    },
                }}
            />

            {/* Right Side - Content */}
            <Box
                sx={{
                    width: { xs: "100%", md: "60%" },
                    px: { xs: 3, md: 5 },
                    py: { xs: 4, md: 4 },
                    display: "flex",
                    justifyContent: { xs: "center", md: "flex-end" },
                    alignItems: { xs: "center", md: "start" },
                }}
            >
                <Box sx={{ width: "100%", maxWidth: "500px" }}>
                    <Typography sx={{ fontFamily: "Cookie, cursive", mb: 3, color: "#136aed", fontSize: '2.5rem' }}>
                        Social Connect
                    </Typography>

                    <Typography variant="h5" sx={{ fontFamily: "nunito, sans-serif", mb: 1, fontWeight: 700 }}>
                        Forgot Password
                    </Typography>
                    <Typography variant="body2" color="#636161" sx={{ mb: 3, fontFamily: 'Nunito' }}>
                        {step === 2 ? "Enter the 4-digit code sent to your email" : "Enter your email to reset your password"}
                    </Typography>

                    <Box sx={{ mt: 2 }}>
                        {step === 1 && (
                            <>
                                <FormControl fullWidth sx={{ mb: 3 }}>
                                    <Typography sx={{ mb: 1, fontSize: '0.875rem', fontWeight: 600 }}>Email / Username</Typography>
                                    <OutlinedInput
                                        placeholder="Enter your email"
                                        name="email"
                                        onChange={handler}
                                        sx={{ borderRadius: 1, height: '45px', background: '#f2f4f7' }}
                                    />
                                </FormControl>
                                <Button variant="contained" fullWidth onClick={handleSendEmail} sx={{ backgroundColor: '#136aed' }}>
                                    SEND OTP
                                </Button>
                            </>
                        )}

                        {step === 2 && (
                            <>
                                <Box sx={{ display: 'flex', gap: 2, mb: 3, justifyContent: "center" }}>
                                    {Array(4).fill().map((_, i) => (
                                        <OutlinedInput
                                            key={i}
                                            name={`otp-${i}`}
                                            value={payload.otp[i]}
                                            onChange={handler}
                                            onKeyDown={(e) => handleOtpKeyDown(e, i)}
                                            onPaste={i === 0 ? handlePaste : undefined}
                                            inputProps={{ maxLength: 1, style: { textAlign: 'center' } }}
                                            inputRef={el => otpRefs.current[i] = el}
                                            sx={{
                                                width: '50px',
                                                height: '50px',
                                                fontSize: '1.5rem',
                                                background: '#f2f4f7',
                                            }}
                                        />
                                    ))}
                                </Box>
                                <Button variant="contained" fullWidth onClick={handleVerifyOTP} sx={{ backgroundColor: '#136aed' }}>
                                    VERIFY OTP
                                </Button>
                            </>
                        )}

                        {step === 3 && (
                            <>
                                <FormControl fullWidth sx={{ mb: 3 }}>
                                    <Typography sx={{ mb: 1, fontSize: '0.875rem', fontWeight: 600 }}>New Password</Typography>
                                    <OutlinedInput
                                        type="password"
                                        name="newPassword"
                                        onChange={handler}
                                        sx={{ borderRadius: 1, height: '45px', background: '#f2f4f7' }}
                                    />
                                </FormControl>
                                <FormControl fullWidth sx={{ mb: 3 }}>
                                    <Typography sx={{ mb: 1, fontSize: '0.875rem', fontWeight: 600 }}>Confirm Password</Typography>
                                    <OutlinedInput
                                        type="password"
                                        name="confirmPassword"
                                        onChange={handler}
                                        sx={{ borderRadius: 1, height: '45px', background: '#f2f4f7' }}
                                    />
                                </FormControl>
                                <Button variant="contained" fullWidth onClick={handleResetPassword} sx={{ backgroundColor: '#136aed' }}>
                                    RESET PASSWORD
                                </Button>
                            </>
                        )}
                    </Box>
                </Box>
            </Box>
        </Box>
    );
};

export default ForgotPasswordPage;