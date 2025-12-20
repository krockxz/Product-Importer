# Product Importer Frontend

A React frontend for managing product imports, built with Vite and TypeScript.

## Features

- **File Upload**: Drag-and-drop CSV file upload with real-time progress tracking
- **Product Management**: List, filter, and delete products with server-side pagination
- **Bulk Operations**: Select and delete multiple products with confirmation modal
- **Webhook Management**: Configure and test webhook endpoints for real-time notifications

## Tech Stack

- React 18 with TypeScript
- Vite for fast development and building
- Tailwind CSS for styling
- Axios for API communication
- Lucide React for icons

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Configuration

The frontend connects to the Django backend running on `http://localhost:8000`. Make sure the backend is running before starting the frontend.

## CORS Configuration

The backend has been configured to accept requests from `http://localhost:5173` (Vite's default port). If you're using a different port, update the `CORS_ALLOWED_ORIGINS` setting in the Django settings.