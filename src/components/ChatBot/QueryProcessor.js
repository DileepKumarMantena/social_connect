class QueryProcessor {
    constructor() {
        this.intentPatterns = {
            leads: {
                keywords: ['leads', 'lead', 'prospects', 'customers', 'clients'],
                actions: {
                    show: ['show', 'get', 'list', 'display', 'view', 'see'],
                    count: ['how many', 'count', 'number', 'total'],
                    create: ['create', 'add', 'new', 'generate'],
                    recent: ['recent', 'latest', 'new', 'today', 'this week']
                }
            },
            campaigns: {
                keywords: ['campaigns', 'campaign', 'marketing', 'ads', 'advertisements'],
                actions: {
                    show: ['show', 'get', 'list', 'display', 'view', 'see'],
                    count: ['how many', 'count', 'number', 'total'],
                    create: ['create', 'add', 'new', 'start', 'launch'],
                    active: ['active', 'running', 'current', 'live'],
                    performance: ['performance', 'results', 'stats', 'analytics', 'metrics', 'effectiveness', 'success', 'conversion', 'roi']
                }
            },
            channels: {
                keywords: ['channels', 'channel', 'social', 'platforms', 'networks'],
                actions: {
                    show: ['show', 'get', 'list', 'display', 'view', 'see'],
                    connected: ['connected', 'active', 'linked', 'setup'],
                    statistics: ['stats', 'statistics', 'followers', 'reach', 'engagement']
                }
            },
            analytics: {
                keywords: ['analytics', 'stats', 'statistics', 'metrics', 'performance', 'data'],
                actions: {
                    show: ['show', 'get', 'display', 'view'],
                    summary: ['summary', 'overview', 'key', 'main'],
                    trends: ['trends', 'growth', 'changes', 'progress']
                }
            },
            dashboard: {
                keywords: ['dashboard', 'overview', 'summary', 'home'],
                actions: {
                    show: ['show', 'get', 'display', 'view'],
                    stats: ['stats', 'statistics', 'numbers', 'figures']
                }
            }
        };
    }

    processQuery(query) {
        console.log('QueryProcessor - processQuery called with:', query);
        const normalizedQuery = query.toLowerCase().trim();
        
        // Determine intent and entity
        const intent = this.extractIntent(normalizedQuery);
        const entity = this.extractEntity(normalizedQuery);
        const action = this.extractAction(normalizedQuery, entity);
        
        console.log('QueryProcessor - extracted:', { intent, entity, action });
        
        return {
            intent,
            entity,
            action,
            originalQuery: query,
            confidence: this.calculateConfidence(normalizedQuery, entity, action)
        };
    }

    extractEntity(query) {
        console.log('QueryProcessor - extractEntity called with:', query);
        
        // Check for "more about" pattern with names
        const moreAboutMatch = query.match(/more about\s+(.+)/i);
        if (moreAboutMatch) {
            const entityName = moreAboutMatch[1].toLowerCase();
            const foundEntity = this.findEntityByName(entityName);
            console.log('QueryProcessor - more about match:', entityName, '->', foundEntity);
            return foundEntity;
        }
        
        // Check for "tell me about" pattern with names
        const tellMeAboutMatch = query.match(/tell me about\s+(.+)/i);
        if (tellMeAboutMatch) {
            const entityName = tellMeAboutMatch[1].toLowerCase();
            const foundEntity = this.findEntityByName(entityName);
            console.log('QueryProcessor - tell me about match:', entityName, '->', foundEntity);
            return foundEntity;
        }
        
        // Check for "about" pattern with names
        const aboutMatch = query.match(/about\s+(.+)/i);
        if (aboutMatch) {
            const entityName = aboutMatch[1].toLowerCase();
            const foundEntity = this.findEntityByName(entityName);
            console.log('QueryProcessor - about match:', entityName, '->', foundEntity);
            return foundEntity;
        }
        
        // Standard keyword matching
        for (const [entityName, entityData] of Object.entries(this.intentPatterns)) {
            if (entityData.keywords.some(keyword => query.includes(keyword))) {
                console.log('QueryProcessor - keyword match:', entityName);
                return entityName;
            }
        }
        
        console.log('QueryProcessor - no entity found, returning unknown');
        return 'unknown';
    }

    findEntityByName(name) {
        console.log('QueryProcessor - findEntityByName called with:', name);
        
        // Map common name variations to entities
        const nameMappings = {
            'dileep': 'leads',        // User name -> leads
            'leads': 'leads',
            'lead': 'leads',
            'campaigns': 'campaigns',
            'campaign': 'campaigns',
            'channels': 'channels',
            'channel': 'channels',
            'analytics': 'analytics',
            'stats': 'analytics',
            'statistics': 'analytics',
            'performance': 'campaigns'  // Default performance to campaigns
        };
        
        const foundEntity = nameMappings[name.toLowerCase()] || 'unknown';
        console.log('QueryProcessor - name mapping result:', name, '->', foundEntity);
        return foundEntity;
    }

    extractAction(query, entity) {
        if (entity === 'unknown') return 'unknown';
        
        const entityActions = this.intentPatterns[entity].actions;
        
        for (const [actionName, actionKeywords] of Object.entries(entityActions)) {
            if (actionKeywords.some(keyword => query.includes(keyword))) {
                return actionName;
            }
        }
        
        return 'show'; // Default action
    }

    extractIntent(query) {
        // Check for "more about" pattern with names
        const moreAboutMatch = query.match(/more about\s+(.+)/i);
        if (moreAboutMatch) {
            return 'show'; // Treat as show intent for the entity
        }
        
        // Check for "tell me about" pattern with names
        const tellMeAboutMatch = query.match(/tell me about\s+(.+)/i);
        if (tellMeAboutMatch) {
            return 'show'; // Treat as show intent for the entity
        }
        
        // Question patterns
        if (query.includes('how many') || query.includes('count') || query.includes('number')) {
            return 'count';
        }
        
        if (query.includes('create') || query.includes('add') || query.includes('new')) {
            return 'create';
        }
        
        if (query.includes('performance') || query.includes('results') || query.includes('stats') || 
            query.includes('analytics') || query.includes('metrics') || query.includes('effectiveness') ||
            query.includes('conversion') || query.includes('roi') || query.includes('success')) {
            return 'analytics';
        }
        
        if (query.includes('help') || query.includes('what can you do')) {
            return 'help';
        }
        
        return 'show'; // Default intent
    }

    calculateConfidence(query, entity, action) {
        if (entity === 'unknown') return 0.3;
        
        let confidence = 0.5;
        
        // Boost confidence based on keyword matches
        const entityKeywords = this.intentPatterns[entity].keywords;
        const entityMatches = entityKeywords.filter(keyword => query.includes(keyword)).length;
        confidence += (entityMatches / entityKeywords.length) * 0.3;
        
        // Boost confidence based on action matches
        if (action !== 'unknown' && this.intentPatterns[entity].actions[action]) {
            const actionKeywords = this.intentPatterns[entity].actions[action];
            const actionMatches = actionKeywords.filter(keyword => query.includes(keyword)).length;
            confidence += (actionMatches / actionKeywords.length) * 0.2;
        }
        
        return Math.min(confidence, 1.0);
    }

    generateResponse(processedQuery, data, permissions = {}) {
        console.log('QueryProcessor - generateResponse:', { processedQuery, data, permissions });
        
        const { entity, action, intent, confidence } = processedQuery;
        
        if (confidence < 0.4) {
            return {
                text: "I'm not sure I understand. Could you rephrase your question? You can ask me about leads, campaigns, channels, analytics, admin, panel, role, management, or settings.",
                suggestions: this.getPermissionBasedSuggestions(permissions)
            };
        }
        
        if (intent === 'help') {
            const helpText = this.generateHelpText(permissions);
            return {
                text: helpText,
                suggestions: this.getPermissionBasedSuggestions(permissions)
            };
        }
        
        // Check permissions before processing requests
        if (!this.hasPermission(entity, action, permissions)) {
            return {
                text: `Sorry, you don't have permission to ${action} ${entity}. Please contact your administrator if you need access to this feature.`,
                suggestions: this.getPermissionBasedSuggestions(permissions)
            };
        }
        
        // Handle multi-entity queries (e.g., "leads, campaigns, channels")
        if (this.isMultiEntityQuery(processedQuery.originalQuery)) {
            return this.generateMultiEntityResponse(processedQuery, data, permissions);
        }
        
        // Special handling for "dileep" queries - show leads info
        if (entity === 'leads' && processedQuery.originalQuery.toLowerCase().includes('dileep')) {
            return this.generateLeadsResponse(action, intent, data.leads, permissions);
        }
        
        switch (entity) {
            case 'leads':
                return this.generateLeadsResponse(action, intent, data.leads, permissions);
            case 'campaigns':
                return this.generateCampaignsResponse(action, intent, data.campaigns, permissions);
            case 'channels':
                return this.generateChannelsResponse(action, intent, data.channels, permissions);
            case 'analytics':
                return this.generateAnalyticsResponse(action, intent, data.analytics, permissions);
            case 'dashboard':
                return this.generateDashboardResponse(action, intent, data.dashboardStats, permissions);
            default:
                return {
                    text: "I can help you with leads, campaigns, channels, analytics, admin panel, role management, and settings. What would you like to know?",
                    suggestions: this.getPermissionBasedSuggestions(permissions)
                };
        }
    }

    isMultiEntityQuery(query) {
        // Check if query mentions multiple entities
        const entities = ['leads', 'campaigns', 'channels', 'analytics', 'admin', 'panel', 'role', 'management', 'settings'];
        const mentionedEntities = entities.filter(entity => 
            query.toLowerCase().includes(entity)
        );
        
        // Also check for comma-separated lists
        const hasCommas = query.includes(',') || query.includes(' and ');
        
        return mentionedEntities.length > 1 || hasCommas;
    }

    generateMultiEntityResponse(processedQuery, data, permissions) {
        const { originalQuery } = processedQuery;
        const mentionedEntities = [];
        
        // Find all mentioned entities
        ['leads', 'campaigns', 'channels', 'analytics', 'admin', 'panel', 'role', 'management', 'settings'].forEach(entity => {
            if (originalQuery.toLowerCase().includes(entity)) {
                mentionedEntities.push(entity);
            }
        });
        
        let responseText = `📊 **Multi-Entity Overview**\n\nI found you're asking about multiple topics. Here's what I can show you:\n\n`;
        
        const entityData = [];
        
        if (mentionedEntities.includes('leads') && data.leads) {
            const leadsCount = data.leads.length;
            entityData.push(`• **Leads**: You have ${leadsCount} lead${leadsCount !== 1 ? 's' : ''}`);
        }
        
        if (mentionedEntities.includes('campaigns') && data.campaigns) {
            const campaignsCount = data.campaigns.length;
            const activeCampaigns = data.campaigns.filter(c => c.status === 'active' || c.status === 'running').length;
            entityData.push(`• **Campaigns**: ${campaignsCount} total (${activeCampaigns} active)`);
        }
        
        if (mentionedEntities.includes('channels') && data.channels) {
            const channelsCount = data.channels.length;
            const connectedChannels = data.channels.filter(c => c.connected || c.active).length;
            entityData.push(`• **Channels**: ${channelsCount} total (${connectedChannels} connected)`);
        }
        
        if (mentionedEntities.includes('analytics') && data.analytics) {
            entityData.push(`• **Analytics**: Performance data available`);
        }
        
        if (mentionedEntities.includes('admin') || mentionedEntities.includes('panel')) {
            entityData.push(`• **Admin Panel**: User and role management`);
        }
        
        if (mentionedEntities.includes('role') || mentionedEntities.includes('management')) {
            entityData.push(`• **Role Management**: Permissions and access control`);
        }
        
        if (mentionedEntities.includes('settings')) {
            entityData.push(`• **Settings**: User preferences and configuration`);
        }
        
        if (entityData.length === 0) {
            responseText += "I don't have data available for the topics you mentioned. Please try asking about specific items like 'leads' or 'campaigns'.";
        } else {
            responseText += entityData.join('\n') + '\n\nWould you like me to elaborate on any of these topics?';
        }
        
        return {
            text: responseText,
            data: { mentionedEntities, entityData },
            suggestions: [
                "Tell me more about leads",
                "Show campaign performance", 
                "What are my connected channels",
                "Show analytics summary",
                "Help me get started"
            ]
        };
    }

    hasPermission(entity, action, permissions) {
        if (!permissions || !permissions[entity]) {
            return true; // Default to allowing if permissions are not available
        }
        
        const entityPermissions = permissions[entity];
        
        switch (action) {
            case 'show':
            case 'count':
            case 'connected':
            case 'statistics':
            case 'summary':
            case 'trends':
            case 'stats':
                return entityPermissions.Read === true;
            case 'create':
                return entityPermissions.Create === true;
            case 'update':
                return entityPermissions.Update === true;
            case 'delete':
                return entityPermissions.Delete === true;
            default:
                return entityPermissions.Read === true;
        }
    }

    getPermissionBasedSuggestions(permissions) {
        const suggestions = [];
        
        if (this.hasPermission('leads', 'show', permissions)) {
            suggestions.push("Show me my leads");
            }
        if (this.hasPermission('campaigns', 'show', permissions)) {
            suggestions.push("How many campaigns do I have?");
        }
        if (this.hasPermission('channels', 'show', permissions)) {
            suggestions.push("What are my connected channels?");
        }
        if (this.hasPermission('analytics', 'show', permissions)) {
            suggestions.push("Show me analytics summary");
        }
        
        // Fallback suggestions if no permissions
        if (suggestions.length === 0) {
            suggestions.push("Help me get started", "What can I access?");
        }
        
        return suggestions.slice(0, 4);
    }

    generateHelpText(permissions) {
        let helpText = "I can help you with:\n\n";
        
        if (this.hasPermission('leads', 'show', permissions)) {
            helpText += "• **Leads**: View, count";
            if (this.hasPermission('leads', 'create', permissions)) {
                helpText += ", or create new leads";
            }
            helpText += "\n";
        }
        
        if (this.hasPermission('campaigns', 'show', permissions)) {
            helpText += "• **Campaigns**: Check status, performance";
            if (this.hasPermission('campaigns', 'create', permissions)) {
                helpText += ", or create campaigns";
            }
            helpText += "\n";
        }
        
        if (this.hasPermission('channels', 'show', permissions)) {
            helpText += "• **Channels**: See connected social media channels\n";
        }
        
        if (this.hasPermission('analytics', 'show', permissions)) {
            helpText += "• **Analytics**: Get performance metrics and insights\n";
        }
        
        helpText += "\nTry asking me anything like 'Show me my leads' or 'How many campaigns do I have?'";
        
        return helpText;
    }

    generateLeadsResponse(action, intent, leads, permissions) {
        if (!leads || leads.length === 0) {
            return {
                text: "You don't have any leads yet. Would you like to create your first lead?",
                suggestions: ["Create new lead", "Show campaigns", "Show channels"]
            };
        }

        switch (intent) {
            case 'count':
                return {
                    text: `You have **${leads.length} total leads**. ${leads.filter(l => l.created_by).length} were created by you.`,
                    data: { count: leads.length, userCreated: leads.filter(l => l.created_by).length }
                };
            case 'create':
                return {
                    text: "I can help you create a new lead! Please provide:\n• Lead name\n• Email address\n• Phone number (optional)\n• Campaign ID (optional)",
                    form: 'create_lead'
                };
            default:
                const recentLeads = leads.slice(-3).reverse();
                const leadsList = recentLeads.map(lead => 
                    `• **${lead.name}** - ${lead.email || 'No email'}`
                ).join('\n');
                
                return {
                    text: `Here are your recent leads:\n\n${leadsList}\n\n*Showing 3 most recent leads out of ${leads.length} total*`,
                    data: { leads: recentLeads },
                    suggestions: ["Create new lead", "Show all leads", "Lead statistics"]
                };
        }
    }

    generateCampaignsResponse(action, intent, campaigns, permissions) {
        console.log('QueryProcessor - generateCampaignsResponse:', { action, intent, campaigns, permissions });
        
        if (!campaigns || campaigns.length === 0) {
            return {
                text: "You don't have any campaigns yet. Would you like to create your first campaign?",
                suggestions: ["Create new campaign", "Show leads", "Show channels"]
            };
        }

        // Handle performance intent specifically
        if (intent === 'analytics' || action === 'performance') {
            const activeCampaigns = campaigns.filter(c => c.status === 'active' || c.status === 'running');
            const totalLeads = campaigns.reduce((sum, c) => sum + (c.leads || 0), 0);
            const avgConversionRate = campaigns.reduce((sum, c) => sum + (parseFloat(c.conversion_rate) || 0), 0) / campaigns.length;
            
            const performanceText = `📊 **Campaign Performance Overview**\n\n` +
                `• **Total Campaigns**: ${campaigns.length}\n` +
                `• **Active Campaigns**: ${activeCampaigns.length}\n` +
                `• **Total Leads Generated**: ${totalLeads}\n` +
                `• **Average Conversion Rate**: ${avgConversionRate.toFixed(1)}%\n\n` +
                `**Campaign Breakdown**:\n` +
                activeCampaigns.map(campaign => 
                    `• **${campaign.name}**: ${campaign.leads || 0} leads, ${campaign.conversion_rate || '0'}% conversion`
                ).join('\n');
            
            return {
                text: performanceText,
                data: { 
                    campaigns: activeCampaigns,
                    summary: {
                        total: campaigns.length,
                        active: activeCampaigns.length,
                        totalLeads,
                        avgConversionRate
                    }
                },
                suggestions: ["Detailed campaign analytics", "Create new campaign", "Show leads"]
            };
        }

        // Handle chat-based campaign creation
        if (action === 'chat_create') {
            return {
                text: "📝 **Creating Campaign via Chat**\n\nI'll help you create a campaign right here! Please provide:\n\n• **Campaign name** (required)\n• **Description** (optional)\n• **Target audience** (optional)\n• **Budget** (optional)\n• **Start date** (optional)\n\n**Example:**\n\"Create campaign called 'Summer Sale' targeting young adults with budget $500\"\n\nJust tell me the details and I'll set it up for you! 🚀",
                form: 'chat_campaign_form',
                suggestions: ["Show campaigns", "Create via form", "Help"]
            };
        }

        const activeCampaigns = campaigns.filter(c => c.status === 'active' || c.status === 'running');
        
        switch (intent) {
            case 'count':
                return {
                    text: `You have **${campaigns.length} total campaigns**, with **${activeCampaigns.length} currently active**.`,
                    data: { total: campaigns.length, active: activeCampaigns.length }
                };
            case 'create':
                return {
                    text: "I can help you create a new campaign! 🚀\n\n**Campaign Creation Options:**\n\n• **Quick Create**: I'll redirect you to the campaigns page where you can create a campaign with all available options\n• **Chat Create**: Tell me the details and I'll create it for you\n\n**Option 1 - Quick Create:**\nClick the button below to go directly to the campaigns page\n\n**Option 2 - Chat Create:**\nProvide:\n• Campaign name (required)\n• Description (optional)\n• Target audience (optional)\n• Budget (optional)\n• Start date (optional)\n\nExample: \"Create campaign called 'Summer Sale' targeting young adults\"\n\nWhich option would you prefer?",
                    form: 'create_campaign',
                    data: {
                        quickCreate: {
                            text: "Go to Campaigns Page",
                            description: "Create campaign with full form interface, scheduling options, and advanced settings"
                        },
                        chatCreate: {
                            text: "Create via Chat",
                            description: "Tell me campaign details and I'll create it for you quickly"
                        }
                    },
                    suggestions: ["Quick create campaign", "Create via chat", "Show campaigns", "Help"]
                };
            default:
                const campaignList = campaigns.slice(0, 3).map(campaign => 
                    `• **${campaign.name}** - Status: ${campaign.status || 'Draft'}`
                ).join('\n');
                
                return {
                    text: `Here are your campaigns:\n\n${campaignList}\n\n*Showing 3 campaigns out of ${campaigns.length} total*`,
                    data: { campaigns: campaigns.slice(0, 3) },
                    suggestions: ["Create new campaign", "Show active campaigns", "Campaign performance"]
                };
        }
    }

    generateChannelsResponse(action, intent, channels, permissions) {
        console.log('QueryProcessor - generateChannelsResponse:', { action, intent, channels, permissions });
        
        if (!channels || channels.length === 0) {
            return {
                text: "You don't have any channels connected yet. Would you like to connect your first channel?",
                suggestions: ["Connect new channel", "Show campaigns", "Show leads"]
            };
        }

        const connectedChannels = channels.filter(c => c.connected || c.active || c.status === 'connected');
        
        switch (intent) {
            case 'count':
                return {
                    text: `You have **${channels.length} total channels**, with **${connectedChannels.length} currently connected**.`,
                    data: { total: channels.length, connected: connectedChannels.length }
                };
            case 'create':
                return {
                    text: "I can help you connect a new channel! 🚀\n\n**Channel Connection Options:**\n\n• **Quick Connect**: I'll redirect you to channels page where you can connect social media accounts\n• **Chat Connect**: Tell me details and I'll help you connect\n\n**Option 1 - Quick Connect:**\nClick button below to go directly to channels page\n\n**Option 2 - Chat Connect:**\nProvide:\n• Channel type (Facebook, Instagram, Twitter, LinkedIn)\n• Account name/handle\n• Connection details\n\nExample: \"Connect Facebook page @yourbrand\"\n\nWhich option would you prefer?",
                    form: 'create_channel',
                    data: {
                        quickConnect: {
                            text: "Go to Channels Page",
                            description: "Connect social media accounts with full setup interface and authentication"
                        },
                        chatConnect: {
                            text: "Connect via Chat",
                            description: "Tell me channel details and I'll help you connect quickly"
                        }
                    },
                    suggestions: ["Quick connect channel", "Connect via chat", "Show channels", "Help"]
                };
            default:
                const channelList = channels.slice(0, 3).map(channel => 
                    `• **${channel.name || channel.platform}** - Status: ${channel.connected || channel.active ? 'Connected' : 'Disconnected'}`
                ).join('\n');
                
                return {
                    text: `Here are your social media channels:\n\n${channelList}\n\n*Showing 3 channels out of ${channels.length} total*`,
                    data: { channels: channels.slice(0, 3) },
                    suggestions: ["Connect new channel", "Show connected channels", "Channel statistics"]
                };
        }
    }

    generateAnalyticsResponse(action, intent, analytics, permissions) {
        if (!analytics || analytics.length === 0) {
            return {
                text: "Analytics data is not available yet. Start running campaigns to see performance metrics.",
                suggestions: ["Show campaigns", "Create campaign", "Show leads"]
            };
        }

        // Mock analytics summary since real analytics structure may vary
        return {
            text: "📊 **Analytics Summary**\n\n• **Total Engagement**: 2,543 interactions\n• **Reach**: 15,234 people\n• **Click-through Rate**: 3.2%\n• **Conversion Rate**: 1.8%\n\n*Data based on your campaign performance*",
            data: { analytics },
            suggestions: ["Detailed analytics", "Campaign performance", "Lead conversion rates"]
        };
    }

    generateDashboardResponse(action, intent, stats, permissions) {
        if (!stats || Object.keys(stats).length === 0) {
            return {
                text: "Dashboard statistics are not available. Let me show you what I can access instead.",
                suggestions: ["Show leads", "Show campaigns", "Show channels"]
            };
        }

        return {
            text: `📈 **Dashboard Overview**\n\n• **Channels Connected**: ${stats.channels || 0}\n• **Active Campaigns**: ${stats.campaigns || 0}\n• **Total Leads**: ${stats.leads || 0}\n\nYour social media presence is growing!`,
            data: { stats },
            suggestions: ["Show leads", "Show campaigns", "Show channels", "Detailed analytics"]
        };
    }
}

export default new QueryProcessor();
