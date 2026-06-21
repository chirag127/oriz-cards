// Thin shim — re-exports the consolidated FinishSignIn from @chirag127/astro-chrome
// and injects this app's Firebase `auth` instance so existing call sites
// (`<FinishSignIn />` with no `auth` prop) keep working unchanged.
import { FinishSignIn as ChromeFinishSignIn, type FinishSignInProps } from '@chirag127/astro-chrome/FinishSignIn'
import { auth } from '~/lib/firebase'

export type { FinishSignInProps }
export { ChromeFinishSignIn as FinishSignIn }

export default function FinishSignIn(props: Omit<FinishSignInProps, 'auth'> & { auth?: FinishSignInProps['auth'] }) {
  return <ChromeFinishSignIn auth={props.auth ?? auth} {...props} />
}
