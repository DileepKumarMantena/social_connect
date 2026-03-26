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
    Download as DownloadIcon
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const CampaignChatBot = ({ open, onClose, onCampaignCreated }) => {
    const { getAuthHeaders } = useAuth();
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [currentStep, setCurrentStep] = useState('welcome');
    const [campaignData, setCampaignData] = useState({});
    const [showSummary, setShowSummary] = useState(false);
    const [posterPreview, setPosterPreview] = useState(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (open) {
            initializeChat();
        }
    }, [open]);

    const initializeChat = () => {
        const welcomeMessage = {
            id: Date.now(),
            type: 'bot',
            content: "👋 Hi! I'm your AI campaign assistant. I'll help you create an amazing marketing campaign! Let's start with some basic details.",
            timestamp: new Date().toISOString()
        };
        setMessages([welcomeMessage]);
        setCurrentStep('campaign_name');
        setCampaignData({});
        setShowSummary(false);
        setPosterPreview(null);
        
        setTimeout(() => {
            askQuestion("What would you like to name your campaign?");
        }, 1000);
    };

    const askQuestion = (question) => {
        const questionMessage = {
            id: Date.now(),
            type: 'bot',
            content: question,
            timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, questionMessage]);
    };

    const addBotMessage = (content, suggestions = []) => {
        const message = {
            id: Date.now(),
            type: 'bot',
            content,
            suggestions,
            timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, message]);
    };

    const addUserMessage = (content) => {
        const message = {
            id: Date.now(),
            type: 'user',
            content,
            timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, message]);
    };

    const processUserInput = async (input) => {
        addUserMessage(input);
        setIsTyping(true);

        // Simulate processing delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        switch (currentStep) {
            case 'campaign_name':
                setCampaignData(prev => ({ ...prev, name: input }));
                setCurrentStep('campaign_type');
                askQuestion("What type of campaign is this?", [
                    "Sale/Promotion",
                    "Product Launch", 
                    "Holiday Special",
                    "Brand Awareness",
                    "Lead Generation"
                ]);
                break;

            case 'campaign_type':
                const typeMap = {
                    'sale/promotion': 'sale',
                    'product launch': 'product_launch',
                    'holiday special': 'holiday',
                    'brand awareness': 'brand_awareness',
                    'lead generation': 'lead_generation'
                };
                const campaignType = typeMap[input.toLowerCase()] || 'sale';
                setCampaignData(prev => ({ ...prev, type: campaignType }));
                setCurrentStep('target_audience');
                askQuestion("Who are you targeting with this campaign?", [
                    "New Customers",
                    "Existing Customers",
                    "All Customers",
                    "Specific Demographics"
                ]);
                break;

            case 'target_audience':
                const audienceMap = {
                    'new customers': 'new_customers',
                    'existing customers': 'existing_customers',
                    'all customers': 'all_customers',
                    'specific demographics': 'specific_demographics'
                };
                const targetAudience = audienceMap[input.toLowerCase()] || 'all_customers';
                setCampaignData(prev => ({ ...prev, target_audience: targetAudience }));
                setCurrentStep('duration');
                askQuestion("How long will this campaign run?", [
                    "1 week",
                    "2 weeks",
                    "1 month",
                    "Custom duration"
                ]);
                break;

            case 'duration':
                const durationMap = {
                    '1 week': 7,
                    '2 weeks': 14,
                    '1 month': 30,
                    'custom duration': 21
                };
                const duration = durationMap[input.toLowerCase()] || 14;
                setCampaignData(prev => ({ ...prev, duration_days: duration }));
                setCurrentStep('budget');
                askQuestion("What's your budget range for this campaign?", [
                    "$500-1000",
                    "$1000-5000",
                    "$5000+",
                    "Limited budget"
                ]);
                break;

            case 'budget':
                setCampaignData(prev => ({ ...prev, budget_range: input }));
                setCurrentStep('platforms');
                askQuestion("Which social media platforms would you like to use?", [
                    "Facebook & Instagram",
                    "All Platforms",
                    "LinkedIn Only",
                    "Twitter Only"
                ]);
                break;

            case 'platforms':
                const platformMap = {
                    'facebook & instagram': ['facebook', 'instagram'],
                    'all platforms': ['facebook', 'instagram', 'linkedin', 'twitter'],
                    'linkedin only': ['linkedin'],
                    'twitter only': ['twitter']
                };
                const platforms = platformMap[input.toLowerCase()] || ['facebook', 'instagram'];
                setCampaignData(prev => ({ ...prev, platforms }));
                setCurrentStep('goal');
                askQuestion("What's the main goal of this campaign?", [
                    "Drive Sales",
                    "Generate Leads",
                    "Increase Engagement",
                    "Build Brand Awareness"
                ]);
                break;

            case 'goal':
                const goalMap = {
                    'drive sales': 'sales',
                    'generate leads': 'leads',
                    'increase engagement': 'engagement',
                    'build brand awareness': 'brand_awareness'
                };
                const goal = goalMap[input.toLowerCase()] || 'sales';
                setCampaignData(prev => ({ ...prev, goal }));
                setCurrentStep('visual_theme');
                askQuestion("What visual theme would you like for your poster?", [
                    "🌊 Blue Ocean (Professional & Clean)",
                    "💻 Modern Tech (Bold & Innovative)", 
                    "🎄 Festive Red (Celebratory & Bright)",
                    "🌿 Nature Green (Fresh & Organic)",
                    "👔 Elegant Purple (Sophisticated & Premium)",
                    "🌅 Sunset Orange (Warm & Energetic)",
                    "⚫ Elegant Black (Minimal & Professional)",
                    "📊 Professional Green (Corporate & Trustworthy)"
                ]);
                break;

            case 'visual_theme':
                const themeMap = {
                    'blue ocean': 'blue_ocean',
                    'modern tech': 'modern_tech',
                    'festive red': 'festive_red',
                    'nature green': 'nature_green',
                    'elegant purple': 'elegant_purple',
                    'sunset orange': 'sunset_orange',
                    'elegant black': 'elegant_black',
                    'professional green': 'professional_green'
                };
                const visualTheme = themeMap[input.toLowerCase()] || 'blue_ocean';
                setCampaignData(prev => ({ ...prev, visual_theme: visualTheme }));
                setCurrentStep('call_to_action');
                askQuestion("What should be the main call to action?", [
                    "Shop Now",
                    "Learn More", 
                    "Sign Up",
                    "Get Started",
                    "Download Now",
                    "Book Now",
                    "Register Today",
                    "Join Us",
                    "Contact Us",
                    "Visit Website",
                    "Get Offer"
                ]);
                break;

            case 'call_to_action':
                setCampaignData(prev => ({ ...prev, call_to_action: input }));
                setCurrentStep('additional_details');
                addBotMessage("Great! Now tell me more about your campaign. You can describe special offers, visual preferences, or any other details you'd like to include.", [
                    "20% OFF everything!",
                    "Buy 1 Get 1 Free",
                    "Limited Time - Don't Miss Out!",
                    "Free Shipping on Orders Over $50",
                    "Early Bird Special - First 50 Get 25% Off",
                    "Custom Offer"
                ], true);
                break;

            case 'additional_details':
                setCampaignData(prev => ({ ...prev, special_offers: input }));
                generateSmartSuggestions();
                break;

            default:
                break;
        }

        setIsTyping(false);
    };

    const generateSmartSuggestions = async () => {
        setIsTyping(true);
        
        // Simulate AI processing
        await new Promise(resolve => setTimeout(resolve, 2000));

        const suggestions = generateCampaignSuggestions(campaignData);
        setCampaignData(prev => ({ ...prev, ...suggestions }));

        addBotMessage("🎉 Based on your inputs, I've generated some smart suggestions for your campaign!");

        setTimeout(() => {
            addBotMessage(`📊 **Campaign Summary:**\n\n**Name:** ${campaignData.name}\n**Type:** ${campaignData.type}\n**Target:** ${campaignData.target_audience}\n**Duration:** ${campaignData.duration_days} days\n**Budget:** ${campaignData.budget_range}\n**Platforms:** ${campaignData.platforms?.join(', ')}\n**Goal:** ${campaignData.goal}\n**Special Offer:** ${campaignData.special_offers}\n\n🎨 **Visual Theme:** ${suggestions.visual_theme}\n📱 **Call to Action:** ${suggestions.call_to_action}\n🏷️ **Suggested Hashtags:** ${suggestions.suggested_hashtags?.join(', ')}\n⏰ **Best Posting Times:** ${suggestions.optimal_posting_times?.join(', ')}`);
            
            setTimeout(() => {
                addBotMessage("I'm also creating a professional poster for your campaign... 🎨");
                generatePosterPreview();
            }, 2000);
        }, 1000);

        setCurrentStep('review');
        setIsTyping(false);
    };

    const generateCampaignSuggestions = (data) => {
        const themes = {
            'sale': 'blue_ocean',
            'product_launch': 'modern_tech',
            'holiday': 'festive_red',
            'brand_awareness': 'elegant_black',
            'lead_generation': 'professional_green'
        };

        const callsToAction = {
            'sales': 'Shop Now',
            'leads': 'Sign Up',
            'engagement': 'Learn More',
            'brand_awareness': 'Discover'
        };

        const hashtags = {
            'sale': ['#Sale', '#SpecialOffer', '#Discount'],
            'product_launch': ['#NewProduct', '#Innovation', '#Launch'],
            'holiday': ['#Holiday', '#Festive', '#Special'],
            'brand_awareness': ['#Brand', '#Discover', '#Story'],
            'lead_generation': ['#Leads', '#Growth', '#Business']
        };

        return {
            visual_theme: themes[data.type] || 'blue_ocean',
            call_to_action: callsToAction[data.goal] || 'Learn More',
            suggested_hashtags: hashtags[data.type] || ['#Campaign', '#Marketing'],
            optimal_posting_times: ['9:00 AM', '6:00 PM'],
            ad_copy_variations: [
                `🔥 ${data.name} is here! ${data.special_offers}. ${callsToAction[data.goal]} →`,
                `✨ Exciting news about ${data.name}! Don't miss out. ${callsToAction[data.goal]}!`,
                `🎯 Amazing opportunity: ${data.name}. ${data.special_offers}. ${callsToAction[data.goal]} now!`
            ]
        };
    };

    const generatePosterPreview = () => {
        // Simulate poster generation
        setTimeout(() => {
            setPosterPreview(`/posters/${campaignData.name?.toLowerCase().replace(/\s+/g, '_')}_2024.png`);
            addBotMessage("🎨 Your professional campaign poster is ready! I'll now create your campaign with all these details.");
            setTimeout(() => {
                setShowSummary(true);
            }, 2000);
        }, 3000);
    };

    const handleSendMessage = () => {
        if (inputValue.trim()) {
            processUserInput(inputValue);
            setInputValue('');
        }
    };

    const handleSuggestionClick = (suggestion) => {
        setInputValue(suggestion);
    };

    const createCampaign = async () => {
        try {
            setIsTyping(true);
            const response = await axios.post(
                `${process.env.REACT_APP_API_LINKS}/api/v1/campaigns/chatbot-create`,
                campaignData,
                { headers: getAuthHeaders() }
            );

            addBotMessage("🎉 Congratulations! Your campaign has been successfully created! You can now view it in your campaigns dashboard.");
            
            setTimeout(() => {
                onCampaignCreated && onCampaignCreated(response.data.campaign);
                handleClose();
            }, 2000);

        } catch (error) {
            console.error('Error creating campaign:', error);
            
            // More detailed error handling
            let errorMessage = "❌ Sorry, I encountered an error creating your campaign. Please try again.";
            
            if (error.response) {
                // Server responded with error status
                if (error.response.status === 403) {
                    errorMessage = "❌ You don't have permission to create campaigns. Please contact your administrator.";
                } else if (error.response.status === 500) {
                    errorMessage = "⚠️ There was a server error, but your campaign might have been created. Please check your campaigns list.";
                } else if (error.response.data && error.response.data.detail) {
                    errorMessage = `❌ ${error.response.data.detail}`;
                }
            } else if (error.request) {
                // Network error
                errorMessage = "⚠️ Network error. Please check your connection and try again.";
            }
            
            addBotMessage(errorMessage);
        } finally {
            setIsTyping(false);
        }
    };

    const handleClose = () => {
        setMessages([]);
        setCampaignData({});
        setCurrentStep('welcome');
        setShowSummary(false);
        setPosterPreview(null);
        onClose();
    };

    const handleDownloadPoster = () => {
        if (posterPreview) {
            const link = document.createElement('a');
            link.href = posterPreview;
            link.download = `${campaignData.name?.replace(/\s+/g, '_') || 'campaign'}_poster.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
            <DialogTitle>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box display="flex" alignItems="center" gap={1}>
                        <SparkleIcon color="primary" />
                        <Typography variant="h6">AI Campaign Assistant</Typography>
                    </Box>
                    <IconButton onClick={handleClose}>
                        <CloseIcon />
                    </IconButton>
                </Box>
            </DialogTitle>
            
            <DialogContent>
                <Box sx={{ height: 500, display: 'flex', flexDirection: 'column' }}>
                    {/* Messages Area */}
                    <Box sx={{ flex: 1, overflow: 'auto', mb: 2, px: 1 }}>
                        {messages.map((message) => (
                            <Box key={message.id} sx={{ mb: 2 }}>
                                <Box display="flex" gap={1} alignItems="flex-start">
                                    {message.type === 'bot' ? (
                                        <BotIcon color="primary" sx={{ fontSize: 24 }} />
                                    ) : (
                                        <PersonIcon sx={{ fontSize: 24, color: 'grey.600' }} />
                                    )}
                                    <Box flex={1}>
                                        <Paper
                                            sx={{
                                                p: 2,
                                                bgcolor: message.type === 'bot' ? 'primary.50' : 'grey.100',
                                                borderRadius: 2
                                            }}
                                        >
                                            <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                                                {message.content}
                                            </Typography>
                                        </Paper>
                                        {message.suggestions && (
                                            <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                                {message.suggestions.map((suggestion, index) => (
                                                    <Chip
                                                        key={index}
                                                        label={suggestion}
                                                        variant="outlined"
                                                        size="small"
                                                        clickable
                                                        onClick={() => handleSuggestionClick(suggestion)}
                                                        sx={{ cursor: 'pointer' }}
                                                    />
                                                ))}
                                            </Box>
                                        )}
                                    </Box>
                                </Box>
                            </Box>
                        ))}
                        
                        {isTyping && (
                            <Box display="flex" gap={1} alignItems="center">
                                <BotIcon color="primary" sx={{ fontSize: 24 }} />
                                <Paper sx={{ p: 2, bgcolor: 'primary.50', borderRadius: 2 }}>
                                    <CircularProgress size={16} />
                                    <Typography variant="body2" sx={{ ml: 1 }}>
                                        Thinking...
                                    </Typography>
                                </Paper>
                            </Box>
                        )}
                        
                        <div ref={messagesEndRef} />
                    </Box>

                    {/* Campaign Summary */}
                    {showSummary && campaignData && (
                        <Alert severity="success" sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" gutterBottom>
                                📋 Campaign Ready to Create!
                            </Typography>
                            <Typography variant="body2">
                                <strong>{campaignData.name}</strong> • {campaignData.type} • {campaignData.duration_days} days
                            </Typography>
                            <Box sx={{ mt: 1 }}>
                                <Button
                                    variant="contained"
                                    size="small"
                                    onClick={createCampaign}
                                    disabled={isTyping}
                                >
                                    Create Campaign
                                </Button>
                            </Box>
                        </Alert>
                    )}

                    {/* Poster Preview */}
                    {posterPreview && (
                        <Box sx={{ mb: 2, textAlign: 'center' }}>
                            <Typography variant="subtitle2" gutterBottom>
                                🎨 Generated Poster Preview
                            </Typography>
                            <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                                <img
                                    src={posterPreview}
                                    alt="Campaign poster preview"
                                    style={{
                                        maxWidth: '100%',
                                        height: 'auto',
                                        maxHeight: '200px',
                                        borderRadius: '8px'
                                    }}
                                    onError={(e) => {
                                        e.target.src = '/posters/default_campaign.png';
                                    }}
                                />
                                <Box mt={1} display="flex" gap={1} justifyContent="center">
                                    <Button
                                        size="small"
                                        variant="outlined"
                                        startIcon={<DownloadIcon />}
                                        onClick={handleDownloadPoster}
                                    >
                                        Download
                                    </Button>
                                </Box>
                                <Box mt={1}>
                                    <Typography variant="caption" color="textSecondary">
                                        {posterPreview}
                                    </Typography>
                                </Box>
                            </Paper>
                        </Box>
                    )}

                    {/* Input Area */}
                    <Box sx={{ borderTop: 1, borderColor: 'divider', pt: 2 }}>
                        <Box display="flex" gap={1}>
                            <TextField
                                fullWidth
                                variant="outlined"
                                placeholder="Type your response..."
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyPress={handleKeyPress}
                                disabled={isTyping || showSummary}
                                size="small"
                            />
                            <IconButton
                                color="primary"
                                onClick={handleSendMessage}
                                disabled={!inputValue.trim() || isTyping || showSummary}
                            >
                                <SendIcon />
                            </IconButton>
                        </Box>
                    </Box>
                </Box>
            </DialogContent>
        </Dialog>
    );
};

export default CampaignChatBot;
