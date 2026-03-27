import React, { useState, useEffect, useRef } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    TextField,
    Button,
    IconButton,
    Paper,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Grid,
    CircularProgress,
    Alert,
    FormControl,
    InputLabel,
    Select,
    MenuItem
} from '@mui/material';
import {
    Send as SendIcon,
    Close as CloseIcon,
    SmartToy as BotIcon,
    Person as PersonIcon,
    AutoAwesome as SparkleIcon,
    Download as DownloadIcon
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const UserChatBot = ({ open, onClose, onUserCreated }) => {
    const { getAuthHeaders } = useAuth();
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [currentStep, setCurrentStep] = useState('welcome');
    const [userData, setUserData] = useState({});
    const [showSummary, setShowSummary] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (open && messages.length === 0) {
            addBotMessage('👋 Welcome to the User Creation AI Assistant! I\'ll help you create a new user step by step. Let\'s start with the user\'s role. What role should this user have?');
            setCurrentStep('role');
        }
    }, [open]);

    const addBotMessage = (message) => {
        setMessages(prev => [...prev, { type: 'bot', text: message }]);
    };

    const addUserMessage = (message) => {
        setMessages(prev => [...prev, { type: 'user', text: message }]);
    };

    const processUserInput = async (input) => {
        const trimmedInput = input.trim().toLowerCase();
        
        switch (currentStep) {
            case 'role':
                if (trimmedInput.includes('admin') || trimmedInput.includes('administrator')) {
                    setUserData(prev => ({ ...prev, role: 'admin' }));
                    addUserMessage(input);
                    addBotMessage('✅ Great! Admin role selected. Now, which company should this user belong to? Please provide a company ID (e.g., 1, 2, 3, etc.).');
                    setCurrentStep('company');
                } else if (trimmedInput.includes('super') || trimmedInput.includes('superadmin')) {
                    setUserData(prev => ({ ...prev, role: 'super_admin' }));
                    addUserMessage(input);
                    addBotMessage('✅ Super Admin role selected. Now, which company should this user belong to? Please provide a company ID (e.g., 1, 2, 3, etc.).');
                    setCurrentStep('company');
                } else if (trimmedInput.includes('user') || trimmedInput.includes('employee') || trimmedInput.includes('staff')) {
                    setUserData(prev => ({ ...prev, role: 'user' }));
                    addUserMessage(input);
                    addBotMessage('✅ User role selected. Now, which company should this user belong to? Please provide a company ID (e.g., 1, 2, 3, etc.).');
                    setCurrentStep('company');
                } else {
                    addBotMessage('❓ I didn\'t understand that. Please choose from: **user**, **admin**, or **super_admin**');
                }
                break;

            case 'company':
                const companyId = parseInt(trimmedInput);
                if (!isNaN(companyId) && companyId > 0) {
                    setUserData(prev => ({ ...prev, companyid: companyId }));
                    addUserMessage(input);
                    addBotMessage('✅ Company ID set. Do you have a specific company domain for the user\'s email? (e.g., company.com) or should I generate one automatically?');
                    setCurrentStep('domain');
                } else {
                    addBotMessage('❓ Please provide a valid company ID (e.g., 1, 2, 3, etc.).');
                }
                break;

            case 'domain':
                if (trimmedInput === 'auto' || trimmedInput === 'automatic' || trimmedInput === 'generate') {
                    setUserData(prev => ({ ...prev, company_domain: null }));
                    addUserMessage('Generate automatically');
                    addBotMessage('✅ I\'ll generate the domain automatically. Let me create the user for you...');
                    generateUser();
                } else if (trimmedInput.includes('.') && trimmedInput.split('.').length === 2) {
                    setUserData(prev => ({ ...prev, company_domain: trimmedInput }));
                    addUserMessage(input);
                    addBotMessage('✅ Domain set. Let me create the user for you...');
                    generateUser();
                } else {
                    addBotMessage('❓ Please provide a valid domain (e.g., company.com) or say **auto** to generate automatically.');
                }
                break;

            default:
                break;
        }
    };

    const generateUser = async () => {
        setIsTyping(true);
        try {
            console.log('Generating user with data:', userData);
            console.log('User role:', userData.role);
            console.log('User company ID:', userData.companyid);
            
            const payload = {
                role: userData.role,
                company_id: userData.companyid,  // Fix: send company_id instead of companyid
                company_domain: userData.company_domain
            };
            console.log('Sending payload to backend:', payload);
            
            const response = await axios.post(
                `${process.env.REACT_APP_API_LINKS}/api/v1/ai/generate-user`,
                payload,
                { headers: getAuthHeaders() }
            );

            const user = response.data.user;
            console.log('Generated user from backend:', user);
            addBotMessage(`🎉 User created successfully! Here are the details:\n\n**Name:** ${user.name}\n**Username:** ${user.username}\n**Email:** ${user.email}\n**Role:** ${user.role}\n**Company ID:** ${user.companyid}\n**Password:** ${user.password}\n**Phone:** ${user.phone}\n**Job Title:** ${user.job_title}\n**Department:** ${user.department}\n\nWould you like me to create this user in the system?`);
            
            setUserData(prev => ({ ...prev, ...user }));
            setCurrentStep('confirm');
            setShowSummary(true);
        } catch (error) {
            console.error('Error generating user:', error);
            addBotMessage('❌ Sorry, I encountered an error while generating the user. Please try again.');
        } finally {
            setIsTyping(false);
        }
    };

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const message = inputValue;
        setInputValue('');
        addUserMessage(message);
        setIsTyping(true);

        await new Promise(resolve => setTimeout(resolve, 500));
        
        processUserInput(message);
        setIsTyping(false);
    };

    const handleConfirmUser = async () => {
        setIsTyping(true);
        try {
            console.log('Creating user with data:', userData);
            console.log('User data structure:', JSON.stringify(userData, null, 2));
            
            const response = await axios.post(
                `${process.env.REACT_APP_API_LINKS}/api/v1/users`,
                userData,
                { headers: getAuthHeaders() }
            );

            console.log('User creation response:', response.data);
            console.log('User creation status:', response.status);
            console.log('User created:', response.data.user);

            addBotMessage('✅ User successfully created and added to the system! You can now find this user in the Users page.');
            
            setTimeout(() => {
                console.log('Calling onUserCreated with:', response.data.user);
                onUserCreated(response.data.user);
                handleClose();
            }, 2000);
        } catch (error) {
            console.error('Error creating user:', error);
            console.error('Error response:', error.response?.data);
            console.error('Error status:', error.response?.status);
            console.error('Error config:', error.config);
            const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error';
            addBotMessage(`❌ Sorry, I encountered an error while creating the user in the system: ${errorMessage}`);
        } finally {
            setIsTyping(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const handleClose = () => {
        setMessages([]);
        setInputValue('');
        setCurrentStep('welcome');
        setUserData({});
        setShowSummary(false);
        onClose();
    };

    const renderMessage = (message, index) => {
        const isBot = message.type === 'bot';
        
        return (
            <Box key={index} sx={{ mb: 2, display: 'flex', justifyContent: isBot ? 'flex-start' : 'flex-end' }}>
                <Box sx={{ maxWidth: '70%' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        {isBot ? (
                            <>
                                <BotIcon sx={{ mr: 1, color: 'primary.main' }} />
                                <Typography variant="caption" color="text.secondary">
                                    AI Assistant
                                </Typography>
                            </>
                        ) : (
                            <>
                                <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
                                    You
                                </Typography>
                                <PersonIcon sx={{ color: 'secondary.main' }} />
                            </>
                        )}
                    </Box>
                    <Paper
                        sx={{
                            p: 2,
                            backgroundColor: isBot ? 'grey.100' : 'primary.main',
                            color: isBot ? 'text.primary' : 'white',
                            borderRadius: 2
                        }}
                    >
                        <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                            {message.text}
                        </Typography>
                    </Paper>
                </Box>
            </Box>
        );
    };

    return (
        <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
            <DialogTitle>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box display="flex" alignItems="center">
                        <BotIcon sx={{ mr: 1, color: 'primary.main' }} />
                        <Typography variant="h6">User Creation AI Assistant</Typography>
                    </Box>
                    <IconButton onClick={handleClose}>
                        <CloseIcon />
                    </IconButton>
                </Box>
            </DialogTitle>
            <DialogContent>
                <Box sx={{ height: 400, overflow: 'auto', p: 2, backgroundColor: 'grey.50', borderRadius: 2 }}>
                    {messages.map((message, index) => renderMessage(message, index))}
                    {isTyping && (
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <BotIcon sx={{ mr: 1, color: 'primary.main' }} />
                            <CircularProgress size={20} />
                            <Typography variant="body2" sx={{ ml: 1, color: 'text.secondary' }}>
                                AI is thinking...
                            </Typography>
                        </Box>
                    )}
                    <div ref={messagesEndRef} />
                </Box>
                
                {showSummary && currentStep === 'confirm' && (
                    <Alert severity="success" sx={{ mt: 2 }}>
                        <Typography variant="body2">
                            User is ready to be created! Click "Confirm & Create User" to add them to the system.
                        </Typography>
                    </Alert>
                )}
            </DialogContent>
            <DialogActions>
                {currentStep === 'confirm' ? (
                    <>
                        <Button onClick={handleClose}>Cancel</Button>
                        <Button
                            variant="contained"
                            onClick={handleConfirmUser}
                            disabled={isTyping}
                            startIcon={<SparkleIcon />}
                        >
                            Confirm & Create User
                        </Button>
                    </>
                ) : (
                    <>
                        <TextField
                            fullWidth
                            variant="outlined"
                            placeholder="Type your response here..."
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyPress={handleKeyPress}
                            disabled={isTyping}
                            sx={{ mr: 1 }}
                        />
                        <Button
                            variant="contained"
                            onClick={handleSendMessage}
                            disabled={isTyping || !inputValue.trim()}
                            startIcon={<SendIcon />}
                        >
                            Send
                        </Button>
                    </>
                )}
            </DialogActions>
        </Dialog>
    );
};

export default UserChatBot;
