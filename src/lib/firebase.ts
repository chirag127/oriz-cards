/**
 * Firebase singleton — re-exports app/auth/db from @chirag127/oriz-ui's
 * shared initFirebase helper so every oriz site uses the same project
 * (oriz-app) and shares a sign-in across subdomains.
 */
import { initFirebase } from '@chirag127/oriz-ui'

const env = {
  apiKey: import.meta.env.PUBLIC_FIREBASE_API_KEY,
  authDomain: import.meta.env.PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.PUBLIC_FIREBASE_APP_ID,
}

export const { app, auth, db } = initFirebase(env)
