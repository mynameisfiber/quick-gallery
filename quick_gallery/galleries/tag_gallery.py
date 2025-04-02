import logging
from collections import Counter, abc

from ..media import Media
from .base_gallery import BaseGallery

logger = logging.getLogger(__name__)


class TagGallery(BaseGallery):
    valid_types = {"image", "video", "audio"}

    def __init__(self, medias: abc.Iterable[Media]):
        super().__init__(medias)
        mimetypes_count = Counter()
        self.gallery_items = []

        for media in medias:
            mimetype = media.mimetype()
            if not mimetype:
                logger.debug(f"No mimetype for file: {media=}, {mimetype=}")
                continue
            file_type = media.media_type()
            if file_type in self.valid_types:
                mimetypes_count[mimetype] += 1
                self.gallery_items.append(
                    f'<span class="media-container" data-src="{media.public_file}" data-mimetype="{mimetype}" data-tags="{media.media_type()},{media.mimetype()},{str(media.parent)}"></span>'
                )
        logger.info(f"Found mime-types: {mimetypes_count.most_common(None)}")

    def html(self):
        return SIMPLE_GALLERY_HTML.replace(
            "{GALLERY_ITEMS}", "\n".join(self.gallery_items)
        )


SIMPLE_GALLERY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gallery</title>
    <style>
           body { display: flex; flex-direction: column; align-items: center; gap: 20px; margin: 0; padding: 20px; }
        .gallery { width: 75%; max-width: 1000px; }
        .media-container { display: flex; justify-content: center; min-height: 300px; border: 3px solid transparent; }
        .highlighted { border-color: red; }
        img, video { width: 100%; border-radius: 5px; }
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
        button, input { padding: 5px; font-size: 14px; cursor: pointer; }
        .tag-filter { 
            display: flex; 
            flex-direction: column; 
            gap: 5px; 
            max-height: 200px; 
            overflow-y: auto; 
        }
        label { font-size: 12px; cursor: pointer; }

        @media (max-width: 768px) {
            .media-container { width: 100%; }
            button, input { font-size: 10px; padding: 3px; }
        }
   </style>
    <script>
        console.log("Loading gallery");
        document.addEventListener("DOMContentLoaded", function() {
            console.log("Loaded");
            const gallery = document.querySelector(".gallery");
            const tagListContainer = document.getElementById("tag-list");
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
                    const tags = container.getAttribute("data-tags");
                    if (mimetype.startsWith("video/")) {
                        container.innerHTML = `<video src="${src}" muted loop controls title="${tags}"></video>`;
                    } else if (mimetype.startsWith("audio/")) {
                        container.innerHTML = `<audio src="${src}" muted loop controls title="${tags}"></video>`;
                    } else if (mimetype.startsWith("image/")) {
                        container.innerHTML = `<img src="${src}" loading="lazy" title="${tags}">`;
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

                        // Extract unique tags from media elements
            function getUniqueTags() {
                let tags = new Set();
                mediaContainers().forEach(container => {
                    const dataTags = container.getAttribute("data-tags");
                    if (dataTags) {
                        dataTags.split(",").forEach(tag => tags.add(tag.trim()));
                    }
                });
                return Array.from(tags);
            }

            function populateTagControls() {
                const tagFilterDiv = document.getElementById("tag-filter");
                tagFilterDiv.innerHTML = ""; // Clear previous tags
            
                getUniqueTags().forEach(tag => {
                    const label = document.createElement("label");
                    const checkbox = document.createElement("input");
                    checkbox.type = "checkbox";
                    checkbox.value = tag;
                    checkbox.checked = false;
            
                    // Regular click: Toggle individual tag
                    checkbox.addEventListener("change", filterGallery);
            
                    // Double-click: Select only this tag (deselect others)
                    label.addEventListener("dblclick", function() {
                        document.querySelectorAll("#tag-filter input[type='checkbox']").forEach(cb => {
                            cb.checked = false;
                        });
                        checkbox.checked = true;
                        filterGallery();
                    });
            
                    label.appendChild(checkbox);
                    label.appendChild(document.createTextNode(" " + tag));
                    tagFilterDiv.appendChild(label);
                });
            
                filterGallery(); // Ensure proper display on load
            }


            // Filters gallery based on selected tags
            function filterGallery() {
                const selectedTags = Array.from(document.querySelectorAll("#tag-filter input[type='checkbox']:checked"))
                    .map(input => input.value);

                if (selectedTags.length === 0) {
                    // If no tags are selected, show all images
                    mediaContainers().forEach(container => {
                        container.style.display = "flex";
                    });
                } else {
                    // Show only matching media
                    mediaContainers().forEach(container => {
                        const tags = container.getAttribute("data-tags");
                        if (!tags || !selectedTags.some(tag => tags.includes(tag))) {
                            container.style.display = "none";
                        } else {
                            container.style.display = "flex";
                        }
                    });
                }
            }

            // Initialize
            populateTagControls();

            console.log("Gallery initialized");
        });
    </script>
</head>
<body>
    <div class="controls">
        <button id="randomize">shuffle</button>
        <button id="toggle-sound">Unmute</button>
        <input type="number" id="slideshow-delay" placeholder="Delay (s)" value="3">
        <button id="toggle-slideshow">▶</button>
        <div id="tag-filter" class="tag-filter"></div>
    </div>
    <div class="gallery">
        {GALLERY_ITEMS}
</body>
</html>
"""
