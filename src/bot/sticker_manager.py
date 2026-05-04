#!/usr/bin/env python3
"""Telegram bot sticker pack management."""

import io
import telebot
from time import sleep
from typing import Dict, List, Optional
import cairocffi as cairo

from ..config.settings import TelegramConfig, AppConfig


class StickerPackManager:
    """Manages Telegram sticker pack operations."""
    
    def __init__(self, bot_token: str, user_id: str, pack_name: str):
        self.bot = telebot.TeleBot(bot_token, parse_mode=None, threaded=False)
        self.user_id = user_id
        self.pack_name = pack_name
        
    @classmethod
    def from_config(cls) -> 'StickerPackManager':
        """Create manager from configuration."""
        if not TelegramConfig.validate():
            raise ValueError("Missing required Telegram configuration")
        
        return cls(
            bot_token=TelegramConfig.BOT_TOKEN,
            user_id=TelegramConfig.USER_ID,
            pack_name=TelegramConfig.PACK_NAME
        )
    
    def create_pack(self, png_file: str, name: str) -> bool:
        """Create a new sticker pack."""
        try:
            with open(png_file, "rb") as sticker:
                response = self.bot.create_new_sticker_set(
                    self.user_id,
                    name=f"{name}_by_{self.bot.get_me().username}",
                    title=f"Stickers {name}",
                    png_sticker=sticker,
                    emojis=["😱"],
                    tgs_sticker=None,
                )
                print(f"Created sticker pack: {response}")
                return True
        except Exception as e:
            print(f"Failed to create sticker pack: {e}")
            return False
    
    def get_current_pack_info(self) -> Optional[telebot.types.StickerSet]:
        """Get information about the current sticker pack."""
        try:
            return self.bot.get_sticker_set(self.pack_name)
        except Exception as e:
            print(f"Failed to get pack info: {e}")
            return None
    
    def update_sticker(self, emoji: str, surface: cairo.ImageSurface, 
                      retry_count: int = 3, retry_delay: int = 60) -> bool:
        """Update a single sticker in the pack."""
        # Convert surface to bytes
        sticker_bytes = io.BytesIO()
        surface.write_to_png(sticker_bytes)
        sticker_bytes.seek(0)
        
        # Get current pack
        pack_info = self.get_current_pack_info()
        if not pack_info:
            print(f"Could not get pack info for {self.pack_name}")
            return False
        
        # Remove existing stickers with this emoji
        for sticker in pack_info.stickers:
            if sticker.emoji == emoji:
                try:
                    self.bot.delete_sticker_from_set(sticker.file_id)
                    print(f"Removed old sticker with emoji {emoji}")
                except Exception as e:
                    print(f"Warning: Could not remove old sticker: {e}")
                    if retry_count > 0:
                        sleep(retry_delay)
        
        # Add new sticker
        for attempt in range(retry_count):
            try:
                sticker_bytes.seek(0)  # Reset buffer position
                self.bot.add_sticker_to_set(
                    self.user_id,
                    name=self.pack_name,
                    png_sticker=sticker_bytes,
                    emojis=emoji,
                    tgs_sticker=None,
                )
                print(f"Successfully updated sticker {emoji}")
                return True
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {emoji}: {e}")
                if attempt < retry_count - 1:
                    sleep(retry_delay)
        
        print(f"Failed to update sticker {emoji} after {retry_count} attempts")
        return False
    
    def update_multiple_stickers(self, sticker_data: Dict[str, cairo.ImageSurface]) -> Dict[str, bool]:
        """Update multiple stickers in the pack."""
        results = {}
        
        for emoji, surface in sticker_data.items():
            print(f"Updating sticker: {emoji}")
            results[emoji] = self.update_sticker(emoji, surface)
            
            # Small delay between updates to be nice to the API
            sleep(1)
        
        return results
    
    def send_error_message(self, message: str) -> bool:
        """Send error message to the bot owner."""
        try:
            self.bot.send_message(self.user_id, message)
            return True
        except Exception as e:
            print(f"Failed to send error message: {e}")
            return False
