#!/usr/bin/env python3
"""Main application orchestrator for the sticker pack bot."""

from typing import Dict, Optional
import cairocffi as cairo

from .config.settings import AppConfig
from .data.fetchers import (
    BitcoinFetcher, EthereumFetcher, FearGreedFetcher, 
    HalvingFetcher, ETFFetcher, DataFetchError
)
from .graphics.renderers import (
    BitcoinRenderer, EthereumRenderer, FearGreedRenderer,
    HalvingRenderer, ETFRenderer
)
from .bot.sticker_manager import StickerPackManager
from .utils.timing import should_update_sticker_type


class StickerPackApp:
    """Main application class that orchestrates the sticker pack updates."""
    
    def __init__(self):
        self.config = AppConfig()
        self.sticker_manager = StickerPackManager.from_config()
        self._cached_data = {}
    
    def fetch_all_data(self) -> Dict:
        """Fetch all required data from APIs."""
        data = {}
        
        try:
            print("Fetching Bitcoin data...")
            data['bitcoin'] = BitcoinFetcher.fetch_btc_data()
        except DataFetchError as e:
            print(f"Bitcoin data fetch failed: {e}")
            data['bitcoin'] = None
        
        try:
            print("Fetching Ethereum data...")
            data['ethereum'] = EthereumFetcher.fetch_eth_data()
        except DataFetchError as e:
            print(f"Ethereum data fetch failed: {e}")
            data['ethereum'] = None
        
        try:
            print("Fetching Fear & Greed data...")
            data['fear_greed'] = FearGreedFetcher.fetch_fear_greed_data()
        except DataFetchError as e:
            print(f"Fear & Greed data fetch failed: {e}")
            data['fear_greed'] = None
        
        try:
            print("Fetching halving data...")
            data['halving'] = HalvingFetcher.fetch_halving_data()
        except DataFetchError as e:
            print(f"Halving data fetch failed: {e}")
            data['halving'] = None
        
        try:
            print("Fetching ETF data...")
            data['etf'] = ETFFetcher.fetch_etf_data()
        except DataFetchError as e:
            print(f"ETF data fetch failed: {e}")
            data['etf'] = None
        
        self._cached_data = data
        return data
    
    def render_stickers(self, data: Dict) -> Dict[str, cairo.ImageSurface]:
        """Render all sticker surfaces from the fetched data."""
        stickers = {}
        
        # Bitcoin sticker
        if data.get('bitcoin'):
            print("Rendering Bitcoin sticker...")
            stickers['💸'] = BitcoinRenderer.render(data['bitcoin'])
        
        # Ethereum sticker  
        if data.get('ethereum'):
            print("Rendering Ethereum sticker...")
            stickers['💩'] = EthereumRenderer.render(data['ethereum'])
        
        # Fear & Greed stickers
        if data.get('fear_greed'):
            print("Rendering Fear & Greed stickers...")
            stickers['😱'] = FearGreedRenderer.render_regular(data['fear_greed'])
            stickers['🤡'] = FearGreedRenderer.render_troll(data['fear_greed'])
        
        # Halving sticker
        if data.get('halving'):
            print("Rendering halving sticker...")
            stickers['⛓'] = HalvingRenderer.render(data['halving'])
        
        # ETF sticker
        if data.get('etf') and data['etf']:
            print("Rendering ETF sticker...")
            stickers['🏦'] = ETFRenderer.render(data['etf'])
        
        return stickers
    
    def filter_stickers_by_schedule(self, stickers: Dict[str, cairo.ImageSurface]) -> Dict[str, cairo.ImageSurface]:
        """Filter stickers based on posting schedule."""
        emoji_to_type = {
            '💸': 'btc',
            '💩': 'eth', 
            '🏦': 'etf',
            '😱': 'fear',
            '🤡': 'fear_troll',
            '⛓': 'halving',
        }
        
        filtered = {}
        for emoji, surface in stickers.items():
            sticker_type = emoji_to_type.get(emoji, 'unknown')
            if should_update_sticker_type(sticker_type):
                filtered[emoji] = surface
                print(f"Scheduled to update: {emoji} ({sticker_type})")
            else:
                print(f"Skipping (not scheduled): {emoji} ({sticker_type})")
        
        return filtered
    
    def update_sticker_pack(self, force_update: bool = False) -> bool:
        """Main method to update the sticker pack."""
        try:
            # Fetch all data
            data = self.fetch_all_data()
            
            # Render stickers
            stickers = self.render_stickers(data)
            
            if not stickers:
                print("No stickers were rendered successfully")
                return False
            
            # Filter by schedule unless forced
            if not force_update:
                stickers = self.filter_stickers_by_schedule(stickers)
            
            if not stickers:
                print("No stickers scheduled for update at this time")
                return True
            
            # Update stickers in Telegram
            print(f"Updating {len(stickers)} stickers...")
            results = self.sticker_manager.update_multiple_stickers(stickers)
            
            # Report results
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            print(f"Update complete: {successful}/{total} stickers updated successfully")
            
            if successful < total:
                failed_stickers = [emoji for emoji, success in results.items() if not success]
                error_msg = f"Failed to update stickers: {', '.join(failed_stickers)}"
                self.sticker_manager.send_error_message(error_msg)
                return False
            
            return True
            
        except Exception as e:
            error_msg = f"Sticker pack update failed with exception: {str(e)}"
            print(error_msg)
            try:
                self.sticker_manager.send_error_message(error_msg)
            except:
                pass  # Don't fail if we can't send error message
            return False
    
    def create_test_stickers(self, output_dir: str = ".") -> None:
        """Create test PNG files for development/debugging."""
        import os
        
        data = self.fetch_all_data()
        stickers = self.render_stickers(data)
        
        for emoji, surface in stickers.items():
            # Map emoji to filename
            filename_map = {
                '💸': 'btc_test.png',
                '💩': 'eth_test.png',
                '🏦': 'etf_test.png', 
                '😱': 'fear_test.png',
                '🤡': 'fear_troll_test.png',
                '⛓': 'halving_test.png',
            }
            
            filename = filename_map.get(emoji, f"sticker_{ord(emoji)}.png")
            filepath = os.path.join(output_dir, filename)
            
            surface.write_to_png(filepath)
            print(f"Saved test sticker: {filepath}")


def main():
    """Main entry point."""
    app = StickerPackApp()
    success = app.update_sticker_pack()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
