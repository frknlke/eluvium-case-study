# Eluvium Gmail OAuth App

This is a Next.js application that implements Google OAuth to access user Gmail accounts. The app allows users to authenticate with their Google accounts and provides access tokens that can be used to interact with the Gmail API. It communicates with a backend API to store credentials in a PostgreSQL database.

## Getting Started

### Prerequisites

- Node.js 18.17 or later
- npm or yarn
- Python backend running (see [backend README](../backend/README.md))

### Installation

1. Clone the repository
2. Navigate to the project directory:
   ```
   cd eluvium-case-study/frontend
   ```
3. Install dependencies:
   ```
   npm install
   ```

### Environment Variables

Create a `.env.local` file in the root directory with the following variables:

```
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-should-be-changed

# Google OAuth
GOOGLE_CLIENT_ID=576019191668-4kcfq8ukau22qvghjo2223t3pbjo904u.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Running the Application

```
npm run dev
```

This will start the development server at [http://localhost:3000](http://localhost:3000).

## Features

- Google OAuth authentication with pre-authentication form
- Collection of additional information (company ID, sync method)
- Sends OAuth credentials to the backend API for storage
- Dashboard to display user information, tokens, and connected mailboxes
- Protected routes requiring authentication

## Architecture

This frontend application is part of a client-server architecture:

- **Frontend (this application)**: Handles user interface, OAuth flow, and communication with the backend
- **Backend**: Provides API endpoints and handles database operations

## Application Flow

1. User fills out a form with company ID and sync method
2. User authenticates with Google OAuth
3. After successful authentication, the application sends the OAuth credentials to the backend API
4. User is redirected to the dashboard where they can see their connected mailboxes

## Important Notes

- The redirect URI in your Google Cloud Console should match the callback URL used by NextAuth.js.
- For security reasons, tokens should not be displayed in a production environment. This is for demonstration purposes only.
- Make sure the backend API is running before using the frontend application.

## Technology Stack

- Next.js 14
- TypeScript
- NextAuth.js
- Tailwind CSS

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
