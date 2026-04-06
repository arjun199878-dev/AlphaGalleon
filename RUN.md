# AlphaGalleon - Deployment Guide

## 1. Prerequisites
-   **Computer & Phone:** Must be on the same WiFi network.
-   **Phone:** Install the "Expo Go" app from App Store (iOS) or Play Store (Android).

## 2. Configure Network
To run on your physical phone, the app needs to talk to your computer's backend. `localhost` won't work on the phone.

1.  **Find your Computer's Local IP:**
    -   **Mac:** System Settings -> Wi-Fi -> Details... -> IP Address (e.g., `192.168.1.5`)
    -   **Windows:** `ipconfig` in terminal -> IPv4 Address.

2.  **Update Frontend Config:**
    -   Open `frontend/src/api/client.js`.
    -   Replace `localhost` with your IP address.
    -   Example: `const BASE_URL = 'http://192.168.1.5:8001';`

## 3. Start the Backend (The Brain)
Open a terminal in the project root:
```bash
cd backend
# Activate virtual environment
source ../venv/bin/activate
# Run server on 0.0.0.0 to allow external access
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 4. Start the Frontend (The Interface)
Open a *new* terminal window:
```bash
cd frontend
npx expo start
```
-   A QR code will appear in the terminal.
-   **Android:** Scan with Expo Go app.
-   **iOS:** Scan with Camera app -> Open in Expo Go.

## Troubleshooting
-   **Network Error?** Ensure firewall allows port 8001.
-   **White Screen?** Check the metro bundler logs in the frontend terminal.
