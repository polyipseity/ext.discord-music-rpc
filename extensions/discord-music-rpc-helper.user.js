// ==UserScript==
// @name        discord-music-rpc helper
// @description
// @namespace   https://github.com/f0e
// @author      f0e
// @version     1.04
// @match       *://*.ampcast.app/*
// @match       *://*.soundcloud.com/*
// @match       *://*.youtube.com/*
// @grant       none
// @updateURL   https://github.com/f0e/discord-music-rpc/raw/main/extensions/discord-music-rpc-helper.user.js
// @downloadURL https://github.com/f0e/discord-music-rpc/raw/main/extensions/discord-music-rpc-helper.user.js
// @supportURL  https://github.com/f0e/discord-music-rpc/issues
// ==/UserScript==

// lots of code from https://github.com/web-scrobbler/web-scrobbler

const WEBSOCKET_URL = "ws://localhost:47474"; // note: brave shields block local websockets.. -_-
const VERSION = 1;
const UPDATE_GAP_SECS = 1;

const PLATFORM_LOGOS = {
  Ampcast: "https://ampcast.app/apple-touch-icon.png",
  SoundCloud:
    "https://d21buns5ku92am.cloudfront.net/26628/images/419679-1x1_SoundCloudLogo_cloudmark-f5912b-large-1645807040.jpg",
  YouTube: "https://music.youtube.com/img/cairo/favicon_144.png",
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const getTextFromSelectors = (selectors, root = document) => {
  for (const selector of selectors) {
    const element = root.querySelector(selector);
    if (element) return element.textContent.trim();
  }
  return null;
};

class MusicPlatformConnector {
  constructor() {
    if (new.target === MusicPlatformConnector) {
      throw new TypeError(
        "Cannot construct MusicPlatformConnector instances directly"
      );
    }

    this.source = "Unknown";
    this.sourceImage = null;
  }

  async isPlaying() {
    throw new Error("Method 'isPlaying()' must be implemented");
  }

  async getArtistTrack() {
    throw new Error("Method 'getArtistTrack()' must be implemented");
  }

  async getCurrentTimeAndDuration() {
    throw new Error("Method 'getCurrentTimeAndDuration()' must be implemented");
  }

  async getUniqueID() {
    return null;
  }

  async getTrackArt() {
    return null;
  }

  async getTrackInfo() {
    if (!await this.isPlaying()) return null;

    const { artist, track } = await this.getArtistTrack();
    const timeInfo = await this.getCurrentTimeAndDuration();

    if (!artist || !track) return null;

    return {
      name: track,
      artist: artist,
      url: await this.getUniqueID(),
      image: await this.getTrackArt(),
      progress_ms: (timeInfo?.currentTime || 0) * 1000,
      duration_ms: (timeInfo?.duration || 0) * 1000,
    };
  }

  async getSourceInfo() {
    return {
      source: this.source,
      sourceImage: this.sourceImage,
    };
  }
}

class AmpcastConnector extends MusicPlatformConnector {
  constructor() {
    super();
    this.source = "Ampcast";
    this.sourceImage = PLATFORM_LOGOS.Ampcast;
  }

  static matchesPlatform() {
    const hostname = window.location.hostname;
    console.log(hostname);
    return hostname.endsWith("ampcast.app");
  }

  static FETCH_CACHE = new Map();

  static async fetchCached(url, init = void 0) {
    let ret = this.FETCH_CACHE.get(url.href);
    if (!ret || (typeof ret === "number" && Date.now() >= ret + 60000)) {
      try {
        ret = await fetch(url, init);
        ret = await ret.json();
      } catch (err) {
        console.debug(err);
        ret = Date.now();
      }
      this.FETCH_CACHE.set(url.href, ret);
    }
    return typeof ret === "number" ? null : ret;
  }

  static NULL_MEDIA_INFO = {
    title: null,
    artist: null,
    uniqueID: null,
    coverArt: null,
  };

  static async getMediaInfo() {
    const infoButton = document.querySelector(".icon-button-info");
    if (infoButton === null) return this.NULL_MEDIA_INFO;

    const dialog = await new Promise(resolve => {
      const obs = new MutationObserver((mutations, observer) => {
        for (const node of mutations.flatMap(mut => [...mut.addedNodes])) {
          if (node instanceof Element && node.classList.contains("media-info-dialog")) {
            resolve(node);
            observer.disconnect();
            return;
          }
        }
      });
      obs.observe(document, { childList: true, subtree: true });
      infoButton.click();
      window.setTimeout(() => { resolve(null); obs.disconnect(); }, 2000);
    });
    if (dialog === null) return this.NULL_MEDIA_INFO;

    let title = getTextFromSelectors([".title"], dialog);

    dialog.querySelector(".artist .by")?.remove();
    let artist = getTextFromSelectors([".artist"], dialog);

    let uniqueID = dialog.querySelector(".external-view a.external-link").href ?? null;
    if (uniqueID !== null && uniqueID.includes("youtube.com")) {
      const videoID = new URL(uniqueID).searchParams.get("v");
      uniqueID = videoID ? `https://youtu.be/${videoID}` : uniqueID;
    }

    const coverArt = dialog.querySelector("img.cover-art-image")?.src ?? null;

    const externalLinkEls = dialog.querySelectorAll("a.external-link, a.external");
    for (const externalLinkEl of externalLinkEls) {
      if (externalLinkEl.href) {
        const url = new URL(externalLinkEl.href);
        if (url.hostname.endsWith("musicbrainz.org")) {
          url.pathname = `/ws/2${url.pathname}`;
          url.searchParams.set("fmt", "json");
          url.searchParams.set("inc", "artists");

          const mbInfo = await this.fetchCached(url, {
            method: "GET",
            mode: "cors",
          });
          if (mbInfo !== null) {
            title = mbInfo.title ?? title;
            artist = (mbInfo["artist-credit"] ?? [])[0]?.name ?? artist;
          }

          break;
        }
      }
    }

    dialog.querySelector(".dialog-close")?.click();
    return { title, artist, uniqueID, coverArt };
  }

  isPlaying() {
    return document.querySelector(".media-button-pause") !== null;
  }

  async getArtistTrack() {
    const { title, artist } = await this.constructor.getMediaInfo();
    return { track: title, artist };
  }

  getCurrentTimeAndDuration() {
    const videoElement = document.querySelector("input#playhead");
    if (!videoElement) return null;
    return {
      currentTime: videoElement.value,
      duration: videoElement.max,
    };
  }

  async getUniqueID() {
    const { uniqueID } = await this.constructor.getMediaInfo();
    return uniqueID;
  }

  async getTrackArt() {
    const { coverArt } = await this.constructor.getMediaInfo();
    return coverArt;
  }

  async getSourceInfo() {
    const ret = await super.getSourceInfo();
    const { uniqueID } = await this.constructor.getMediaInfo();
    if (uniqueID !== null) {
      const url = new URL(uniqueID);
      if (url.hostname.endsWith("soundcloud.com"))
        ret.source = "SoundCloud";
      else if (url.hostname.endsWith("youtu.be"))
        ret.source = "YouTube";
    }
    return ret;
  }
}

// SoundCloud Platform Connector
class SoundCloudConnector extends MusicPlatformConnector {
  constructor() {
    super();
    this.source = "SoundCloud";
    this.sourceImage = PLATFORM_LOGOS.SoundCloud;
  }

  static matchesPlatform() {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;

    return (
      hostname.includes("soundcloud.com") && pathname !== "/n/pages/standby"
    );
  }

  SELECTORS = {
    artist: [
      ".playbackSoundBadge__titleContextContainer > a",
      "[class*=MiniPlayer_MiniPlayerArtist]",
    ],
    track: [
      ".playbackSoundBadge__titleLink > span:nth-child(2)",
      "[class*=MiniPlayer_MiniPlayerTrack]",
    ],
    trackArt: [
      ".playControls__soundBadge span.sc-artwork",
      "[class*=MiniPlayer_MiniPlayerArtworkImage]",
    ],
    progress: ".playbackTimeline__progressWrapper[role='progressbar']",
    playControl: ".playControls .playControl",
    miniplayerPause:
      '[class*=IconButton_Medium][data-testid="miniplayer-pause"]',
    titleLink: ".playbackSoundBadge__titleLink",
  };

  isPlaying() {
    const playControl = document.querySelector(this.SELECTORS.playControl);
    const miniplayerPause = document.querySelector(
      this.SELECTORS.miniplayerPause
    );

    return (
      playControl?.classList.contains("playing") || miniplayerPause !== null
    );
  }

  getArtistTrack() {
    const trackText = getTextFromSelectors(this.SELECTORS.track);
    if (!trackText) return { artist: null, track: null };

    const parts = trackText.split(" - ");

    let artist, track;

    if (parts.length > 1) {
      // track name is 'artist - title', use that
      [artist, track] = parts;
    } else {
      track = trackText;
      artist = getTextFromSelectors(this.SELECTORS.artist);
    }

    return { artist, track };
  }

  getCurrentTimeAndDuration() {
    const progressWrapper = document.querySelector(this.SELECTORS.progress);
    if (!progressWrapper) return { currentTime: 0, duration: 0 };

    const currentTime =
      parseInt(progressWrapper.getAttribute("aria-valuenow")) || 0;
    const duration =
      parseInt(progressWrapper.getAttribute("aria-valuemax")) || 0;

    return {
      currentTime,
      duration,
    };
  }

  getUniqueID() {
    const titleLink = document.querySelector(this.SELECTORS.titleLink);
    if (!titleLink) return null;

    const url = new URL(titleLink.href);
    return url.origin + url.pathname;
  }

  getTrackArt() {
    for (const selector of this.SELECTORS.trackArt) {
      const element = document.querySelector(selector);

      if (element && element.src) {
        return element.src.replace("-t50x50.", "-t200x200.");
      }

      if (element && element.style.backgroundImage) {
        const imageUrl = element.style.backgroundImage
          .slice(4, -1)
          .replace(/["']/g, "");
        return imageUrl.replace("-t50x50.", "-t200x200.");
      }
    }
    return null;
  }
}

// YouTube Platform Connector
class YouTubeConnector extends MusicPlatformConnector {
  constructor() {
    super();
    this.source = "YouTube";
    this.sourceImage = PLATFORM_LOGOS.YouTube;
  }

  static matchesPlatform() {
    const hostname = window.location.hostname;
    console.log(hostname);
    return hostname.includes("youtube.com");
  }

  SELECTORS = {
    video: ".html5-main-video",
    title: [
      ".html5-video-player .ytp-title-link",
      ".slim-video-information-title .yt-core-attributed-string",
    ],
    channel: [
      "#top-row .ytd-channel-name a",
      ".slim-owner-channel-name .yt-core-attributed-string",
    ],
  };

  isPlaying() {
    return document.querySelector(".html5-video-player.playing-mode") !== null;
  }

  getArtistTrack() {
    const title = getTextFromSelectors(this.SELECTORS.title);
    const artist = getTextFromSelectors(this.SELECTORS.channel);

    if (!title) return { artist: null, track: null };

    return { track: title, artist };

    // todo: implement this just for music when/if i add music detection
    // const parts = title.split(" - ");
    // return parts.length > 1
    //   ? { artist: parts[0], track: parts[1] }
    //   : { artist: artist, track: title };
  }

  getCurrentTimeAndDuration() {
    const videoElement = document.querySelector(this.SELECTORS.video);
    if (!videoElement) return null;

    return {
      currentTime: videoElement.currentTime,
      duration: videoElement.duration,
    };
  }

  getUniqueID() {
    const videoId = new URLSearchParams(window.location.search).get("v");
    return videoId ? `https://youtu.be/${videoId}` : null;
  }

  getTrackArt() {
    // YouTube typically requires more complex thumbnail extraction
    const videoId = new URLSearchParams(window.location.search).get("v");
    return videoId ? `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg` : null;
  }
}

class ApiConnector {
  constructor(url) {
    this.url = url;
    this.socket = null;
    this.reconnectTimeout = null;
    this.isConnected = false;
  }

  connect() {
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      console.log("WebSocket connected");
      this.isConnected = true;
      clearTimeout(this.reconnectTimeout);
    };

    this.socket.onclose = (event) => {
      console.log("WebSocket disconnected", event);
      this.isConnected = false;
      this.reconnectTimeout = setTimeout(() => this.connect(), 5000);
    };

    this.socket.onerror = (error) => {
      console.error("WebSocket error", error);
    };
  }

  sendTrackInfo(trackInfo, sourceInfo) {
    if (!this.isConnected) return;

    try {
      const packet = {
        version: VERSION,
        type: "track_update",
        data: trackInfo,
        source: sourceInfo.source,
        source_image: sourceInfo.sourceImage,
      };

      console.log("Sent track info", packet);

      this.socket.send(JSON.stringify(packet));
    } catch (error) {
      console.error("Error sending track info", error);
    }
  }

  close() {
    if (this.socket) {
      this.socket.close();
    }
    clearTimeout(this.reconnectTimeout);
  }
}

async function run() {
  const PLATFORM_CONNECTORS = [AmpcastConnector, SoundCloudConnector, YouTubeConnector];

  const PlatformConnectorClass = PLATFORM_CONNECTORS.find((connector) =>
    connector.matchesPlatform()
  );

  if (!PlatformConnectorClass) return;

  const scrobbler = new ApiConnector(WEBSOCKET_URL);
  scrobbler.connect();

  const connector = new PlatformConnectorClass();
  let first = true;
  let lastTrackInfo = null;

  while (true) {
    if (!first) await sleep(UPDATE_GAP_SECS * 1000);
    else first = false;

    const trackInfo = await connector.getTrackInfo();

    if (JSON.stringify(lastTrackInfo) !== JSON.stringify(trackInfo)) {
      scrobbler.sendTrackInfo(trackInfo, await connector.getSourceInfo());
      lastTrackInfo = trackInfo;
    }
  }
}

run();
