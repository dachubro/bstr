import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
TELEGRAM_BOT_API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
BUNNY_STREAM_API_KEY = os.getenv('BUNNY_STREAM_API_KEY')
STORAGE_ZONE_NAME = os.getenv('STORAGE_ZONE_NAME')

# Function to handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello! Send me the remote video URL and I will upload it to Bunny Stream.")

# Function to handle messages (remote video URL)
def handle_video_url(update: Update, context: CallbackContext) -> None:
    video_url = update.message.text
    update.message.reply_text(f"Got it! Uploading the video from: {video_url} to Bunny Stream...")

    # Download the video from the provided URL
    try:
        video_response = requests.get(video_url, stream=True)
        if video_response.status_code != 200:
            update.message.reply_text("Failed to download the video from the provided URL.")
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
            update.message.reply_text("Video uploaded successfully to Bunny Stream!")
        else:
            update.message.reply_text(f"Failed to upload the video: {upload_response.text}")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")

# Function to handle unknown messages
def handle_unknown(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Sorry, I can only process video URLs.")

# Function to set up the Telegram bot and handlers
def main() -> None:
    # Create the Updater and pass it your bot's token
    updater = Updater(TELEGRAM_BOT_API_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Command handler for /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Message handler to capture any text message (assuming it's a video URL)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_video_url))

    # Handle unknown messages
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_unknown))

    # Start polling updates from Telegram
    updater.start_polling()

    # Run the bot until you send a signal to stop it
    updater.idle()

if __name__ == '__main__':
    main()
