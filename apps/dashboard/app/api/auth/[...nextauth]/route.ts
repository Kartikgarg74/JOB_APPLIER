import NextAuth, { DefaultSession, SessionStrategy } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import GoogleProvider from "next-auth/providers/google";

// [PURPOSE] Handles user authentication and session management
const authOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials, req) {
        // [CONTEXT] Authenticates user against the backend API
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_USER_SERVICE_URL}/api/login`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              username: credentials?.username,
              password: credentials?.password,
            }),
          },
        );

        const user = await res.json();

        if (res.ok && user) {
          // [CONTEXT] Attach token and user ID to the user object for session
          return { ...user, id: user.user_id, token: user.token };
        }
        return null;
      },
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID as string,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
    }),
  ],
  session: {
    strategy: "jwt" as SessionStrategy,
  },
  callbacks: {
    // [CONTEXT] Manages JWT creation and updates
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.token = user.token;
        // [CONTEXT] Placeholder for user roles - to be fetched from backend if available
        token.roles = ["user"]; // Example role
      }
      return token;
    },
    // [CONTEXT] Manages session data, exposing user information to the frontend
    async session({ session, token }) {
      session.user.id = token.id;
      session.user.token = token.token;
      session.user.roles = token.roles; // Expose roles to session
      return session;
    },
  },
  pages: {
    signIn: "/auth/signin",
  },
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };

// [CONTEXT] Extend NextAuth types to include custom properties
declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      token: string;
      roles: string[];
    } & DefaultSession["user"];
  }

  interface User {
    id: string;
    token: string;
    roles: string[];
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id: string;
    token: string;
    roles: string[];
  }
}
