from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from find_duplicates import find_and_delete_duplicates

import os, pickle

# Scope gives full access to manage Drive files
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)
from datetime import datetime, timedelta, timezone


def make_file_look_old(service, file_id):
    """Force a file's modifiedTime to appear 5 months old."""
    from datetime import datetime, timedelta, timezone

    old_date = (datetime.now(timezone.utc) - timedelta(days=150)).isoformat()
    service.files().update(
        fileId=file_id,
        body={'modifiedTime': old_date},
        fields='id, modifiedTime'
    ).execute()
    print(f"🕒 File {file_id} modifiedTime set to {old_date}")


# def cleanup_old_files(service):
#     """
#     Deletes (or trashes) files older than 6 hours from Google Drive.
#     Includes preview mode, error handling, and logging.
#     """

#     print("\n🧹 Starting cleanup of files older than 6 hours...")

#     # ==== SETTINGS ====
#     PREVIEW_MODE = True       # ✅ True = preview only, False = perform delete
#     MOVE_TO_TRASH = True      # ✅ True = move to Trash, False = permanent delete
#     HOURS_OLD = 6
#     # ===================

#     # Calculate cutoff timestamp (6 hours ago from now)
#     cutoff_time = datetime.now(timezone.utc) - timedelta(hours=HOURS_OLD)
#     cutoff_iso = cutoff_time.isoformat()

#     print(f"🕒 Cutoff time: {cutoff_iso}")
#     print(f"👀 Preview mode: {'ON' if PREVIEW_MODE else 'OFF'}")
#     print(f"🗑️ Delete mode: {'Move to Trash' if MOVE_TO_TRASH else 'Permanent delete'}")

#     # Query: all non-folder files older than cutoff and not already trashed
#     query = (
#         f"modifiedTime < '{cutoff_iso}' "
#         f"and mimeType != 'application/vnd.google-apps.folder' "
#         f"and trashed = false"
#     )

#     try:
#         results = service.files().list(
#             q=query,
#             fields="files(id, name, modifiedTime, owners, mimeType)",
#             pageSize=1000
#         ).execute()
#         old_files = results.get('files', [])

#         if not old_files:
#             print("✅ No files older than 6 hours found.")
#             return

#         print(f"🧾 Found {len(old_files)} files older than 6 hours:\n")

#         for file in old_files:
#             file_name = file['name']
#             mod_time = file['modifiedTime']
#             file_id = file['id']

#             print(f"➡️ {file_name} | Last modified: {mod_time}")

#             if PREVIEW_MODE:
#                 print("   🔍 [Preview only — not deleted]")
#                 continue

#             try:
#                 if MOVE_TO_TRASH:
#                     service.files().update(fileId=file_id, body={'trashed': True}).execute()
#                     print(f"   🗑️ Moved to Trash successfully.")
#                 else:
#                     service.files().delete(fileId=file_id).execute()
#                     print(f"   ❌ Permanently deleted.")
#             except Exception as e:
#                 print(f"   ⚠️ Could not delete {file_name}: {e}")

#         print("\n🎯 Cleanup complete!")

#     except Exception as e:
#         print(f"❌ Error during cleanup: {e}")


def cleanup_old_files(service):
    """
    Deletes (or trashes) files older than 4 months from Google Drive.
    Includes preview mode, error handling, and logging.
    """

    print("\n🧹 Starting cleanup of files older than 4 months...")

    # ==== SETTINGS ====
    PREVIEW_MODE = True       # ✅ True = preview only, False = actually delete
    MOVE_TO_TRASH = True      # ✅ True = move to Trash, False = permanent delete
    MONTHS_OLD = 4
    # ===================

    # Calculate cutoff timestamp (4 months ago)
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=MONTHS_OLD * 30)
    cutoff_iso = cutoff_time.isoformat()

    print(f"🕒 Cutoff date: {cutoff_iso}")
    print(f"👀 Preview mode: {'ON' if PREVIEW_MODE else 'OFF'}")
    print(f"🗑️ Delete mode: {'Move to Trash' if MOVE_TO_TRASH else 'Permanent delete'}")

    # Query: all non-folder files older than cutoff and not already trashed
    query = (
        f"modifiedTime < '{cutoff_iso}' "
        f"and mimeType != 'application/vnd.google-apps.folder' "
        f"and trashed = false"
    )

    try:
        results = service.files().list(
            q=query,
            fields="files(id, name, modifiedTime, mimeType)",
            pageSize=1000
        ).execute()

        old_files = results.get('files', [])
        if not old_files:
            print("✅ No files older than 4 months found.")
            return

        print(f"🧾 Found {len(old_files)} files older than 4 months:\n")

        for file in old_files:
            file_name = file['name']
            mod_time = file['modifiedTime']
            file_id = file['id']

            print(f"➡️ {file_name} | Last modified: {mod_time}")

            if PREVIEW_MODE:
                print("   🔍 [Preview only — not deleted]")
                continue

            try:
                if MOVE_TO_TRASH:
                    service.files().update(fileId=file_id, body={'trashed': True}).execute()
                    print(f"   🗑️ Moved to Trash successfully.")
                else:
                    service.files().delete(fileId=file_id).execute()
                    print(f"   ❌ Permanently deleted.")
            except Exception as e:
                print(f"   ⚠️ Could not delete {file_name}: {e}")

        print("\n🎯 Cleanup complete!")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def main():
    service = authenticate()
    print("✅ Authentication successful!")
    # Simple test: list first 10 files
    results = service.files().list(pageSize=100, fields="files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('First 10 files in Drive:')
        for item in items:
            print(f"{item['name']} ({item['id']})")


# Step 2: Upload a file to Drive
    print("\n📤 Uploading test file to Drive...")

    # Local file you want to upload (make sure this exists)
    local_file = 'lorem.pdf'

    # File metadata (name on Drive)
    file_metadata = {'name': 'lorem.pdf'}

    # Upload the file
    # media = MediaFileUpload(local_file, mimetype='text/plain')

    # uploaded_file = service.files().create(
    #     body=file_metadata,
    #     media_body=media,
    #     fields='id, name'
    # ).execute()

    # print(f"✅ File uploaded successfully: {uploaded_file.get('name')} ({uploaded_file.get('id')})")

    # make_file_look_old(service, '1OLmFzZSxp-cKPNcjO2faIkGPMwr0-hzj')

    cleanup_old_files(service)
    find_and_delete_duplicates(service, preview_mode=True)
    # find_and_delete_duplicates(service)
   

if __name__ == '__main__':
  main()


