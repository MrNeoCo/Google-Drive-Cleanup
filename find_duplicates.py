# find_duplicates.py

from datetime import datetime
from googleapiclient.errors import HttpError

def find_and_delete_duplicates(service, preview_mode=True):
    """
    Finds and optionally deletes duplicate files from Google Drive.
    Duplicates are detected by md5Checksum (content match) or same name.
    """
    print("\n🔍 Searching for duplicate files in Drive...")

    try:
        files = []
        page_token = None

        # Fetch all files (excluding folders and trashed)
        while True:
            response = service.files().list(
                q="mimeType != 'application/vnd.google-apps.folder' and trashed = false",
                fields="nextPageToken, files(id, name, md5Checksum, size, mimeType, modifiedTime)",
                pageSize=1000,
                pageToken=page_token
            ).execute()

            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break

        print(f"📦 Total files scanned: {len(files)}")

        # Step 1: Group by checksum (content)
        checksum_map = {}
        for f in files:
            checksum = f.get('md5Checksum')
            if not checksum:
                continue  # Google Docs etc. have no md5Checksum
            checksum_map.setdefault(checksum, []).append(f)

        # Step 2: Group by name
        name_map = {}
        for f in files:
            name_map.setdefault(f['name'], []).append(f)

        # Step 3: Collect duplicates
        duplicates = []

        # Content-based duplicates
        for checksum, group in checksum_map.items():
            if len(group) > 1:
                duplicates.extend(group[1:])  # keep one, mark rest as duplicates

        # Name-based duplicates
        for name, group in name_map.items():
            if len(group) > 1:
                duplicates.extend(group[1:])

        # Remove duplicates from duplicates 🙂
        unique_dupes = {d['id']: d for d in duplicates}.values()

        if not unique_dupes:
            print("✅ No duplicates found.")
            return

        print(f"⚠️ Found {len(unique_dupes)} duplicate files.\n")

        for f in unique_dupes:
            print(f"➡️ {f['name']} ({f['id']}) | Modified: {f['modifiedTime']}")
            if preview_mode:
                print("   🔍 [Preview mode — not deleted]")
            else:
                try:
                    # Deletes Permanently skips trash/bin
                    # service.files().delete(fileId=f['id']).execute() 
                    service.files().update(fileId=f['id'], body={'trashed': True}).execute()
                    print("   ❌ Deleted duplicate successfully.")
                except HttpError as e:
                    print(f"   ⚠️ Error deleting {f['name']}: {e}")

        print("\n🎯 Duplicate cleanup complete!")

    except Exception as e:
        print(f"❌ Error finding duplicates: {e}")
        
