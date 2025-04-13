import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import Text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
TELEGRAM_BOT_API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
BUNNY_STREAM_API_KEY = os.getenv('BUNNY_STREAM_API_KEY')
STORAGE_ZONE_NAME = os.getenv('STORAGE_ZONE_NAME')

# Function to handle the /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! Send me the remote video URL and I will upload it to Bunny Stream.")

# Function to handle messages (remote video URL)
async def handle_video_url(update: Update, context: CallbackContext) -> None:
    video_url = update.message.text
    await update.message.reply_text(f"Got it! Uploading the video from: {video_url} to Bunny Stream...")

    # Download the video from the provided URL
    try:
        video_response = requests.get(video_url, stream=True)
        if video_response.status_code != 200:
            await update.message.reply_text("Failed to download the video from the provided URL.")
            return

        # Create FormData for Bunny Stream upload
        video_data = video_response.raw
        file_name = video_url.split("/")[-1]

        # Send video data to Bunny Stream
        upload_url = f"https://video.bunnycdn.com/library/{STORAGE_ZONE_NAME}/videos/upload"
        headers = {
            'Authorization': f'Bearer {BUNNY_STREAM_API_KEY}',
        }
        files = {'file': (file_name, video_data)}
        upload_response = requests.post(upload_url, headers=headers, files=files)

        if upload_response.status_code == 200:
            await update.message.reply_text("Video uploaded successfully to Bunny Stream!")
        else:
            await update.message.reply_text(f"Failed to upload the video: {upload_response.text}")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

# Function to handle unknown messages
async def handle_unknown(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Sorry, I can only process video URLs.")

# Function to set up the Telegram bot and handlers
async def main() -> None:
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_BOT_API_TOKEN).build()

    # Command handler for /start
    application.add_handler(CommandHandler("start", start))

    # Message handler to capture any text message (assuming it's a video URL)
    application.add_handler(MessageHandler(Text(), handle_video_url))

    # Handle unknown messages
    application.add_handler(MessageHandler(Text(), handle_unknown))

    # Start polling updates from Telegram
    await application.run_polling()

if __name__ == '__main__':
    # Directly run the async function without creating a new event loop
    import asyncio
    asyncio.create_task(main())
