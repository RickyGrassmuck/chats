# Chats

A static archive of chat conversations, served via GitHub Pages.

## How it works

- Each chat is a standalone HTML file in `chats/` with two required `<meta>` tags.
- On push to `main`, GitHub Actions runs `scripts/build-index.py`, which reads every chat in `chats/`, generates `index.html` from `index-template.html`, and deploys the result to GitHub Pages.
- The `_site/` build output is never committed — it's an Actions artifact.

## Adding a new chat

1. Copy `templates/chat-template.html` to `chats/YYYY-MM-DD-slug.html`.
2. Fill in the two meta tags near the top:
   ```html
   <meta name="chat-title" content="Your title here">
   <meta name="chat-start-date" content="2026-05-18">
   ```
3. Replace the placeholder turns with your conversation content.
4. Commit and push to `main`. CI rebuilds and deploys automatically.

### Required meta tags

| Tag | Format | Purpose |
|-----|--------|---------|
| `chat-title` | Free text | Title shown on the index |
| `chat-start-date` | `YYYY-MM-DD` | Used for sorting (newest first) and display |

Files missing either tag are skipped by the build script with a warning — they won't appear on the index.

## Local development

```sh
pip install beautifulsoup4
python scripts/build-index.py
# Output is in _site/. Serve with:
python -m http.server -d _site 8000
```

## One-time GitHub setup

After creating the repo:

1. Go to **Settings → Pages**.
2. Set **Source** to **GitHub Actions** (not "Deploy from a branch").
3. Push a commit. The first run will deploy.

Site URL will be `https://<user>.github.io/Chats/`.

## Layout

```
.
├── .github/workflows/deploy.yml   CI: build + deploy on push
├── chats/                         Chat HTML files (add new ones here)
├── scripts/build-index.py         Reads chats/, renders index
├── templates/chat-template.html   Starting point for new chats
├── index-template.html            Index layout with {{ENTRIES}}, {{COUNT}}, {{BUILD_DATE}} placeholders
└── README.md
```
