import React from 'react';
import { 
    Box, 
    Typography, 
    Paper, 
    Chip, 
    Avatar, 
    Button,
    Card,
    CardContent,
    Divider,
    IconButton
} from '@mui/material';
import {
    SmartToy as BotIcon,
    Person as UserIcon,
    ContentCopy as CopyIcon,
    OpenInNew as OpenIcon
} from '@mui/icons-material';

const ChatMessage = ({ message, isBot, onSuggestionClick, onActionClick }) => {
    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
    };

    const formatMessage = (text) => {
        // Convert markdown-style formatting to JSX
        const parts = text.split(/(\*\*.*?\*\*)/);
        return parts.map((part, index) => {
            if (part.startsWith('**') && part.endsWith('**')) {
                return (
                    <strong key={index}>
                        {part.slice(2, -2)}
                    </strong>
                );
            }
            // Handle newlines
            return part.split('\n').map((line, lineIndex) => (
                <React.Fragment key={`${index}-${lineIndex}`}>
                    {line}
                    {lineIndex < part.split('\n').length - 1 && <br />}
                </React.Fragment>
            ));
        });
    };

    const renderDataCards = () => {
        if (!message.data) return null;

        const { data } = message;
        
        if (data.leads) {
            return (
                <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                        Recent Leads:
                    </Typography>
                    {data.leads.map((lead, index) => (
                        <Card key={index} sx={{ mb: 1, bgcolor: 'grey.50' }}>
                            <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                    {lead.name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    {lead.email || 'No email available'}
                                </Typography>
                            </CardContent>
                        </Card>
                    ))}
                </Box>
            );
        }

        if (data.campaigns) {
            return (
                <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                        Campaigns:
                    </Typography>
                    {data.campaigns.map((campaign, index) => (
                        <Card key={index} sx={{ mb: 1, bgcolor: 'grey.50' }}>
                            <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                        {campaign.name}
                                    </Typography>
                                    <Chip 
                                        label={campaign.status || 'Draft'} 
                                        size="small"
                                        color={campaign.status === 'active' ? 'success' : 'default'}
                                    />
                                </Box>
                            </CardContent>
                        </Card>
                    ))}
                </Box>
            );
        }

        if (data.channels) {
            return (
                <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                        Social Media Channels:
                    </Typography>
                    {data.channels.map((channel, index) => (
                        <Card key={index} sx={{ mb: 1, bgcolor: 'grey.50' }}>
                            <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                        {channel.name}
                                    </Typography>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        {channel.followers && (
                                            <Typography variant="caption" color="text.secondary">
                                                {channel.followers.toLocaleString()} followers
                                            </Typography>
                                        )}
                                        <Chip 
                                            label={channel.connected || channel.active ? 'Connected' : 'Not Connected'} 
                                            size="small"
                                            color={channel.connected || channel.active ? 'success' : 'default'}
                                        />
                                    </Box>
                                </Box>
                            </CardContent>
                        </Card>
                    ))}
                </Box>
            );
        }

        if (data.stats) {
            return (
                <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                        Quick Stats:
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                        <Card sx={{ flex: 1, minWidth: 120, bgcolor: 'primary.50' }}>
                            <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 }, textAlign: 'center' }}>
                                <Typography variant="h6" color="primary.main" sx={{ fontWeight: 700 }}>
                                    {data.stats.channels || 0}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Channels
                                </Typography>
                            </CardContent>
                        </Card>
                        <Card sx={{ flex: 1, minWidth: 120, bgcolor: 'secondary.50' }}>
                            <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 }, textAlign: 'center' }}>
                                <Typography variant="h6" color="secondary.main" sx={{ fontWeight: 700 }}>
                                    {data.stats.campaigns || 0}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Campaigns
                                </Typography>
                            </CardContent>
                        </Card>
                        <Card sx={{ flex: 1, minWidth: 120, bgcolor: 'success.50' }}>
                            <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 }, textAlign: 'center' }}>
                                <Typography variant="h6" color="success.main" sx={{ fontWeight: 700 }}>
                                    {data.stats.leads || 0}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Leads
                                </Typography>
                            </CardContent>
                        </Card>
                    </Box>
                </Box>
            );
        }

        return null;
    };

    const renderSuggestions = () => {
        if (!message.suggestions || message.suggestions.length === 0) return null;

        return (
            <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                    Suggested questions:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {message.suggestions.map((suggestion, index) => (
                        <Chip
                            key={index}
                            label={suggestion}
                            variant="outlined"
                            size="small"
                            clickable
                            onClick={() => onSuggestionClick(suggestion)}
                            sx={{
                                '&:hover': {
                                    bgcolor: 'primary.50',
                                    borderColor: 'primary.main'
                                }
                            }}
                        />
                    ))}
                </Box>
            </Box>
        );
    };

    const renderForm = () => {
        if (!message.form) return null;

        if (message.form === 'create_lead') {
            return (
                <Card sx={{ mt: 2, bgcolor: 'grey.50' }}>
                    <CardContent>
                        <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
                            Create New Lead
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            Click to open the leads page where you can create a new lead with full form functionality.
                        </Typography>
                        <Button 
                            variant="contained" 
                            size="small"
                            onClick={() => onActionClick('create_lead')}
                            sx={{ mr: 1 }}
                        >
                            Open Leads Page
                        </Button>
                        <Button 
                            variant="outlined" 
                            size="small"
                            onClick={() => onActionClick('cancel')}
                        >
                            Cancel
                        </Button>
                    </CardContent>
                </Card>
            );
        }

        if (message.form === 'create_campaign') {
            return (
                <Card sx={{ mt: 2, bgcolor: 'grey.50' }}>
                    <CardContent>
                        <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
                            🚀 Create New Campaign
                        </Typography>
                        
                        {message.data?.quickCreate && message.data?.chatCreate && (
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2, fontWeight: 500 }}>
                                    Choose how you'd like to create your campaign:
                                </Typography>
                                
                                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                                    <Button 
                                        variant="contained" 
                                        size="small"
                                        onClick={() => onActionClick('create_campaign')}
                                        sx={{ flex: 1 }}
                                    >
                                        📝 {message.data.quickCreate.text}
                                    </Button>
                                    <Button 
                                        variant="outlined" 
                                        size="small"
                                        onClick={() => onActionClick('chat_create_campaign')}
                                        sx={{ flex: 1 }}
                                    >
                                        💬 {message.data.chatCreate.text}
                                    </Button>
                                </Box>
                                
                                <Typography variant="caption" color="text.secondary">
                                    {message.data.quickCreate.description}
                                </Typography>
                                <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                                    {message.data.chatCreate.description}
                                </Typography>
                            </Box>
                        )}
                        
                        <Box sx={{ display: 'flex', gap: 1 }}>
                            <Button 
                                variant="outlined" 
                                size="small"
                                onClick={() => onActionClick('cancel')}
                            >
                                Cancel
                            </Button>
                        </Box>
                    </CardContent>
                </Card>
            );
        }

        if (message.form === 'create_channel') {
            return (
                <Card sx={{ mt: 2, bgcolor: 'grey.50' }}>
                    <CardContent>
                        <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
                            🔗 Connect New Channel
                        </Typography>
                        
                        {message.data?.quickConnect && message.data?.chatConnect && (
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2, fontWeight: 500 }}>
                                    Choose how you'd like to connect your channel:
                                </Typography>
                                
                                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                                    <Button 
                                        variant="contained" 
                                        size="small"
                                        onClick={() => onActionClick('create_channel')}
                                        sx={{ flex: 1 }}
                                    >
                                        🔗 {message.data.quickConnect.text}
                                    </Button>
                                    <Button 
                                        variant="outlined" 
                                        size="small"
                                        onClick={() => onActionClick('chat_create_channel')}
                                        sx={{ flex: 1 }}
                                    >
                                        💬 {message.data.chatConnect.text}
                                    </Button>
                                </Box>
                                
                                <Typography variant="caption" color="text.secondary">
                                    {message.data.quickConnect.description}
                                </Typography>
                                <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                                    {message.data.chatConnect.description}
                                </Typography>
                            </Box>
                        )}
                        
                        <Box sx={{ display: 'flex', gap: 1 }}>
                            <Button 
                                variant="outlined" 
                                size="small"
                                onClick={() => onActionClick('cancel')}
                            >
                                Cancel
                            </Button>
                        </Box>
                    </CardContent>
                </Card>
            );
        }

        if (message.form === 'chat_campaign_form') {
            return (
                <Card sx={{ mt: 2, bgcolor: 'primary.50' }}>
                    <CardContent>
                        <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
                            📝 Create Campaign via Chat
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            Please provide campaign details below:
                        </Typography>
                        
                        <Box sx={{ mt: 2 }}>
                            <Typography variant="subtitle2" color="primary.main" sx={{ mb: 1 }}>
                                Example Response:
                            </Typography>
                            <Typography variant="body2" sx={{ 
                                p: 2, 
                                bgcolor: 'grey.100', 
                                borderRadius: 1,
                                fontFamily: 'monospace',
                                fontSize: '0.8rem'
                            }}>
                                "Create campaign called 'Summer Sale' targeting young adults with budget $500"
                            </Typography>
                        </Box>
                        
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 2, mb: 1 }}>
                            💡 **Tip:** You can include details like target audience, budget, start date, etc. The more details you provide, the better I can set up your campaign!
                        </Typography>
                        
                        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                            <Button 
                                variant="outlined" 
                                size="small"
                                onClick={() => onActionClick('cancel')}
                            >
                                Cancel
                            </Button>
                        </Box>
                    </CardContent>
                </Card>
            );
        }

        if (message.form === 'chat_channel_form') {
            return (
                <Card sx={{ mt: 2, bgcolor: 'primary.50' }}>
                    <CardContent>
                        <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
                            🔗 Connect Channel via Chat
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            Please provide channel details below:
                        </Typography>
                        
                        <Box sx={{ mt: 2 }}>
                            <Typography variant="subtitle2" color="primary.main" sx={{ mb: 1 }}>
                                Example Response:
                            </Typography>
                            <Typography variant="body2" sx={{ 
                                p: 2, 
                                bgcolor: 'grey.100', 
                                borderRadius: 1,
                                fontFamily: 'monospace',
                                fontSize: '0.8rem'
                            }}>
                                "Connect Facebook page @yourbrand"
                            </Typography>
                        </Box>
                        
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 2, mb: 1 }}>
                            💡 **Tip:** You can include details like platform (Facebook, Instagram, Twitter), account name, and connection preferences. The more details you provide, the better I can assist with the connection!
                        </Typography>
                        
                        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                            <Button 
                                variant="outlined" 
                                size="small"
                                onClick={() => onActionClick('cancel')}
                            >
                                Cancel
                            </Button>
                        </Box>
                    </CardContent>
                </Card>
            );
        }

        return null;
    };

    return (
        <Box
            sx={{
                display: 'flex',
                mb: 2,
                flexDirection: isBot ? 'row' : 'row-reverse',
                alignItems: 'flex-start',
                gap: 1,
            }}
        >
            <Avatar
                sx={{
                    bgcolor: isBot ? 'primary.main' : 'secondary.main',
                    width: 32,
                    height: 32,
                }}
            >
                {isBot ? <BotIcon fontSize="small" /> : <UserIcon fontSize="small" />}
            </Avatar>
            
            <Box sx={{ flex: 1, maxWidth: '70%' }}>
                <Paper
                    sx={{
                        p: 2,
                        bgcolor: isBot ? 'grey.50' : 'primary.main',
                        color: isBot ? 'text.primary' : 'primary.contrastText',
                        borderRadius: 2,
                        position: 'relative',
                        '&:hover .message-actions': {
                            opacity: 1,
                        }
                    }}
                >
                    <Box className="message-actions" sx={{ 
                        position: 'absolute', 
                        top: 4, 
                        right: 4, 
                        opacity: 0, 
                        transition: 'opacity 0.2s',
                        display: 'flex',
                        gap: 0.5
                    }}>
                        <IconButton 
                            size="small" 
                            onClick={() => copyToClipboard(message.text)}
                            sx={{ 
                                color: isBot ? 'text.secondary' : 'primary.contrastText',
                                bgcolor: isBot ? 'grey.200' : 'rgba(255,255,255,0.1)',
                                '&:hover': {
                                    bgcolor: isBot ? 'grey.300' : 'rgba(255,255,255,0.2)',
                                }
                            }}
                        >
                            <CopyIcon fontSize="small" />
                        </IconButton>
                    </Box>
                    
                    <Typography variant="body2" sx={{ lineHeight: 1.5 }}>
                        {formatMessage(message.text)}
                    </Typography>
                    
                    {renderDataCards()}
                    {renderForm()}
                    {renderSuggestions()}
                </Paper>
                
                <Typography 
                    variant="caption" 
                    color="text.secondary" 
                    sx={{ 
                        mt: 0.5, 
                        display: 'block',
                        textAlign: isBot ? 'left' : 'right'
                    }}
                >
                    {message.timestamp}
                </Typography>
            </Box>
        </Box>
    );
};

export default ChatMessage;
