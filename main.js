// @ts-check

class FrameClock {
    /** @type {number} */
    fps = 0;

    /** @type {number} */
    last = performance.now();

    /** @type {number} */
    delta = 0;

    /** @type {number} */
    smooth = 0.1;

    /**
     * @param {number} [now]
     * @returns {void}
     */
    _tick = (now = performance.now()) => {
        this.delta = now - this.last;
        this.last = now;
        this.fps += (1000 / this.delta - this.fps) * this.smooth;
    };
}

const showInfo = () => {
    const windowInnerWidth = document.getElementById("window-inner-width");
    if (windowInnerWidth) windowInnerWidth.textContent = f(window.innerWidth);
    const windowInnerHeight = document.getElementById("window-inner-height");
    if (windowInnerHeight) windowInnerHeight.textContent = f(window.innerHeight);

    const htmlClientWidth = document.getElementById("html-client-width");
    if (htmlClientWidth) htmlClientWidth.textContent = f(document.documentElement.clientWidth);
    const htmlClientHeight = document.getElementById("html-client-height");
    if (htmlClientHeight) htmlClientHeight.textContent = f(document.documentElement.clientHeight);

    const bodyClientWidth = document.getElementById("body-client-width");
    if (bodyClientWidth) bodyClientWidth.textContent = f(document.body.clientWidth);
    const bodyClientHeight = document.getElementById("body-client-height");
    if (bodyClientHeight) bodyClientHeight.textContent = f(document.body.clientHeight);
};

/**
 * @param {number} n
 * @returns {string}
 */
const f = (n) => String(n).padStart(4, "0");

window.addEventListener("load", () => {
    showInfo();
});

window.addEventListener("resize", () => {
    showInfo();
});
