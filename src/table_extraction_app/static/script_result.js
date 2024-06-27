document.addEventListener("DOMContentLoaded", function() {
    var zoomableImages = document.querySelectorAll(".zoomable");
    var imageModal = document.getElementById("imageModal");
    var modalImage = document.getElementById("modalImage");

    zoomableImages.forEach(function(img) {
        img.addEventListener("click", function() {
            modalImage.src = this.src;
            imageModal.style.display = "flex";
        });
    });

    imageModal.addEventListener("click", function() {
        imageModal.style.display = "none";
    });
});
