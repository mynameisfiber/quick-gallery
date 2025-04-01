import sys
from collections import Counter, abc
import mimetypes

from .media import Media


def generate_gallery(medias: abc.Iterable[Media], log=sys.stderr):
    valid_types = {"image", "video", "audio"}
    mimetypes_count = Counter()
    gallery_items = []

    for media in medias:
        mimetype = media.mimetype()
        if not mimetype:
            print(f"No mimetype for file: {media=}, {mimetype=}", file=log)
            continue
        file_type = media.media_type()
        if file_type in valid_types:
            mimetypes_count[mimetype] += 1
            gallery_items.append(
                f'<span class="media-container" data-src="{media.public_file}" data-mimetype="{mimetype}"></span>'
            )
    print(f"Found mime-types: {mimetypes_count.most_common(None)}", file=log)

    html_content = (
        """<!DOCTYPE html>
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
        .controls { position: fixed; top: 10px; left: 10px; display: flex; flex-direction: column; gap: 5px; z-index: 1000; background: rgba(255, 255, 255, 0.6); padding: 5px; border-radius: 5px; min-width: 55px; width: 10%; }
        button, input { padding: 5px; font-size: 14px; cursor: pointer; }

        @media (max-width: 768px) {
            .media-container { width: 100%; }
            button, input { font-size: 10px; padding: 3px; }
        }
    </style>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const gallery = document.querySelector(".gallery");
            let currentIndex = 0;
            let startMuted = true;
            let currentPlaying = null;
            let slideshowActive = false;
            let slideshowInterval = null;

            function shuffleArray(a) {
                for (let i = a.length; i; i--) {
                    let j = Math.floor(Math.random() * i);
                    [a[i - 1], a[j]] = [a[j], a[i - 1]];
                }
            }

            function shuffleContent() {
                console.log("Shuffling");
                let children = Array.from(mediaContainers());
                for (var i = 0; i <= Math.log2(children.length); i++) {
                    shuffleArray(children)
                };
                children.forEach((e) => {
                    gallery.removeChild(e);
                    gallery.appendChild(e);
                })
            }

            function mediaContainers() {
                return gallery.querySelectorAll('.media-container');
            }
            
            function loadMedia(index) {
                const container = mediaContainers()[index];
                if (!container.innerHTML) {
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
            
            function updateCurrentIndex(index) {
                const media = mediaContainers();
                media[currentIndex].classList.remove("highlighted");
                currentIndex = index;
                media[currentIndex].classList.add("highlighted");
                loadMedia(currentIndex);
                media[currentIndex].scrollIntoView({ behavior: "smooth", block: "center" });
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
                    let media = entry.target.querySelector("video");
                    let index = Array.from(mediaContainers()).indexOf(entry.target);
                    if (entry.isIntersecting) {
                        loadMedia(index);
                        if (media && entry.intersectionRatio == 1.0) {
                            if (currentPlaying && currentPlaying !== media) {
                                currentPlaying.pause();
                            }
                            media.muted = startMuted;
                            media.play();
                            currentPlaying = media;
                        }
                    } else if (media && media === currentPlaying) {
                        media.pause();
                        currentPlaying = null;
                    }
                });
            }, { threshold: 0.05 });
            
            mediaContainers().forEach(container => observer.observe(container));
            
            document.getElementById("toggle-sound").addEventListener("click", function() {
                startMuted = !startMuted;
                if (currentPlaying) {
                    currentPlaying.muted = startMuted;
                }
                this.textContent = startMuted ? "Unmute" : "Mute";
            });
            
            document.getElementById("toggle-slideshow").addEventListener("click", function() {
                if (slideshowActive) { stopSlideshow(); this.textContent = "▶"; } 
                else { startSlideshow(); this.textContent = "⏹"; }
            });

            document.getElementById("randomize").addEventListener("click", function() {
                shuffleContent();
            });
        });
    </script>
</head>
<body>
    <div class="controls">
        <button id="randomize">shuffle</button>
        <button id="toggle-sound">Unmute</button>
        <input type="number" id="slideshow-delay" placeholder="Delay (s)" value="3">
        <button id="toggle-slideshow">▶</button>
    </div>
    <div class="gallery">"""
        + "".join(gallery_items)
        + """</div>
</body>
</html>
    """
    )

    return html_content


if __name__ == "__main__":
    file_paths = sys.stdin.readlines()
    print(generate_gallery(file_paths))
