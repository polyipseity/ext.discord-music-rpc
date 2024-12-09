# setup

- Create an application at https://discord.com/developers/ (the name will be the text displayed in Listening to ...)
- Copy `.env.template` to `.env`
- Copy your Discord app's Application ID into `.env`
- Add services:
  - Last.fm - create an API account at https://www.last.fm/api/account/create and copy your API key and fill out your username in `.env`
  - Spotify - create an app at https://developer.spotify.com/dashboard with a Redirect URI of http://localhost:8888/callback and copy the Client ID and Secret into `.env`
  - SoundCloud - copy your token from your browser cookies after you've logged in (f12 -> Application -> Cookies -> soundcloud.com -> `oauth_token`) into `.env`
