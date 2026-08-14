/*
 * AuthButton — compact top-right sign-in / account island (client:load).
 * Vault & Foil styled Clerk auth. Signed out → foil-bordered "Sign in"
 * button opening a modal; signed in → Clerk <UserButton>.
 *
 * Per the no-auth rule this gates only saved-cards/compare-sync, never the
 * free ledger.
 */
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react'
import ClerkProvider, { hasClerk } from './auth/ClerkProvider'

export default function AuthButton() {
  // No Clerk key configured (e.g. CI build without the secret): render a plain
  // link to the account page rather than Clerk context-dependent components,
  // which would throw without a real provider.
  if (!hasClerk) {
    return (
      <a className="auth-btn" href="/account/">
        Sign in
      </a>
    )
  }
  return (
    <ClerkProvider>
      <SignedOut>
        <SignInButton mode="modal">
          <button className="auth-btn" type="button" aria-label="Sign in">
            Sign in
          </button>
        </SignInButton>
      </SignedOut>
      <SignedIn>
        <UserButton
          afterSignOutUrl="/"
          appearance={{
            elements: {
              userButtonAvatarBox: {
                width: '28px',
                height: '28px',
                border: '1.5px solid #C69A5B',
                boxShadow: '0 0 0 2px rgba(198,154,91,0.28)',
              },
            },
          }}
        />
      </SignedIn>
    </ClerkProvider>
  )
}
