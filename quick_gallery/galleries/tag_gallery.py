import logging
from collections import Counter, abc

from ..media import Media
from .simple_gallery import SimpleGallery

logger = logging.getLogger(__name__)


class TagGallery(SimpleGallery):
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
                tags = ",".join(media.tags())
                gallery_items.append(
                    f'<span class="media-container" data-src="{media.public_file}" data-mimetype="{mimetype}" data-tags="{tags}"  data-index="{index}"></span>'
                )
                index += 1
        logger.info(f"Found mime-types: {mimetypes_count.most_common(None)}")
        return gallery_items

    def css_extra(self):
        return TAG_CSS

    def js_extra(self):
        return TAG_JS


TAG_CSS = """
    .tag-filter {
        display: flex;
        flex-direction: column;
        gap: 5px;
        overflow-y: auto;
    }
    label { font-size: 12px; cursor: pointer; }
"""

TAG_JS = """
    document.getElementById("controls")?.insertAdjacentHTML("beforeend", '<div id="tag-filter" class="tag-filter"></div>');

    function getUniqueTags() {
        let tags = new Set();
        mediaContainers().forEach(container => {
            const dataTags = container.getAttribute("data-tags");
            if (dataTags) {
                dataTags.split(",").forEach(tag => tags.add(tag.trim()));
            }
        });
        return Array.from(tags).sort();
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
"""
