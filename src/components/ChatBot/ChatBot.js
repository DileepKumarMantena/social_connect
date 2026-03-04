import React, { useState, useEffect, useRef } from 'react';
import {
    Box,
    Drawer,
    Fab,
    Typography,
    IconButton,
    Paper,
    Divider,
    Avatar,
    useTheme,
    alpha,
    CircularProgress,
    Chip,
    Tooltip
} from '@mui/material';
import {
    Close as CloseIcon,
    SmartToy as BotIcon,
    Minimize as MinimizeIcon,
    Maximize as MaximizeIcon,
    QuestionAnswer as ChatIcon,
    Settings as SettingsIcon
} from '@mui/icons-material';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import ChatAPI from './ChatAPI';
import QueryProcessor from './QueryProcessor';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';

const ChatBot = () => {
    console.log('ChatBot component rendering...');
    const theme = useTheme();
    const { user } = useAuth();
    const navigate = useNavigate();
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [messages, setMessages] = useState([]);
    const [isTyping, setIsTyping] = useState(false);
    const [data, setData] = useState({});
    const [permissions, setPermissions] = useState({});
    const messagesEndRef = useRef(null);

    const defaultSuggestions = useMemo(() => [
        "Show me my leads",
        "How many campaigns do I have?",
        "What are my connected channels?",
        "Show me analytics summary"
    ], []);

    const contextualSuggestions = [
        "Create new lead",
        "View campaign performance",
        "Check channel statistics",
        "Help me get started"
    ];

    useEffect(() => {
        if (isOpen && messages.length === 0) {
            // Fetch user permissions first
            fetchUserPermissions();
            
            // Send welcome message
            const welcomeMessage = {
                id: Date.now(),
                text: `Hi ${user?.username || 'there'}! 👋 I'm your AI assistant for SocialConnect. I can help you with:\n\n• **Leads**: View, count, or create new leads\n• **Campaigns**: Check status, performance, or create campaigns\n• **Channels**: See connected social media channels\n• **Analytics**: Get performance metrics and insights\n\nWhat would you like to know today?`,
                isBot: true,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                suggestions: defaultSuggestions
            };
            setMessages([welcomeMessage]);
        }
    }, [isOpen, messages.length, user?.username, defaultSuggestions]);

    const fetchUserPermissions = async () => {
        try {
            const userPermissions = await ChatAPI.getUserPermissions();
            setPermissions(userPermissions);
        } catch (error) {
            console.error('Error fetching user permissions:', error);
        }
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const toggleChat = () => {
        console.log('toggleChat called, isOpen:', isOpen);
        setIsOpen(!isOpen);
        if (!isOpen) {
            setIsMinimized(false);
        }
    };

    const toggleMinimize = () => {
        setIsMinimized(!isMinimized);
    };

    const fetchData = async () => {
        try {
            const [leads, campaigns, channels, analytics, dashboardStats] = await Promise.all([
                ChatAPI.fetchLeads(),
                ChatAPI.fetchCampaigns(),
                ChatAPI.fetchChannels(),
                ChatAPI.fetchAnalytics(),
                ChatAPI.fetchDashboardStats()
            ]);

            const fetchedData = {
                leads,
                campaigns,
                channels,
                analytics,
                dashboardStats
            };
            
            setData(fetchedData);
            return fetchedData;
        } catch (error) {
            console.error('Error fetching data:', error);
            return {
                leads: [],
                campaigns: [],
                channels: [],
                analytics: [],
                dashboardStats: {}
            };
        }
    };

    const processMessage = async (userMessage) => {
        setIsTyping(true);
        
        try {
            // Fetch latest data and permissions
            const fetchedData = await fetchData();
            
            // Process the query
            const processedQuery = QueryProcessor.processQuery(userMessage);
            
            // Generate response with permissions and fresh data
            const response = QueryProcessor.generateResponse(processedQuery, fetchedData, permissions);
            
            // Add bot response
            const botMessage = {
                id: Date.now(),
                text: response.text,
                isBot: true,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                suggestions: response.suggestions || [],
                data: response.data || null,
                form: response.form || null
            };
            
            setTimeout(() => {
                setMessages(prev => [...prev, botMessage]);
                setIsTyping(false);
            }, 1000);
        } catch (error) {
            console.error('Error processing message:', error);
            
            const errorMessage = {
                id: Date.now(),
                text: "Sorry, I encountered an error while processing your request. Please try again or contact support if the issue persists.",
                isBot: true,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                suggestions: defaultSuggestions
            };
            
            setTimeout(() => {
                setMessages(prev => [...prev, errorMessage]);
                setIsTyping(false);
            }, 1000);
        }
    };

    const handleSendMessage = async (message) => {
        const userMessage = {
            id: Date.now(),
            text: message,
            isBot: false,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        
        setMessages(prev => [...prev, userMessage]);
        await processMessage(message);
    };

    const handleSuggestionClick = (suggestion) => {
        handleSendMessage(suggestion);
    };

    const handleActionClick = (action) => {
        console.log('handleActionClick called with action:', action);
        switch (action) {
            case 'create_lead':
                // Navigate to leads page with creation mode
                console.log('Navigating to leads page...');
                navigate('/leads');
                break;
            case 'create_campaign':
            case 'chat_create_campaign':
                // Navigate to campaigns page with creation mode
                console.log('Navigating to campaigns page...');
                navigate('/campaigns');
                break;
            case 'create_channel':
            case 'chat_create_channel':
                // Navigate to channels page with creation mode
                console.log('Navigating to channels page...');
                navigate('/channels');
                break;
            case 'cancel':
                // Add cancellation message
                const cancelMessage = {
                    id: Date.now(),
                    text: "No problem! Let me know if you need anything else.",
                    isBot: true,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    suggestions: defaultSuggestions
                };
                setMessages(prev => [...prev, cancelMessage]);
                break;
            default:
                break;
        }
    };

    const handleChatCampaignCreation = async (campaignDetails) => {
        try {
            setIsTyping(true);
            
            // Create campaign via API
            const response = await ChatAPI.createCampaign({
                name: campaignDetails.name,
                description: campaignDetails.description || '',
                target_audience: campaignDetails.targetAudience || '',
                budget: campaignDetails.budget || '',
                start_date: campaignDetails.startDate || ''
            });
            
            if (response.success) {
                const successMessage = {
                    id: Date.now(),
                    text: `✅ **Campaign Created Successfully!**\n\n📝 **${campaignDetails.name}** has been created and is now ready to launch.\n\nYou can view and manage your campaign in the Campaigns page.`,
                    isBot: true,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    suggestions: ["View campaigns", "Create another campaign", "Campaign performance"]
                };
                setMessages(prev => [...prev, successMessage]);
            } else {
                const errorMessage = {
                    id: Date.now(),
                    text: `❌ **Failed to Create Campaign**\n\nSorry, I encountered an error while creating "${campaignDetails.name}". Please try again or check your permissions.\n\nError: ${response.message || 'Unknown error'}`,
                    isBot: true,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    suggestions: ["Try again", "Create via form", "Help"]
                };
                setMessages(prev => [...prev, errorMessage]);
            }
        } catch (error) {
            const errorMessage = {
                id: Date.now(),
                text: `❌ **Failed to Create Campaign**\n\nSorry, I encountered an error while creating "${campaignDetails.name}". Please try again later.`,
                isBot: true,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                suggestions: ["Try again", "Create via form", "Help"]
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsTyping(false);
        }
    };

    const clearChat = () => {
        setMessages([]);
        setData({});
    };

    const getUnreadCount = () => {
        return messages.filter(m => m.isBot && !m.read).length;
    };

    return (
        <>
            {/* Floating Action Button */}
            {!isOpen && (
                <Tooltip title="AI Assistant" placement="left">
                    <Fab
                        color="primary"
                        aria-label="chat"
                        onClick={toggleChat}
                        sx={{
                            position: 'fixed',
                            bottom: 24,
                            right: 24,
                            zIndex: 9999,
                            background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                            '&:hover': {
                                background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.secondary.dark} 100%)`,
                            }
                        }}
                    >
                        {getUnreadCount() > 0 ? (
                            <Box sx={{ position: 'relative' }}>
                                <ChatIcon />
                                <Box
                                    sx={{
                                        position: 'absolute',
                                        top: -6,
                                        right: -6,
                                        bgcolor: 'error.main',
                                        color: 'white',
                                        borderRadius: '50%',
                                        width: 18,
                                        height: 18,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: '0.6rem',
                                        fontWeight: 'bold'
                                    }}
                                >
                                    {getUnreadCount()}
                                </Box>
                            </Box>
                        ) : (
                            <ChatIcon />
                        )}
                    </Fab>
                </Tooltip>
            )}

            {/* Chat Drawer */}
            <Drawer
                anchor="right"
                open={isOpen}
                onClose={toggleChat}
                variant="persistent"
                sx={{
                    '& .MuiDrawer-paper': {
                        width: isMinimized ? 80 : 380,
                        height: '100vh',
                        position: 'fixed',
                        right: 0,
                        top: 0,
                        bgcolor: 'background.default',
                        borderLeft: '1px solid',
                        borderLeftColor: 'divider',
                        zIndex: 999,
                    }
                }}
            >
                <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
                    {/* Header */}
                    <Paper
                        sx={{
                            p: 2,
                            background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                            color: 'primary.contrastText',
                            borderRadius: 0,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between'
                        }}
                    >
                        {!isMinimized && (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                                    <BotIcon />
                                </Avatar>
                                <Box>
                                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                                        AI Assistant
                                    </Typography>
                                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                                        Always here to help
                                    </Typography>
                                </Box>
                            </Box>
                        )}
                        
                        <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton
                                size="small"
                                onClick={toggleMinimize}
                                sx={{ color: 'primary.contrastText' }}
                            >
                                {isMinimized ? <MaximizeIcon /> : <MinimizeIcon />}
                            </IconButton>
                            <IconButton
                                size="small"
                                onClick={toggleChat}
                                sx={{ color: 'primary.contrastText' }}
                            >
                                <CloseIcon />
                            </IconButton>
                        </Box>
                    </Paper>

                    {!isMinimized && (
                        <>
                            {/* Messages Area */}
                            <Box
                                sx={{
                                    flex: 1,
                                    overflow: 'auto',
                                    p: 2,
                                    display: 'flex',
                                    flexDirection: 'column',
                                    gap: 1,
                                    bgcolor: alpha(theme.palette.background.default, 0.5)
                                }}
                            >
                                {messages.map((message) => (
                                    <ChatMessage
                                        key={message.id}
                                        message={message}
                                        isBot={message.isBot}
                                        onSuggestionClick={handleSuggestionClick}
                                        onActionClick={handleActionClick}
                                    />
                                ))}
                                
                                {isTyping && (
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                        <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                                            <BotIcon fontSize="small" />
                                        </Avatar>
                                        <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                <CircularProgress size={16} />
                                                <Typography variant="body2" color="text.secondary">
                                                    Thinking...
                                                </Typography>
                                            </Box>
                                        </Paper>
                                    </Box>
                                )}
                                
                                <div ref={messagesEndRef} />
                            </Box>

                            {/* Input Area */}
                            <Box sx={{ p: 2, borderTop: '1px solid', borderTopColor: 'divider' }}>
                                <ChatInput
                                    onSendMessage={handleSendMessage}
                                    onSuggestionClick={handleSuggestionClick}
                                    disabled={isTyping}
                                    suggestions={messages.length > 1 ? contextualSuggestions : defaultSuggestions}
                                />
                            </Box>
                        </>
                    )}
                </Box>
            </Drawer>
        </>
    );
};

export default ChatBot;
