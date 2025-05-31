import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import { JWT } from "next-auth/jwt";
import { Session } from "next-auth";

// Extend the default session type to include our custom properties
interface ExtendedSession extends Session {
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: number;
}

// Extend the default JWT type
interface ExtendedToken extends JWT {
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: number;
}

export const authOptions = {
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile",
          prompt: "consent",
          access_type: "offline",
          response_type: "code",
        },
      },
    }),
  ],
  pages: {
    signIn: '/',
    signOut: '/',
    error: '/',
    newUser: '/',
  },
  callbacks: {
    async jwt({ token, account }: { token: ExtendedToken; account: any }) {
      // Persist the OAuth access_token and refresh_token to the token right after signin
      if (account) {
        token.accessToken = account.access_token;
        token.refreshToken = account.refresh_token;
        token.expiresAt = account.expires_at;
      }
      return token;
    },
    async session({ session, token }: { session: ExtendedSession; token: ExtendedToken }) {
      // Send properties to the client
      session.accessToken = token.accessToken;
      session.refreshToken = token.refreshToken;
      session.expiresAt = token.expiresAt;
      return session;
    },
    async redirect({ url, baseUrl }: { url: string; baseUrl: string }) {
      // Ensure all redirects use port 3000
      if (url.startsWith("/")) {
        return `http://localhost:3000${url}`;
      }
      // For other URLs, check if they should be allowed
      else if (new URL(url).origin === baseUrl) {
        return url;
      }
      return 'http://localhost:3000';
    },
  },
  debug: process.env.NODE_ENV === 'development',
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST }; 