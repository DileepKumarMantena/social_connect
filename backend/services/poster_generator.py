"""
Poster Generation Service
Creates professional campaign posters using design templates and AI
"""

from typing import Dict, Any, Optional
import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from services.logger import app_logger
import io
import base64

class PosterGenerator:
    """Professional poster generation for marketing campaigns"""
    
    def __init__(self):
        self.poster_dimensions = (1080, 1080)  # Square format for social media
        # Correct path from backend to public/posters
        self.poster_dir = "../public/posters"
        self.templates = self._load_templates()
        self.color_schemes = self._load_color_schemes()
        
        # Ensure poster directory exists
        os.makedirs(self.poster_dir, exist_ok=True)

    def _load_templates(self) -> Dict[str, Dict]:
        """Load poster templates"""
        return {
            'blue_ocean': {
                'background': (41, 128, 185),  # Ocean blue
                'accent': (52, 152, 219),       # Sky blue
                'text': (255, 255, 255),       # White
                'gradient': True
            },
            'modern_tech': {
                'background': (44, 62, 80),    # Dark blue-gray
                'accent': (52, 152, 219),       # Bright blue
                'text': (255, 255, 255),       # White
                'gradient': False
            },
            'festive_red': {
                'background': (192, 57, 43),    # Festive red
                'accent': (231, 76, 60),       # Light red
                'text': (255, 255, 255),       # White
                'gradient': True
            },
            'elegant_black': {
                'background': (33, 33, 33),    # Dark gray
                'accent': (52, 73, 94),        # Muted blue
                'text': (255, 255, 255),       # White
                'gradient': False
            },
            'professional_green': {
                'background': (39, 174, 96),    # Professional green
                'accent': (46, 204, 113),       # Light green
                'text': (255, 255, 255),       # White
                'gradient': True
            }
        }

    def _load_color_schemes(self) -> Dict[str, Dict]:
        """Load color schemes for different campaign types"""
        return {
            'sale': {
                'primary': (230, 126, 34),      # Orange
                'secondary': (241, 196, 15),    # Yellow
                'accent': (231, 76, 60)         # Red
            },
            'product_launch': {
                'primary': (52, 152, 219),      # Blue
                'secondary': (155, 89, 182),    # Purple
                'accent': (46, 204, 113)       # Green
            },
            'holiday': {
                'primary': (192, 57, 43),       # Red
                'secondary': (46, 204, 113),    # Green
                'accent': (241, 196, 15)       # Gold
            },
            'brand_awareness': {
                'primary': (52, 73, 94),        # Dark blue
                'secondary': (149, 165, 166),   # Gray
                'accent': (52, 152, 219)       # Light blue
            },
            'lead_generation': {
                'primary': (39, 174, 96),       # Green
                'secondary': (52, 152, 219),    # Blue
                'accent': (241, 196, 15)       # Yellow
            }
        }

    def generate_campaign_poster(self, campaign_data: Dict[str, Any]) -> str:
        """Generate a professional poster for the campaign"""
        
        try:
            # Get campaign details
            campaign_name = campaign_data.get('name', 'Campaign')
            campaign_type = campaign_data.get('type', 'sale')
            visual_theme = campaign_data.get('visual_theme', 'blue_ocean')
            call_to_action = campaign_data.get('call_to_action', 'Learn More')
            special_offers = campaign_data.get('special_offers', '')
            
            # Sanitize campaign name for filename
            safe_name = "".join(c for c in campaign_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_name:
                safe_name = "campaign"
            
            # Create poster image
            poster_image = self._create_poster_image(
                campaign_name, campaign_type, visual_theme, 
                call_to_action, special_offers
            )
            
            # Generate filename
            filename = f"{safe_name.lower().replace(' ', '_')}_2024.png"
            filepath = os.path.join(self.poster_dir, filename)
            
            # Save poster
            poster_image.save(filepath, 'PNG', quality=95)
            
            app_logger.info(f"Poster generated successfully: {filename}")
            return f"/posters/{filename}"
            
        except Exception as e:
            app_logger.error(f"Error generating campaign poster: {e}")
            import traceback
            app_logger.error(f"Poster generation traceback: {traceback.format_exc()}")
            return "/posters/default_campaign.png"

    def _create_poster_image(self, campaign_name: str, campaign_type: str, 
                            visual_theme: str, call_to_action: str, 
                            special_offers: str) -> Image.Image:
        """Create the actual poster image"""
        
        # Create base image
        img = Image.new('RGB', self.poster_dimensions, color='white')
        draw = ImageDraw.Draw(img)
        
        # Get color scheme
        theme = self.templates.get(visual_theme, self.templates['blue_ocean'])
        colors = self.color_schemes.get(campaign_type, self.color_schemes['sale'])
        
        # Create gradient background
        if theme['gradient']:
            self._create_gradient_background(img, draw, theme)
        else:
            self._create_solid_background(img, draw, theme)
        
        # Add design elements
        self._add_geometric_patterns(draw, theme, colors)
        
        # Add text content
        self._add_campaign_text(draw, campaign_name, call_to_action, special_offers, theme)
        
        # Add decorative elements
        self._add_decorative_elements(draw, theme, colors)
        
        # Add frame/border
        self._add_frame(draw, theme)
        
        return img

    def _create_gradient_background(self, img: Image.Image, draw: ImageDraw.Draw, theme: Dict):
        """Create gradient background"""
        width, height = img.size
        base_color = theme['background']
        accent_color = theme['accent']
        
        # Create vertical gradient
        for y in range(height):
            ratio = y / height
            r = int(base_color[0] * (1 - ratio) + accent_color[0] * ratio)
            g = int(base_color[1] * (1 - ratio) + accent_color[1] * ratio)
            b = int(base_color[2] * (1 - ratio) + accent_color[2] * ratio)
            draw.rectangle([(0, y), (width, y)], fill=(r, g, b))

    def _create_solid_background(self, img: Image.Image, draw: ImageDraw.Draw, theme: Dict):
        """Create solid background"""
        width, height = img.size
        draw.rectangle([(0, 0), (width, height)], fill=theme['background'])

    def _add_geometric_patterns(self, draw: ImageDraw.Draw, theme: Dict, colors: Dict):
        """Add geometric patterns for visual interest"""
        width, height = self.poster_dimensions
        
        # Add circles in corners
        circle_positions = [
            (50, 50), (width - 50, 50),
            (50, height - 50), (width - 50, height - 50)
        ]
        
        for x, y in circle_positions:
            # Outer circle
            draw.ellipse([x - 40, y - 40, x + 40, y + 40], 
                        fill=colors['primary'], outline=theme['text'], width=2)
            # Inner circle
            draw.ellipse([x - 20, y - 20, x + 20, y + 20], 
                        fill=colors['accent'])

    def _add_campaign_text(self, draw: ImageDraw.Draw, campaign_name: str, 
                           call_to_action: str, special_offers: str, theme: Dict):
        """Add campaign text to poster"""
        width, height = self.poster_dimensions
        
        try:
            # Try to load system fonts with fallback
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 60)
                subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
                cta_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
            except:
                try:
                    title_font = ImageFont.truetype("arial.ttf", 60)
                    subtitle_font = ImageFont.truetype("arial.ttf", 40)
                    cta_font = ImageFont.truetype("arial.ttf", 36)
                except:
                    # Use default fonts
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()
                    cta_font = ImageFont.load_default()
        except Exception as e:
            app_logger.warning(f"Font loading failed: {e}")
            # Use default fonts
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            cta_font = ImageFont.load_default()
        
        # Calculate text positions
        title_y = height // 4
        subtitle_y = title_y + 100
        cta_y = height - 150
        
        try:
            # Add campaign name (title)
            title_bbox = draw.textbbox((0, 0), campaign_name, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            
            # Add shadow for title
            draw.text((title_x + 2, title_y + 2), campaign_name, 
                     font=title_font, fill=(0, 0, 0, 128))
            # Add title
            draw.text((title_x, title_y), campaign_name, 
                     font=title_font, fill=theme['text'])
            
            # Add special offers (subtitle)
            if special_offers:
                subtitle_bbox = draw.textbbox((0, 0), special_offers, font=subtitle_font)
                subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                subtitle_x = (width - subtitle_width) // 2
                
                draw.text((subtitle_x, subtitle_y), special_offers, 
                         font=subtitle_font, fill=theme['text'])
            
            # Add call to action button
            cta_bbox = draw.textbbox((0, 0), call_to_action, font=cta_font)
            cta_width = cta_bbox[2] - cta_bbox[0] + 40
            cta_height = 60
            cta_x = (width - cta_width) // 2
            cta_y = height - 120
            
            # Draw CTA button background
            draw.rectangle([cta_x, cta_y, cta_x + cta_width, cta_y + cta_height], 
                          fill=theme['accent'], outline=theme['text'], width=2)
            
            # Add CTA text
            cta_text_bbox = draw.textbbox((0, 0), call_to_action, font=cta_font)
            cta_text_width = cta_text_bbox[2] - cta_text_bbox[0]
            cta_text_x = cta_x + (cta_width - cta_text_width) // 2
            cta_text_y = cta_y + (cta_height - 36) // 2
            
            draw.text((cta_text_x, cta_text_y), call_to_action, 
                     font=cta_font, fill=theme['text'])
        except Exception as e:
            app_logger.error(f"Error adding text to poster: {e}")
            # Add simple text as fallback
            try:
                draw.text((50, height // 2), campaign_name, font=title_font, fill=theme['text'])
            except:
                pass

    def _add_decorative_elements(self, draw: ImageDraw.Draw, theme: Dict, colors: Dict):
        """Add decorative elements to poster"""
        width, height = self.poster_dimensions
        
        # Add diagonal lines
        for i in range(5):
            y_start = i * 150
            draw.line([(0, y_start), (200, y_start + 100)], 
                     fill=colors['primary'], width=3)
            draw.line([(width, y_start), (width - 200, y_start + 100)], 
                     fill=colors['primary'], width=3)
        
        # Add small decorative dots
        for i in range(10):
            x = (i + 1) * (width // 11)
            y = height // 2
            draw.ellipse([x - 5, y - 5, x + 5, y + 5], 
                        fill=colors['accent'])

    def _add_frame(self, draw: ImageDraw.Draw, theme: Dict):
        """Add frame/border to poster"""
        width, height = self.poster_dimensions
        frame_width = 10
        
        # Draw frame
        draw.rectangle([frame_width, frame_width, 
                      width - frame_width, height - frame_width], 
                     outline=theme['text'], width=3)

    def create_default_poster(self) -> str:
        """Create a default poster for fallback"""
        try:
            img = Image.new('RGB', self.poster_dimensions, color=(52, 152, 219))
            draw = ImageDraw.Draw(img)
            
            # Add simple text
            try:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
                except:
                    font = ImageFont.truetype("arial.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            text = "Campaign Poster"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (self.poster_dimensions[0] - text_width) // 2
            y = (self.poster_dimensions[1] - text_height) // 2
            
            draw.text((x, y), text, font=font, fill=(255, 255, 255))
            
            # Save default poster
            filepath = os.path.join(self.poster_dir, "default_campaign.png")
            img.save(filepath, 'PNG')
            
            return "/posters/default_campaign.png"
            
        except Exception as e:
            app_logger.error(f"Error creating default poster: {e}")
            return "/posters/default_campaign.png"

    def get_poster_preview_base64(self, poster_path: str) -> Optional[str]:
        """Get poster as base64 string for preview"""
        try:
            full_path = poster_path.replace('/posters/', self.poster_dir + '/')
            if os.path.exists(full_path):
                with open(full_path, 'rb') as img_file:
                    img_data = img_file.read()
                    return base64.b64encode(img_data).decode('utf-8')
            return None
        except Exception as e:
            app_logger.error(f"Error converting poster to base64: {e}")
            return None

# Global instance
poster_generator = PosterGenerator()

# Create default poster on startup
poster_generator.create_default_poster()
