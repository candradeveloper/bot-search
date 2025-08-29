import os
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- KONFIGURASI (GANTI DENGAN DATA ANDA) ---
TELEGRAM_BOT_TOKEN = 'TELEGRAM_BOT_TOKEN'
GOOGLE_DRIVE_FOLDER_ID_1 = 'GOOGLE_DRIVE_FOLDER_ID_1'
GOOGLE_DRIVE_FOLDER_ID_2 = 'GOOGLE_DRIVE_FOLDER_ID_2'
GOOGLE_DRIVE_FOLDER_ID_3 ='GOOGLE_DRIVE_FOLDER_ID_3'
FOLDER_IDS = [GOOGLE_DRIVE_FOLDER_ID_1, GOOGLE_DRIVE_FOLDER_ID_2,GOOGLE_DRIVE_FOLDER_ID_3]

# Pastikan nama file JSON ini sesuai dengan nama file Anda
CREDENTIALS_FILE = 'credentials.json' 
# --- AKHIR KONFIGURASI ---


# --- Fungsi Otentikasi Google Drive (tetap sama) ---
def get_gdrive_service():
    """Melakukan otentikasi dengan Google Drive API menggunakan Service Account."""
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    return build('drive', 'v3', credentials=creds)

# --- Fungsi Handler Perintah Telegram ---
def start(update, context):
    """Mengirim pesan sambutan."""
    update.message.reply_text(
        'Halo! Saya bot pencari file (mode tes lokal).\nKirimkan nama file yang ingin dicari.'
    )

def search_files(update, context):
    """Mencari file di Google Drive."""
    query = update.message.text
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text=f'Mencari file: "{query}"...')

    all_found_items = []
    try:
        service = get_gdrive_service()
        
        for folder_id in FOLDER_IDS:
            if not folder_id: continue
            
            search_query = f"name contains '{query}' and '{folder_id}' in parents and trashed=false"
            results = service.files().list(
                q=search_query, pageSize=10, fields="files(name, webViewLink)"
            ).execute()
            all_found_items.extend(results.get('files', []))

        if not all_found_items:
            update.message.reply_text('File tidak ditemukan di kedua folder.')
        else:
            message = 'Berikut adalah file yang berhasil ditemukan:\n\n'
            for item in all_found_items:
                message += f"📄 Nama: {item['name']}\n"
                message += f"🔗 Link: {item['webViewLink']}\n\n"
            update.message.reply_text(message)

    except FileNotFoundError:
        update.message.reply_text(f"Error: File kredensial '{CREDENTIALS_FILE}' tidak ditemukan.")
    except Exception as e:
        print(f"Terjadi error: {e}")
        update.message.reply_text('Maaf, terjadi kesalahan saat mencari file.')

def main():
    """Fungsi utama untuk menjalankan bot."""
    # Membuat objek Updater untuk mengambil update dari Telegram
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)

    # Mendapatkan dispatcher untuk mendaftarkan handler
    dp = updater.dispatcher

    # Mendaftarkan command handler
    dp.add_handler(CommandHandler("start", start))

    # Mendaftarkan message handler untuk mencari file
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, search_files))

    # Memulai bot dengan metode polling
    print("Bot sedang berjalan dalam mode polling...")
    updater.start_polling()

    # Menjaga bot tetap berjalan sampai dihentikan (misal dengan Ctrl+C)
    updater.idle()

if __name__ == '__main__':
    main()
