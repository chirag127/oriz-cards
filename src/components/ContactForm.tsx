/*
 * ContactForm — local copy emitting the canonical `data-oriz-contact-*` hooks.
 * Posts to Web3Forms which forwards to the operator's inbox. Includes a
 * honeypot field for spam mitigation.
 */
import { useState } from 'react'

interface Props {
  web3formsKey?: string
  fromName?: string
}

export default function ContactForm({
  web3formsKey,
  fromName = 'oriz · cards contact form',
}: Props) {
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle')
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!web3formsKey) {
      setStatus('error')
      setError('Form is not configured. Please email whyiswhen@gmail.com directly.')
      return
    }
    setStatus('sending')
    setError(null)
    const fd = new FormData(e.currentTarget)
    if (fd.get('botcheck')) {
      // Honeypot — silently mark sent without actually sending.
      setStatus('sent')
      return
    }
    fd.append('access_key', web3formsKey)
    fd.append('from_name', fromName)
    try {
      const res = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        body: fd,
      })
      const json = await res.json().catch(() => ({}))
      if (res.ok && json.success !== false) {
        setStatus('sent')
        e.currentTarget.reset()
      } else {
        setStatus('error')
        setError(json.message ?? 'Something went wrong. Please try email instead.')
      }
    } catch (err) {
      setStatus('error')
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  return (
    <form data-oriz-contact onSubmit={onSubmit} noValidate>
      <input
        type="text"
        name="botcheck"
        tabIndex={-1}
        autoComplete="off"
        data-oriz-contact-honeypot
        aria-hidden="true"
      />
      <label data-oriz-contact-field>
        <span>Name</span>
        <input type="text" name="name" required maxLength={120} autoComplete="name" />
      </label>
      <label data-oriz-contact-field>
        <span>Email</span>
        <input type="email" name="email" required maxLength={200} autoComplete="email" />
      </label>
      <label data-oriz-contact-field>
        <span>Message</span>
        <textarea name="message" required minLength={4} maxLength={4000} rows={5} />
      </label>
      {status === 'error' && (
        <p data-oriz-contact-error role="alert">
          {error ?? 'Something went wrong.'}
        </p>
      )}
      <button
        type="submit"
        data-oriz-contact-submit
        disabled={status === 'sending' || status === 'sent'}
      >
        {status === 'sending' ? 'Sending…' : status === 'sent' ? 'Sent ·' : 'Send message'}
      </button>
      {status === 'sent' && (
        <p data-oriz-contact-success role="status">
          Message received. I read these in batches and reply within a few days.
        </p>
      )}
    </form>
  )
}
