import logging
from collections import Counter, abc

from ..media import Media
from .base_gallery import BaseGallery

logger = logging.getLogger(__name__)


class SimpleGallery(BaseGallery):
    valid_types = {"image", "video", "audio"}

    def gallery_items(self):
        mimetypes_count = Counter()
        gallery_items = []

        index = 0
        for media in self.medias:
            mimetype = media.mimetype()
            if not mimetype:
                logger.debug(f"No mimetype for file: {media=}, {mimetype=}")
                continue
            file_type = media.media_type()
            if file_type in self.valid_types:
                mimetypes_count[mimetype] += 1
                gallery_items.append(
                    f'<span class="media-container" data-src="{media.public_file}" data-mimetype="{mimetype}" data-index="{index}"></span>'
                )
                index += 1
        logger.info(f"Found mime-types: {mimetypes_count.most_common(None)}")
        return gallery_items

    def html(self):
        return (
            SIMPLE_GALLERY_HTML.replace(
                "{GALLERY_ITEMS}", "\n".join(self.gallery_items())
            )
            .replace("{CSS}", self.css_extra())
            .replace("{JS}", self.js_extra())
        )

    def css_extra(self) -> str:
        return ""

    def js_extra(self) -> str:
        return ""


SIMPLE_GALLERY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gallery</title>
    <style>
        body { display: flex; flex-direction: column; align-items: center; gap: 20px; margin: 0; padding: 20px; }
        .gallery {
width: 75%; max-width: 1000px;
        }
        .media-container {  display: flex; justify-content: center; min-height: 300px; border: 3px solid transparent; }
        .highlighted { border-color: red; }
        img, video { width: 100%; border-radius: 5px; }
            position: fixed;
            top: 10px; left: 10px;
            display: flex;
            flex-direction: column;
            gap: 5px;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.6);
            padding: 5px;
            border-radius: 5px;
            min-width: 140px;
            max-height: 80vh;
            overflow-y: auto;
        button, input { padding: 5px; font-size: 14px; cursor: pointer; }
        .controls {
            position: fixed;
            top: 10px; left: 10px;
            display: flex;
            flex-direction: column;
            gap: 5px;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.6);
            padding: 5px;
            border-radius: 5px;
            min-width: 140px;
            max-height: 80vh;
            overflow-y: auto;
        }

        @media (max-width: 768px) {
            .media-container { width: 100%; }
            button, input { font-size: 10px; padding: 3px; }
        }
        {CSS}
    </style>
    <script>
        console.log("Loading gallery");
        document.addEventListener("DOMContentLoaded", function() {
            console.log("Loaded");
            const gallery = document.querySelector(".gallery");
            let urlQP = new URLSearchParams(window.location.search);
            let currentIndex = 0;
            let startMuted = true;
            let slideshowActive = false;
            let slideshowInterval = null;

            function shuffleArray(a) {
                for (let i = a.length; i; i--) {
                    let j = Math.floor(Math.random() * i);
                    [a[i - 1], a[j]] = [a[j], a[i - 1]];
                }
            }

            function setUrlParam(key, value) {
                urlQP.set(key, value);
                history.replaceState(null, null, "?"+urlQP.toString());
            }

            function getUrlParam(key) {
                return urlQP.get(key);
            }

            function shuffleContent() {
                console.log("Shuffling");
                let children = Array.from(mediaContainers());
                for (var i = 0; i <= Math.log2(children.length); i++) {
                    shuffleArray(children)
                };
                children.forEach((e, i) => {
                    gallery.removeChild(e);
                    gallery.appendChild(e);
                    e.setAttribute('data-index', i)
                })
            }

            function mediaContainers() {
                return gallery.querySelectorAll('.media-container');
            }
            
            function loadMedia(container) {
                if (!container.innerHTML) {
                    container.style.height = null;
                    const src = container.getAttribute("data-src");
                    const mimetype = container.getAttribute("data-mimetype");
                    if (mimetype.startsWith("video/")) {
                        container.innerHTML = `<video src="${src}" muted loop controls></video>`;
                    } else if (mimetype.startsWith("audio/")) {
                        container.innerHTML = `<audio src="${src}" muted loop controls></video>`;
                    } else if (mimetype.startsWith("image/")) {
                        container.innerHTML = `<img src="${src}" loading="lazy">`;
                    } else {
                        console.log("Unknown mimetype:", container)
                    }
                }
            }

            function unloadMedia(container) {
                if (container.innerHTML) {
                    container.style.height = `${container.clientHeight}px`;
                    container.innerHTML = null;
                }
            }
            
            function updateCurrentIndex(newIndex) {
                setUrlParam("i", newIndex);
                const medias = mediaContainers();
                const prevMedia = medias[currentIndex];
                const prevVideo = prevMedia.querySelector("video");
                const currentMedia = medias[newIndex];
                const currentVideo = currentMedia.querySelector("video")
                currentIndex = newIndex;

                prevMedia.classList.remove("highlighted");
                if (prevVideo) {
                    prevVideo.muted = true;
                }

                currentMedia.classList.add("highlighted");
                loadMedia(currentMedia);
                currentMedia.scrollIntoView({ behavior: "smooth", block: "center" });
                if (currentVideo) {
                    currentVideo.muted = startMuted;
                }
            }
            
            function startSlideshow() {
                if (slideshowActive) return;
                slideshowActive = true;
                let delay = parseInt(document.getElementById("slideshow-delay").value) || 3;
                slideshowInterval = setInterval(() => {
                    updateCurrentIndex((currentIndex + 1) % mediaContainers().length);
                }, delay * 1000);
            }
            
            function stopSlideshow() {
                slideshowActive = false;
                clearInterval(slideshowInterval);
            }
            
            document.addEventListener("keydown", function(event) {
                if (event.code === "ArrowDown") {
                    event.preventDefault();
                    updateCurrentIndex((currentIndex + 1) % mediaContainers().length);
                } else if (event.code === "ArrowUp") {
                    event.preventDefault();
                    updateCurrentIndex((currentIndex - 1 + mediaContainers().length) % mediaContainers().length);
                } else if (event.code === "Space") {
                    event.preventDefault();
                    if (slideshowActive) { stopSlideshow(); } else { startSlideshow(); }
                } else if (event.code === "KeyR" ) {
                    shuffleContent()
                }
            });
            
            mediaContainers().forEach((container, index) => {
                container.addEventListener("click", function(event) {
                    let idx = Array.from(mediaContainers()).indexOf(container);
                    updateCurrentIndex(idx);
                });
            });
            
            const observer = new IntersectionObserver(entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        loadMedia(entry.target);
                        let video = entry.target.querySelector("video");
                        if (video) {
                            video.muted = true;
                            video.play();
                        }
                    } else if (entry.target.innerHTML) {
                        unloadMedia(entry.target);

                    }
                });
            }, {rootMargin: "100%"});
            
            mediaContainers().forEach(container => observer.observe(container));
            
            document.getElementById("toggle-sound").addEventListener("click", function() {
                startMuted = !startMuted;
                this.textContent = startMuted ? "Muted" : "Unmuted";
            });
            
            document.getElementById("toggle-slideshow").addEventListener("click", function() {
                if (slideshowActive) { stopSlideshow(); this.textContent = "▶"; } 
                else { startSlideshow(); this.textContent = "⏹"; }
            });

            document.getElementById("randomize").addEventListener("click", function() {
                shuffleContent();
            });

            if (getUrlParam("i")) {
                updateCurrentIndex(Number(getUrlParam("i")));
            }

            {JS}
            console.log("Gallery initialized");
        });
    </script>
</head>
<body>
    <div class="controls" id="controls">
        <button id="randomize">shuffle</button>
        <button id="toggle-sound">Muted</button>
        <input type="number" id="slideshow-delay" placeholder="Delay (s)" value="3">
        <button id="toggle-slideshow">▶</button>
    </div>
    <div class="gallery">
        {GALLERY_ITEMS}
    </div>
</body>
</html>
"""
