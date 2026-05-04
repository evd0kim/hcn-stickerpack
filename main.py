#!/usr/bin/env python3
"""
Modern entry point for the Bitcoin sticker pack bot.

This replaces the old btc_update.py with a cleaner, modular architecture.
"""

import sys
import argparse
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.app import StickerPackApp


def main():
    """Main entry point with CLI arguments."""
    parser = argparse.ArgumentParser(description="Bitcoin Sticker Pack Bot")
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force update all stickers regardless of schedule"
    )
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Generate test PNG files instead of updating Telegram"
    )
    parser.add_argument(
        "--output-dir", 
        default=".", 
        help="Output directory for test PNG files"
    )
    
    args = parser.parse_args()
    
    try:
        app = StickerPackApp()
        
        if args.test:
            print("Creating test stickers...")
            app.create_test_stickers(args.output_dir)
            print("Test stickers created successfully")
            return 0
        else:
            print("Starting sticker pack update...")
            success = app.update_sticker_pack(force_update=args.force)
            if success:
                print("Sticker pack update completed successfully")
                return 0
            else:
                print("Sticker pack update failed")
                return 1
                
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
