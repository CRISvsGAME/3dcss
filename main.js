// @ts-check

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
