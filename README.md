# History & Immigration Policy

A scrollytelling interactive about the history of US immigration policy — a scroll-driven timeline that sails a ship down a river of law, from the colonial era to the present, stopping at the policies that opened or closed the door.

## What's here

- **`index.html`** — the main interactive. A single self-contained page: open it directly in a browser, no build step or server required. Scrolling drives a GSAP-powered camera and ship along an SVG river path; each policy gets a card (or, for landmark policies, a "dossier" you can open for fuller context), grouped into narrative eras.
- **`images/`** — photos, illustrations, and textures used by the timeline.
- **`docs/`** — planning notes for upcoming work on the timeline (image placement, animation specs).
- **`script.js`** / **`style.css`** — logic and styles for a second, not-yet-assembled part of the project (a persona-based "walk in someone's shoes" flow plus a demographics questionnaire). Not currently linked from any page.

## Running it

Open `index.html` in any modern browser. That's it — everything the timeline needs is inlined in that file.

## Contributing

See [CLAUDE.md](CLAUDE.md) for a detailed breakdown of the timeline's architecture (scroll engine, coordinate system, data shape, and hard constraints) if you're making changes to it.
