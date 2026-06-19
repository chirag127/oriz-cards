/**
 * Firebase singleton — every site in the oriz family initializes the same
 * project (oriz-app) so a logged-in user is logged in across every subdomain.
 *
 * Lazy-proxy pattern (verbatim from oriz-home): the `auth` / `db` / `app`
 * exports are Proxies that defer the actual Firebase API call until a
 * property is accessed at runtime. This means SSR/SSG of pages that import
 * an island that imports this module does not crash when env vars are
 * missing on the build runner — only the BROWSER needs the auth instance,
 * and the React component runs only there.
 */
import { type FirebaseApp, getApps, initializeApp } from 'firebase/app'
import { type Auth, getAuth } from 'firebase/auth'
import { type Firestore, getFirestore } from 'firebase/firestore'

const config = {
  apiKey: import.meta.env.PUBLIC_FIREBASE_API_KEY,
  authDomain: import.meta.env.PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.PUBLIC_FIREBASE_APP_ID,
}

let _app: FirebaseApp | null = null
let _auth: Auth | null = null
let _db: Firestore | null = null

function getApp(): FirebaseApp {
  if (_app) return _app
  _app = getApps()[0] ?? initializeApp(config)
  return _app
}

export const auth: Auth = new Proxy({} as Auth, {
  get(_t, p) {
    if (!_auth) _auth = getAuth(getApp())
    return Reflect.get(_auth, p)
  },
}) as Auth

export const db: Firestore = new Proxy({} as Firestore, {
  get(_t, p) {
    if (!_db) _db = getFirestore(getApp())
    return Reflect.get(_db, p)
  },
}) as Firestore

export const app: FirebaseApp = new Proxy({} as FirebaseApp, {
  get(_t, p) {
    return Reflect.get(getApp(), p)
  },
}) as FirebaseApp
