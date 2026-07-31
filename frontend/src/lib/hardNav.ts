// Hard navigation: every internal navigation link is a plain <a> with a
// data-hardnav attribute and a hash href (the app uses HashRouter). A native
// capture-phase click listener (registered outside React, so it works even if
// React's event system misbehaves) turns each click into: go to the URL, then
// force a full page reload so the destination always loads fresh.

export function hardHref(to: string): string {
  return `#${to}`
}

export function installHardNav(): void {
  document.addEventListener(
    'click',
    (event) => {
      const el = event.target as Element | null
      const anchor = el?.closest?.('a[data-hardnav]')
      if (!anchor) return
      const href = anchor.getAttribute('href')
      if (!href) return
      event.preventDefault()
      window.location.href = href
      window.location.reload()
    },
    true,
  )
}
