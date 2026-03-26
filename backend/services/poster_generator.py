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
                'secondary': (231, 76, 60),       # Coral
                'gradient': True,
                'pattern': 'waves'
            },
            'modern_tech': {
                'background': (44, 62, 80),    # Dark blue-gray
                'accent': (52, 152, 219),       # Bright blue
                'text': (255, 255, 255),       # White
                'secondary': (142, 68, 173),      # Purple
                'gradient': False,
                'pattern': 'grid'
            },
            'festive_red': {
                'background': (192, 57, 43),    # Festive red
                'accent': (231, 76, 60),       # Light red
                'text': (255, 255, 255),       # White
                'secondary': (255, 193, 7),       # Gold
                'gradient': True,
                'pattern': 'confetti'
            },
            'nature_green': {
                'background': (34, 139, 34),    # Forest green
                'accent': (76, 175, 80),       # Mint green
                'text': (255, 255, 255),       # White
                'secondary': (255, 235, 59),      # Sunny yellow
                'gradient': True,
                'pattern': 'leaves'
            },
            'elegant_purple': {
                'background': (91, 33, 182),     # Deep purple
                'accent': (186, 85, 211),      # Light purple
                'text': (255, 255, 255),       # White
                'secondary': (255, 184, 108),     # Peach
                'gradient': True,
                'pattern': 'geometric'
            },
            'sunset_orange': {
                'background': (255, 94, 77),     # Sunset orange
                'accent': (255, 154, 0),       # Bright orange
                'text': (255, 255, 255),       # White
                'secondary': (255, 206, 84),     # Yellow
                'gradient': True,
                'pattern': 'rays'
            },
            'elegant_black': {
                'background': (33, 33, 33),    # Dark gray
                'accent': (52, 73, 94),        # Muted blue
                'text': (255, 255, 255),       # White
                'secondary': (156, 163, 175),     # Light gray
                'gradient': False,
                'pattern': 'minimal'
            },
            'professional_green': {
                'background': (39, 174, 96),    # Professional green
                'accent': (46, 204, 113),       # Light green
                'text': (255, 255, 255),       # White
                'secondary': (0, 128, 128),         # Teal
                'gradient': False,
                'pattern': 'corporate'
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
        """Add sophisticated geometric patterns"""
        width, height = self.poster_dimensions
        pattern = theme.get('pattern', 'minimal')
        
        if pattern == 'waves':
            # Wave pattern for ocean theme
            for i in range(5):
                y = height // 4 + i * 40
                amplitude = 20
                for x in range(0, width, 5):
                    wave_y = y + amplitude * 0.1 * (x / 50)
                    draw.ellipse([x, wave_y, x + 3, wave_y + 3], 
                               fill=colors['primary'], outline=None)
        
        elif pattern == 'grid':
            # Grid pattern for tech theme
            for x in range(0, width, 30):
                draw.line([(x, 0), (x, height)], 
                         fill=colors['secondary'], width=1)
            for y in range(0, height, 30):
                draw.line([(0, y), (width, y)], 
                         fill=colors['secondary'], width=1)
        
        elif pattern == 'confetti':
            # Confetti pattern for festive theme
            import random
            for _ in range(15):
                x = random.randint(0, width - 20)
                y = random.randint(0, height - 20)
                size = random.randint(10, 25)
                draw.rectangle([x, y, x + size, y + size], 
                           fill=colors['accent'], outline=colors['primary'])
        
        elif pattern == 'leaves':
            # Leaf pattern for nature theme
            for i in range(8):
                x = 100 + i * 120
                y = 50 + (i % 2) * 80
                # Draw leaf shape
                draw.ellipse([x, y, x + 30, y + 50], 
                           fill=colors['secondary'], outline=colors['primary'])
                draw.ellipse([x + 5, y + 10, x + 25, y + 40], 
                           fill=colors['primary'])
        
        elif pattern == 'geometric':
            # Geometric pattern for elegant theme
            import math
            center_x, center_y = width // 2, height // 2
            for i in range(12):
                angle = (i * 30) * math.pi / 180
                x1 = center_x + 150 * math.cos(angle)
                y1 = center_y + 150 * math.sin(angle)
                x2 = center_x + 100 * math.cos(angle + math.pi)
                y2 = center_y + 100 * math.sin(angle + math.pi)
                draw.line([x1, y1, x2, y2], 
                         fill=colors['secondary'], width=3)
        
        elif pattern == 'rays':
            # Sun rays pattern for sunset theme
            center_x, center_y = width // 2, 100
            for i in range(16):
                angle = (i * 22.5) * math.pi / 180
                x = center_x + 200 * math.cos(angle)
                y = center_y + 200 * math.sin(angle)
                draw.line([center_x, center_y, x, y], 
                         fill=colors['secondary'], width=2)
        
        elif pattern == 'minimal':
            # Minimal pattern - just subtle dots
            for x in range(50, width - 50, 40):
                for y in range(50, height - 50, 40):
                    draw.ellipse([x, y, x + 2, y + 2], 
                               fill=colors['secondary'], outline=None)
        
        elif pattern == 'corporate':
            # Corporate pattern - clean lines
            for i in range(3):
                y = height // 4 + i * height // 4
                draw.line([(50, y), (width - 50, y)], 
                         fill=colors['secondary'], width=2)

    def _add_campaign_text(self, draw: ImageDraw.Draw, campaign_name: str, 
                           call_to_action: str, special_offers: str, theme: Dict):
        """Add campaign text to poster"""
        width, height = self.poster_dimensions
        
        try:
            # Try to load system fonts with fallback
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 72)
                subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 42)
                cta_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
                offers_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 28)
            except:
                try:
                    title_font = ImageFont.truetype("arial.ttf", 72)
                    subtitle_font = ImageFont.truetype("arial.ttf", 42)
                    cta_font = ImageFont.truetype("arial.ttf", 36)
                    offers_font = ImageFont.truetype("arial.ttf", 28)
                except:
                    # Use default fonts
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()
                    cta_font = ImageFont.load_default()
                    offers_font = ImageFont.load_default()
        except Exception as e:
            app_logger.warning(f"Font loading failed: {e}")
            # Use default fonts
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            cta_font = ImageFont.load_default()
            offers_font = ImageFont.load_default()
        
        # Add decorative background text
        draw.text((width // 2, 50), campaign_name.upper(), 
                 font=title_font, fill=theme['text'], anchor='mm')
        
        # Add campaign name with shadow
        title_bbox = draw.textbbox((0, 0), campaign_name, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = height // 3
        
        # Title shadow
        draw.text((title_x + 3, title_y + 3), campaign_name, 
                 font=title_font, fill=(0, 0, 0, 100))
        # Title
        draw.text((title_x, title_y), campaign_name, 
                 font=title_font, fill=theme['text'])
        
        # Add special offers with styling
        if special_offers:
            offers_y = title_y + 120
            offers_bbox = draw.textbbox((0, 0), special_offers, font=offers_font)
            offers_width = offers_bbox[2] - offers_bbox[0]
            offers_x = (width - offers_width) // 2
            
            # Offers background
            draw.rectangle([offers_x - 20, offers_y - 5, offers_x + offers_width + 20, offers_y + 35], 
                       fill=theme.get('secondary', theme['accent']), 
                       outline=theme['text'], width=2)
            # Offers text
            draw.text((offers_x, offers_y), special_offers, 
                     font=offers_font, fill=theme['text'], anchor='mm')
        
        # Add call to action button
        cta_y = height - 120
        cta_bbox = draw.textbbox((0, 0), call_to_action, font=cta_font)
        cta_width = cta_bbox[2] - cta_bbox[0] + 60
        cta_x = (width - cta_width) // 2
        
        # CTA button with gradient effect
        button_height = 50
        for i in range(button_height):
            ratio = i / button_height
            r = int(theme['accent'][0] * (1 - ratio * 0.3) + theme['text'][0] * ratio * 0.3)
            g = int(theme['accent'][1] * (1 - ratio * 0.3) + theme['text'][1] * ratio * 0.3)
            b = int(theme['accent'][2] * (1 - ratio * 0.3) + theme['text'][2] * ratio * 0.3)
            draw.rectangle([cta_x, cta_y + i, cta_x + cta_width, cta_y + i + 1], 
                       fill=(r, g, b))
        
        # CTA button border
        draw.rectangle([cta_x, cta_y, cta_x + cta_width, cta_y + button_height], 
                   fill=None, outline=theme['text'], width=2)
        
        # CTA text
        draw.text((cta_x + cta_width // 2, cta_y + button_height // 2), call_to_action, 
                 font=cta_font, fill=theme['text'], anchor='mm')
        
        # Add decorative elements
        self._add_text_decorations(draw, campaign_name, theme)
        
    def _add_text_decorations(self, draw: ImageDraw.Draw, campaign_name: str, theme: Dict):
        """Add decorative text elements"""
        width, height = self.poster_dimensions
        
        # Add small decorative text in corners
        try:
            font = ImageFont.load_default()
            # Top left corner
            draw.text((20, 20), "✨", font=font, fill=theme['text'])
            # Top right corner  
            draw.text((width - 60, 20), "🚀", font=font, fill=theme['text'])
            # Bottom left corner
            draw.text((20, height - 40), "📈", font=font, fill=theme['text'])
            # Bottom right corner
            draw.text((width - 60, height - 40), "🎯", font=font, fill=theme['text'])
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
