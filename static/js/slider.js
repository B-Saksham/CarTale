document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-slider]").forEach(slider => {
        const slides = slider.querySelectorAll(".car-slide");
        if (slides.length <= 1) return;

        let index = 0;

        const showSlide = (i) => {
            slides.forEach((img, idx) => {
                img.classList.toggle("active", idx === i);
            });
        };

        const nextBtn = slider.querySelector(".slider-btn.next");
        const prevBtn = slider.querySelector(".slider-btn.prev");

        nextBtn?.addEventListener("click", () => {
            index = (index + 1) % slides.length;
            showSlide(index);
        });

        prevBtn?.addEventListener("click", () => {
            index = (index - 1 + slides.length) % slides.length;
            showSlide(index);
        });
    });
});
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".car-price").forEach(el => {
        let value = el.innerText.replace(/[^0-9]/g, "");
        if (!value) return;
        el.innerText = "NPR " + Number(value).toLocaleString("en-IN");
    });
});