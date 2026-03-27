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
    Alert
} from '@mui/material';
import {
    Send as SendIcon,
    Close as CloseIcon,
    SmartToy as BotIcon,
    Person as PersonIcon,
    AutoAwesome as SparkleIcon,
    Business as BusinessIcon
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const CompanyChatBot = ({ open, onClose, onCompanyCreated }) => {
    const { getAuthHeaders } = useAuth();
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [currentStep, setCurrentStep] = useState('welcome');
    const [companyData, setCompanyData] = useState({});
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
            addBotMessage('🏢 Welcome to the Company Creation AI Assistant! I\'ll help you create a new company step by step. Let\'s start with the industry. What industry should this company belong to?');
            setCurrentStep('industry');
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
        console.log('Processing input. Current step:', currentStep, 'Input:', trimmedInput);
        
        switch (currentStep) {
            case 'industry':
                console.log('Industry step. Input:', trimmedInput);
                const validIndustries = ['technology', 'healthcare', 'finance', 'retail', 'education', 'manufacturing'];
                const matchedIndustry = validIndustries.find(industry => trimmedInput.includes(industry));
                
                if (matchedIndustry) {
                    setCompanyData(prev => ({ ...prev, industry: matchedIndustry.charAt(0).toUpperCase() + matchedIndustry.slice(1) }));
                    addUserMessage(input);
                    addBotMessage(`✅ ${matchedIndustry.charAt(0).toUpperCase() + matchedIndustry.slice(1)} industry selected. Now, would you like to:\n\n1. **Auto-generate** all company details\n2. **Provide custom details** manually\n\nType **auto** or **manual** to continue.`);
                    setCurrentStep('generation_mode');
                } else {
                    addBotMessage(`❓ I didn't recognize that industry. Please choose from: **Technology**, **Healthcare**, **Finance**, **Retail**, **Education**, or **Manufacturing**`);
                }
                break;

            case 'generation_mode':
                console.log('Generation mode step. Input:', trimmedInput);
                if (trimmedInput === 'auto' || trimmedInput === 'automatic' || trimmedInput === 'generate') {
                    addUserMessage('Auto-generate all details');
                    addBotMessage('✅ I\'ll generate all company details automatically. Let me create the company for you...');
                    generateCompany();
                } else if (trimmedInput === 'manual' || trimmedInput === 'custom' || trimmedInput === 'provide') {
                    addUserMessage('Provide custom details');
                    addBotMessage('✅ Great! Let\'s collect the company details manually. What should be the **company name**?');
                    setCurrentStep('company_name');
                } else {
                    addBotMessage('❓ Please choose **auto** to generate all details or **manual** to provide custom details.');
                }
                break;

            case 'company_name':
                if (trimmedInput.length >= 2) {
                    setCompanyData(prev => ({ ...prev, name: input }));
                    addUserMessage(input);
                    addBotMessage('✅ Company name set. What should be the **company domain**? (e.g., company.com, tech.co)');
                    setCurrentStep('domain');
                } else {
                    addBotMessage('❓ Please provide a valid company name (at least 2 characters).');
                }
                break;

            case 'domain':
                if (trimmedInput.includes('.') && trimmedInput.split('.').length === 2) {
                    setCompanyData(prev => ({ ...prev, domain: trimmedInput }));
                    addUserMessage(input);
                    addBotMessage('✅ Domain set. What should be the **company size**? (e.g., 1-10, 11-50, 51-200, 201-500, 501-1000, 1000+)');
                    setCurrentStep('size');
                } else {
                    addBotMessage('❓ Please provide a valid domain (e.g., company.com, tech.co)');
                }
                break;

            case 'size':
                const validSizes = ['1-10', '11-50', '51-200', '201-500', '501-1000', '1000+'];
                if (validSizes.includes(trimmedInput)) {
                    setCompanyData(prev => ({ ...prev, size: trimmedInput }));
                    addUserMessage(input);
                    addBotMessage('✅ Size set. What should be the **founding year**? (e.g., 2015, 2020)');
                    setCurrentStep('founded');
                } else {
                    addBotMessage(`❓ Please choose from: ${validSizes.join(', ')}`);
                }
                break;

            case 'founded':
                const year = parseInt(trimmedInput);
                if (!isNaN(year) && year >= 1900 && year <= 2024) {
                    setCompanyData(prev => ({ ...prev, founded: year.toString() }));
                    addUserMessage(input);
                    addBotMessage('✅ Founded year set. What should be the **revenue**? (e.g., $100M, $50K, $1B)');
                    setCurrentStep('revenue');
                } else {
                    addBotMessage('❓ Please provide a valid year between 1900 and 2024.');
                }
                break;

            case 'revenue':
                if (trimmedInput.match(/^\$[\d.]+[KMGT]?B?$/i)) {
                    setCompanyData(prev => ({ ...prev, revenue: trimmedInput }));
                    addUserMessage(input);
                    addBotMessage('✅ Revenue set. What should be the **company phone number**? (e.g., (212) 555-1234)');
                    setCurrentStep('phone');
                } else {
                    addBotMessage('❓ Please provide revenue in format like: $100M, $50K, $1B');
                }
                break;

            case 'phone':
                // Simple phone validation - should look like US phone number
                if (trimmedInput.match(/^\(\d{3}\)\s*\d{3}[-\s]?\d{4}$/) || trimmedInput.match(/^\d{3}[-\s]?\d{3}[-\s]?\d{4}$/)) {
                    setCompanyData(prev => ({ ...prev, phone: input }));
                    addUserMessage(input);
                    addBotMessage('✅ Phone set. What should be the **company address**? (e.g., 123 Main St, New York, NY 10001)');
                    setCurrentStep('address');
                } else {
                    addBotMessage('❓ Please provide a valid phone number (e.g., (212) 555-1234 or 212-555-1234)');
                }
                break;

            case 'address':
                if (trimmedInput.length >= 10) {
                    const addressObj = { full_address: input };
                    console.log('Setting custom address:', addressObj);
                    console.log('Current companyData before setting address:', companyData);
                    
                    // Update state AND pass address directly to generateCompany
                    setCompanyData(prev => ({ ...prev, address: addressObj }));
                    addUserMessage(input);
                    addBotMessage('✅ Address set. Let me create the company with your custom details...');
                    
                    // Pass the address directly to avoid state timing issues
                    generateCompany(addressObj);
                } else {
                    addBotMessage('❓ Please provide a complete address (e.g., 123 Main St, New York, NY 10001)');
                }
                break;

            default:
                break;
        }
    };

    const generateCompany = async (manualAddress = null) => {
        setIsTyping(true);
        try {
            let company;
            
            // If we have custom data, use it; otherwise generate automatically
            if (companyData.name && companyData.domain) {
                console.log('=== MANUAL MODE DETECTED ===');
                console.log('Custom company data before generation:', companyData);
                console.log('Manual address passed:', manualAddress);
                
                company = {
                    ...companyData,
                    description: `Leading ${companyData.industry} company specializing in innovative solutions`,
                    // Use manual phone/address if provided, otherwise generate
                    phone: companyData.phone || `(${['212', '646', '917', '718', '347'][Math.floor(Math.random() * 5)]}) ${Math.floor(Math.random() * 900) + 200}-${Math.floor(Math.random() * 9000) + 1000}`,
                    // Use the manual address if provided, otherwise check state, otherwise generate
                    address: manualAddress || companyData.address || {
                        street: `${Math.floor(Math.random() * 9999) + 1} Main St`,
                        city: 'San Antonio',
                        state: 'CO',
                        zip: `${Math.floor(Math.random() * 90000) + 10000}`,
                        full_address: ''
                    }
                };
                
                console.log('Company after spreading companyData:', company);
                console.log('Company address after spreading:', company.address);
                
                // If we have a manual address (highest priority), use it
                if (manualAddress) {
                    console.log('✅ USING MANUAL ADDRESS (passed as parameter):', manualAddress);
                    company.address = manualAddress;
                }
                // If address was provided by user in state, use it
                else if (companyData.address && companyData.address.full_address) {
                    console.log('✅ USING CUSTOM ADDRESS (from state):', companyData.address);
                    company.address = companyData.address;
                }
                // If address was auto-generated, create full_address
                else {
                    console.log('❌ GENERATING RANDOM ADDRESS - NO CUSTOM ADDRESS FOUND');
                    company.address.full_address = `${company.address.street}, ${company.address.city}, ${company.address.state} ${company.address.zip}`;
                }
                
                // Ensure all required fields have values
                company.size = company.size || '1-10';
                company.founded = company.founded || '2020';
                company.revenue = company.revenue || '$1M';
                
                console.log('=== FINAL COMPANY OBJECT ===');
                console.log('Final company object:', company);
                console.log('Final address:', company.address);
                console.log('Final address full_address:', company.address.full_address);
            } else {
                // Generate automatically using API
                console.log('=== AUTO MODE - USING API ===');
                const response = await axios.post(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/ai/generate-company`,
                    { industry: companyData.industry },
                    { headers: getAuthHeaders() }
                );
                company = response.data.company;
            }
            
            addBotMessage(`🎉 Company created successfully! Here are the details:\n\n**Name:** ${company.name}\n**Domain:** ${company.domain}\n**Industry:** ${company.industry}\n**Size:** ${company.size}\n**Founded:** ${company.founded}\n**Revenue:** ${company.revenue}\n**Phone:** ${company.phone}\n**Address:** ${company.address.full_address}\n\nWould you like me to create this company in the system?`);
            
            setCompanyData(prev => ({ ...prev, ...company }));
            setCurrentStep('confirm');
            setShowSummary(true);
        } catch (error) {
            console.error('Error generating company:', error);
            addBotMessage('❌ Sorry, I encountered an error while generating the company. Please try again.');
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

    const handleConfirmCompany = async () => {
        setIsTyping(true);
        try {
            console.log('Creating company with data:', companyData);
            
            // Send only the fields that backend expects
            const companyPayload = {
                name: companyData.name,
                description: `${companyData.industry} company - ${companyData.size} employees, founded ${companyData.founded}, revenue ${companyData.revenue}. Contact: ${companyData.phone}, ${companyData.address?.full_address || ''}`,
                logo_url: ""
            };
            
            console.log('Sending payload to backend:', companyPayload);
            
            const response = await axios.post(
                `${process.env.REACT_APP_API_LINKS}/api/v1/companies`,
                companyPayload,
                { headers: getAuthHeaders() }
            );

            addBotMessage('✅ Company successfully created and added to the system! You can now find this company in the Companies page.');
            
            setTimeout(() => {
                onCompanyCreated(response.data);
                handleClose();
            }, 2000);
        } catch (error) {
            console.error('Error creating company:', error);
            console.error('Error response:', error.response?.data);
            const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error';
            addBotMessage(`❌ Sorry, I encountered an error while creating the company in the system: ${errorMessage}`);
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
        setCompanyData({});
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
                        <BusinessIcon sx={{ mr: 1, color: 'primary.main' }} />
                        <Typography variant="h6">Company Creation AI Assistant</Typography>
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
                            Company is ready to be created! Click "Confirm & Create Company" to add it to the system.
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
                            onClick={handleConfirmCompany}
                            disabled={isTyping}
                            startIcon={<SparkleIcon />}
                        >
                            Confirm & Create Company
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

export default CompanyChatBot;
