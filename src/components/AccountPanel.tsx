// Thin shim — re-exports the consolidated AccountPanel from @chirag127/astro-chrome
// and injects this app's Firebase `auth` instance so existing call sites
// (`<AccountPanel />` with no `auth` prop) keep working unchanged.
import { AccountPanel as ChromeAccountPanel, type AccountPanelProps } from '@chirag127/astro-chrome/AccountPanel'
import { auth } from '~/lib/firebase'

export type { AccountPanelProps }
export { ChromeAccountPanel as AccountPanel }

export default function AccountPanel(props: Omit<AccountPanelProps, 'auth'> & { auth?: AccountPanelProps['auth'] }) {
  return <ChromeAccountPanel auth={props.auth ?? auth} {...props} />
}
