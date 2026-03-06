import React, { useState, useRef } from 'react';
import {
    Box,
    TextField,
    IconButton,
    Paper,
    Chip,
    Typography
} from '@mui/material';
import {
    Send as SendIcon,
    Mic as MicIcon,
    AttachFile as AttachIcon
} from '@mui/icons-material';

const ChatInput = ({ 
    onSendMessage, 
    onSuggestionClick, 
    onFormSubmit,
    disabled = false,
    suggestions = [],
    placeholder = "Ask me about your leads, campaigns, channels, or analytics..."
}) => {
    const [message, setMessage] = useState('');
    const [isRecording, setIsRecording] = useState(false);
    const inputRef = useRef(null);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim() && !disabled) {
            onSendMessage(message.trim());
            setMessage('');
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleSuggestionClick = (suggestion) => {
        setMessage(suggestion);
        onSuggestionClick(suggestion);
        inputRef.current?.focus();
    };

    const handleVoiceRecord = () => {
        if (!isRecording) {
            setIsRecording(true);
            // Voice recording implementation would go here
            // For now, just simulate recording
            setTimeout(() => {
                setIsRecording(false);
                setMessage("Show me my leads");
            }, 2000);
        } else {
            setIsRecording(false);
        }
    };

    const handleFileAttach = () => {
        // File attachment implementation would go here
        console.log('File attachment clicked');
    };

    return (
        <Box sx={{ position: 'relative' }}>
            {/* Suggestions */}
            {suggestions.length > 0 && (
                <Box sx={{ mb: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {suggestions.slice(0, 3).map((suggestion, index) => (
                        <Chip
                            key={index}
                            label={suggestion}
                            variant="outlined"
                            size="small"
                            clickable
                            onClick={() => handleSuggestionClick(suggestion)}
                            sx={{
                                '&:hover': {
                                    bgcolor: 'primary.50',
                                    borderColor: 'primary.main'
                                }
                            }}
                        />
                    ))}
                </Box>
            )}

            {/* Input Form */}
            <Paper
                component="form"
                onSubmit={handleSubmit}
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    p: 1,
                    bgcolor: 'background.paper',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 2,
                }}
            >
                <TextField
                    inputRef={inputRef}
                    fullWidth
                    multiline
                    maxRows={3}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={placeholder}
                    disabled={disabled}
                    variant="standard"
                    InputProps={{
                        disableUnderline: true,
                        sx: {
                            px: 1,
                            fontSize: '0.875rem',
                        }
                    }}
                    sx={{ flex: 1 }}
                />

                {/* Action Buttons */}
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                    <IconButton
                        size="small"
                        onClick={handleFileAttach}
                        disabled={disabled}
                        sx={{
                            color: 'text.secondary',
                            '&:hover': {
                                bgcolor: 'action.hover',
                            }
                        }}
                    >
                        <AttachIcon fontSize="small" />
                    </IconButton>

                    <IconButton
                        size="small"
                        onClick={handleVoiceRecord}
                        disabled={disabled}
                        sx={{
                            color: isRecording ? 'error.main' : 'text.secondary',
                            bgcolor: isRecording ? 'error.light' : 'transparent',
                            animation: isRecording ? 'pulse 1.5s infinite' : 'none',
                            '&:hover': {
                                bgcolor: isRecording ? 'error.light' : 'action.hover',
                            }
                        }}
                    >
                        <MicIcon fontSize="small" />
                    </IconButton>

                    <IconButton
                        type="submit"
                        size="small"
                        disabled={!message.trim() || disabled}
                        sx={{
                            bgcolor: message.trim() && !disabled ? 'primary.main' : 'action.disabled',
                            color: message.trim() && !disabled ? 'primary.contrastText' : 'text.disabled',
                            '&:hover': {
                                bgcolor: message.trim() && !disabled ? 'primary.dark' : 'action.disabled',
                            }
                        }}
                    >
                        <SendIcon fontSize="small" />
                    </IconButton>
                </Box>
            </Paper>

            {/* Voice Recording Indicator */}
            {isRecording && (
                <Box sx={{ 
                    position: 'absolute', 
                    top: -30, 
                    left: 0,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1
                }}>
                    <Box sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: 'error.main',
                        animation: 'pulse 1s infinite'
                    }} />
                    <Typography variant="caption" color="error.main">
                        Recording...
                    </Typography>
                </Box>
            )}

            {/* CSS for pulse animation */}
            <style jsx>{`
                @keyframes pulse {
                    0% {
                        opacity: 1;
                        transform: scale(1);
                    }
                    50% {
                        opacity: 0.5;
                        transform: scale(1.1);
                    }
                    100% {
                        opacity: 1;
                        transform: scale(1);
                    }
                }
            `}</style>
        </Box>
    );
};

export default ChatInput;
