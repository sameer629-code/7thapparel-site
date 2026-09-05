# Preview

The working preview bundles all pages into one self-contained HTML file and renders
them in an iframe with a floating page switcher. Useful for review without hosting.

Build it with `scripts/bundle.py` (see the script header for how it works and why the
navigation is a floating dock rather than a second top bar).

Known limits of the bundled preview, none of which affect the real site:

- The PDF download does nothing — the preview sandbox blocks downloads.
- Fragment links cannot navigate inside a `srcdoc` frame, which is why every in-page
  anchor is handled in JavaScript.
- `target="_blank"` is swallowed by the sandbox, so external links are passed to the
  parent frame to open.
