"""
Campaign Chatbot Service
Handles AI-powered campaign creation with conversation flow and smart suggestions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid
from services.logger import app_logger
from services.mongo_db import mongo_db
from services.util import get_user_from_token
from services.poster_generator import poster_generator

class CampaignChatbot:
    """AI-powered campaign creation assistant"""
    
    def __init__(self):
        self.conversation_steps = [
            'welcome',
            'campaign_name',
            'campaign_type',
            'target_audience',
            'duration',
            'budget',
            'platforms',
            'goal',
            'visual_theme',
            'special_offers',
            'call_to_action',
            'additional_details',
            'poster_generation',
            'campaign_creation'
        ]
        
        self.campaign_types = {
            'sale': {
                'visual_theme': 'blue_ocean',
                'default_hashtags': ['#Sale', '#SpecialOffer', '#Discount', '#Deals'],
                'call_to_action': 'Shop Now',
                'ad_copy_templates': [
                    "🔥 {name} is ON! Get {special_offers}! {cta} →",
                    "☀️ Hot {name} Deals! {special_offers}. Limited time only!",
                    "🛍️ {name} Shopping Spree! {special_offers}!"
                ]
            },
            'product_launch': {
                'visual_theme': 'modern_tech',
                'default_hashtags': ['#NewProduct', '#Innovation', '#Launch', '#Tech'],
                'call_to_action': 'Learn More',
                'ad_copy_templates': [
                    "🚀 Exciting News! {name} is here. Discover the future today!",
                    "✨ Innovation Unveiled! Be the first to experience {name}.",
                    "🎯 Game Changer Alert! Transform your experience with {name}."
                ]
            },
            'holiday': {
                'visual_theme': 'festive_red',
                'default_hashtags': ['#Holiday', '#Festive', '#Special', '#Celebration'],
                'call_to_action': 'Sign Up',
                'ad_copy_templates': [
                    "🎄 {name} Magic! {special_offers}. {cta} now!",
                    "🎅 Festive {name} Special! {special_offers}. Join us!",
                    "🎁 {name} Cheer! {special_offers}. Don't miss out!"
                ]
            },
            'brand_awareness': {
                'visual_theme': 'elegant_black',
                'default_hashtags': ['#Brand', '#Discover', '#Story', '#Identity'],
                'call_to_action': 'Discover',
                'ad_copy_templates': [
                    "✨ Discover {name} - A story worth sharing.",
                    "🌟 {name} - More than just a brand, it's an experience.",
                    "🎯 {name} - Redefining excellence in every way."
                ]
            },
            'lead_generation': {
                'visual_theme': 'professional_green',
                'default_hashtags': ['#Leads', '#Growth', '#Business', '#Success'],
                'call_to_action': 'Sign Up',
                'ad_copy_templates': [
                    "📈 Grow your business with {name}! {special_offers}. {cta}!",
                    "🎯 {name} - Your path to success starts here. {cta} now!",
                    "💼 Transform your business with {name}. {special_offers} inside!"
                ]
            }
        }
        
        self.target_audiences = {
            'new_customers': {
                'optimal_times': ['12:00 PM', '7:00 PM'],
                'content_focus': 'introductory offers and value proposition'
            },
            'existing_customers': {
                'optimal_times': ['9:00 AM', '6:00 PM'],
                'content_focus': 'loyalty rewards and exclusive deals'
            },
            'all_customers': {
                'optimal_times': ['10:00 AM', '2:00 PM', '8:00 PM'],
                'content_focus': 'broad appeal and general promotions'
            },
            'specific_demographics': {
                'optimal_times': ['11:00 AM', '5:00 PM'],
                'content_focus': 'targeted messaging and personalized content'
            }
        }
        
        self.platform_strategies = {
            'facebook': {
                'content_type': 'carousel posts and videos',
                'optimal_length': 'short to medium',
                'engagement_tips': 'use questions and interactive content'
            },
            'instagram': {
                'content_type': 'visual stories and reels',
                'optimal_length': 'visual-first',
                'engagement_tips': 'use high-quality images and trending audio'
            },
            'linkedin': {
                'content_type': 'professional articles and company updates',
                'optimal_length': 'medium to long',
                'engagement_tips': 'focus on value and professional insights'
            },
            'twitter': {
                'content_type': 'quick updates and threads',
                'optimal_length': 'short and punchy',
                'engagement_tips': 'use hashtags and trending topics'
            }
        }

    def process_user_input(self, step: str, user_input: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user input at each conversation step"""
        
        try:
            if step == 'campaign_name':
                campaign_data['name'] = user_input.strip()
                return campaign_data
                
            elif step == 'campaign_type':
                campaign_type = self._map_campaign_type(user_input)
                campaign_data['type'] = campaign_type
                return campaign_data
                
            elif step == 'target_audience':
                audience = self._map_target_audience(user_input)
                campaign_data['target_audience'] = audience
                return campaign_data
                
            elif step == 'duration':
                duration = self._map_duration(user_input)
                campaign_data['duration_days'] = duration
                return campaign_data
                
            elif step == 'budget':
                campaign_data['budget_range'] = user_input.strip()
                return campaign_data
                
            elif step == 'platforms':
                platforms = self._map_platforms(user_input)
                campaign_data['platforms'] = platforms
                return campaign_data
                
            elif step == 'goal':
                goal = self._map_goal(user_input)
                campaign_data['goal'] = goal
                return campaign_data
                
            elif step == 'visual_theme':
                theme = user_input.strip().lower()
                valid_themes = ['blue_ocean', 'modern_tech', 'festive_red', 'nature_green', 
                               'elegant_purple', 'sunset_orange', 'elegant_black', 'professional_green']
                
                if theme in valid_themes:
                    campaign_data['visual_theme'] = theme
                    return campaign_data
                else:
                    return {
                        'error': f'Please choose from: {", ".join(valid_themes)}',
                        'suggestions': valid_themes
                    }
                
            elif step == 'call_to_action':
                cta = user_input.strip()
                valid_ctas = ['Shop Now', 'Learn More', 'Sign Up', 'Get Started', 
                              'Download Now', 'Book Now', 'Register Today', 'Join Us',
                              'Follow Us', 'Contact Us', 'Visit Website', 'Get Offer']
                
                if cta:
                    campaign_data['call_to_action'] = cta
                    return campaign_data
                else:
                    return {
                        'error': f'Please provide a clear call to action. Examples: {", ".join(valid_ctas)}',
                        'suggestions': valid_ctas
                    }
                
            elif step == 'additional_details':
                campaign_data['special_offers'] = user_input.strip()
                return campaign_data
                
            else:
                return campaign_data
                
        except Exception as e:
            app_logger.error(f"Error processing user input for step {step}: {e}")
            return campaign_data

    def generate_smart_suggestions(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered suggestions based on campaign data"""
        
        try:
            campaign_type = campaign_data.get('type', 'sale')
            target_audience = campaign_data.get('target_audience', 'all_customers')
            platforms = campaign_data.get('platforms', ['facebook', 'instagram'])
            goal = campaign_data.get('goal', 'sales')
            
            # Get type-specific configurations
            type_config = self.campaign_types.get(campaign_type, self.campaign_types['sale'])
            audience_config = self.target_audiences.get(target_audience, self.target_audiences['all_customers'])
            
            # Generate visual theme
            visual_theme = type_config['visual_theme']
            
            # Generate call to action
            call_to_action = type_config['call_to_action']
            
            # Generate suggested hashtags
            base_hashtags = type_config['default_hashtags'].copy()
            custom_hashtags = self._generate_custom_hashtags(campaign_data)
            suggested_hashtags = list(set(base_hashtags + custom_hashtags))
            
            # Generate optimal posting times
            optimal_posting_times = audience_config['optimal_times']
            
            # Generate ad copy variations
            ad_copy_variations = []
            for template in type_config['ad_copy_templates']:
                ad_copy = template.format(
                    name=campaign_data.get('name', 'Campaign'),
                    special_offers=campaign_data.get('special_offers', 'Special Offer'),
                    cta=call_to_action
                )
                ad_copy_variations.append(ad_copy)
            
            # Generate platform-specific strategies
            platform_strategies = {}
            for platform in platforms:
                if platform in self.platform_strategies:
                    platform_strategies[platform] = self.platform_strategies[platform]
            
            # Generate poster URL
            poster_url = f"/posters/{campaign_data.get('name', 'campaign').lower().replace(' ', '_')}_2024.png"
            
            return {
                **campaign_data,
                'visual_theme': visual_theme,
                'call_to_action': call_to_action,
                'suggested_hashtags': suggested_hashtags,
                'optimal_posting_times': optimal_posting_times,
                'ad_copy_variations': ad_copy_variations,
                'platform_strategies': platform_strategies,
                'poster_url': poster_url,
                'content_focus': audience_config['content_focus']
            }
            
        except Exception as e:
            app_logger.error(f"Error generating smart suggestions: {e}")
            return campaign_data

    def create_campaign_from_chat(self, campaign_data: Dict[str, Any], user_token: str) -> Dict[str, Any]:
        """Create campaign from chatbot conversation data"""
        
        try:
            # Get user information
            current_user = get_user_from_token(user_token)
            if not current_user:
                raise Exception("Invalid user token")
            
            # Generate smart suggestions
            enhanced_data = self.generate_smart_suggestions(campaign_data)
            
            # Add required fields
            enhanced_data['created_by'] = current_user['username']
            enhanced_data['created_at'] = datetime.utcnow().isoformat()
            enhanced_data['companyid'] = current_user.get('companyid', 0)
            enhanced_data['status'] = 'draft'
            enhanced_data['leads'] = 0
            enhanced_data['conversion_rate'] = 0.0
            
            # Generate unique ID
            enhanced_data['id'] = self._generate_campaign_id()
            
            # Save to database
            if mongo_db.create_campaign(enhanced_data):
                # Generate poster (non-critical)
                try:
                    poster_url = poster_generator.generate_campaign_poster(enhanced_data)
                    enhanced_data['poster_url'] = poster_url
                    app_logger.info(f"Poster generated: {poster_url}")
                except Exception as e:
                    app_logger.warning(f"Failed to generate poster: {e}")
                    # Keep default poster URL
                    enhanced_data['poster_url'] = "/posters/default_campaign.png"
                
                app_logger.info(f"Campaign created via chatbot: {enhanced_data['name']}")
                return {
                    'success': True,
                    'campaign': enhanced_data,
                    'message': 'Campaign created successfully with AI assistance!'
                }
            else:
                raise Exception("Failed to save campaign to database")
                
        except Exception as e:
            app_logger.error(f"Error creating campaign from chat: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create campaign'
            }

    def _map_campaign_type(self, user_input: str) -> str:
        """Map user input to campaign type"""
        input_lower = user_input.lower()
        
        type_mapping = {
            'sale': ['sale', 'promotion', 'discount', 'offer', 'deal'],
            'product_launch': ['product launch', 'launch', 'new product', 'product'],
            'holiday': ['holiday', 'festive', 'christmas', 'thanksgiving', 'seasonal'],
            'brand_awareness': ['brand awareness', 'brand', 'awareness', 'identity'],
            'lead_generation': ['lead generation', 'leads', 'generation', 'business']
        }
        
        for campaign_type, keywords in type_mapping.items():
            if any(keyword in input_lower for keyword in keywords):
                return campaign_type
        
        return 'sale'  # Default

    def _map_target_audience(self, user_input: str) -> str:
        """Map user input to target audience"""
        input_lower = user_input.lower()
        
        audience_mapping = {
            'new_customers': ['new', 'potential', 'prospects'],
            'existing_customers': ['existing', 'current', 'loyal', 'repeat'],
            'all_customers': ['all', 'everyone', 'general'],
            'specific_demographics': ['specific', 'targeted', 'demographic', 'niche']
        }
        
        for audience, keywords in audience_mapping.items():
            if any(keyword in input_lower for keyword in keywords):
                return audience
        
        return 'all_customers'  # Default

    def _map_duration(self, user_input: str) -> int:
        """Map user input to duration in days"""
        input_lower = user_input.lower()
        
        if 'week' in input_lower:
            if '1' in input_lower or 'one' in input_lower:
                return 7
            elif '2' in input_lower or 'two' in input_lower:
                return 14
            elif '3' in input_lower or 'three' in input_lower:
                return 21
            elif '4' in input_lower or 'four' in input_lower:
                return 28
        elif 'month' in input_lower:
            if '1' in input_lower or 'one' in input_lower:
                return 30
            elif '2' in input_lower or 'two' in input_lower:
                return 60
        elif 'day' in input_lower:
            # Extract number of days
            import re
            numbers = re.findall(r'\d+', input_lower)
            if numbers:
                return int(numbers[0])
        
        return 14  # Default to 2 weeks

    def _map_platforms(self, user_input: str) -> List[str]:
        """Map user input to social media platforms"""
        input_lower = user_input.lower()
        platforms = []
        
        platform_mapping = {
            'facebook': ['facebook', 'fb'],
            'instagram': ['instagram', 'ig', 'insta'],
            'linkedin': ['linkedin', 'li'],
            'twitter': ['twitter', 'tweet']
        }
        
        for platform, keywords in platform_mapping.items():
            if any(keyword in input_lower for keyword in keywords):
                platforms.append(platform)
        
        # If no specific platforms mentioned, default to facebook & instagram
        if not platforms:
            platforms = ['facebook', 'instagram']
        
        return platforms

    def _map_goal(self, user_input: str) -> str:
        """Map user input to campaign goal"""
        input_lower = user_input.lower()
        
        goal_mapping = {
            'sales': ['sales', 'sell', 'revenue', 'purchase', 'buy'],
            'leads': ['leads', 'lead generation', 'prospects', 'sign up'],
            'engagement': ['engagement', 'engage', 'interaction', 'likes', 'comments'],
            'brand_awareness': ['brand awareness', 'awareness', 'brand', 'visibility']
        }
        
        for goal, keywords in goal_mapping.items():
            if any(keyword in input_lower for keyword in keywords):
                return goal
        
        return 'sales'  # Default

    def _generate_custom_hashtags(self, campaign_data: Dict[str, Any]) -> List[str]:
        """Generate custom hashtags based on campaign data"""
        hashtags = []
        
        # Add campaign name as hashtag
        name = campaign_data.get('name', '')
        if name:
            clean_name = name.replace(' ', '').replace('&', '').replace('!', '')
            hashtags.append(f"#{clean_name}")
        
        # Add type-specific hashtags
        campaign_type = campaign_data.get('type', '')
        if campaign_type:
            hashtags.append(f"#{campaign_type.replace('_', '').title()}")
        
        # Add year
        current_year = datetime.now().year
        hashtags.append(f"#{current_year}")
        
        return hashtags

    def _generate_campaign_id(self) -> int:
        """Generate unique campaign ID"""
        try:
            # Get existing campaigns to determine next ID
            existing_campaigns = mongo_db.get_campaigns()
            if existing_campaigns:
                max_id = max(campaign.get('id', 0) for campaign in existing_campaigns)
                return max_id + 1
            else:
                return 1
        except:
            return int(uuid.uuid4().hex[:8], 16) % 1000000

# Global instance
campaign_chatbot = CampaignChatbot()
