const showInfo = () => {
    const windowInnerWidth = document.getElementById("window-inner-width");
    windowInnerWidth.textContent = f(window.innerWidth);
    const windowInnerHeight = document.getElementById("window-inner-height");
    windowInnerHeight.textContent = f(window.innerHeight);

    const htmlClientWidth = document.getElementById("html-client-width");
    htmlClientWidth.textContent = f(document.documentElement.clientWidth);
    const htmlClientHeight = document.getElementById("html-client-height");
    htmlClientHeight.textContent = f(document.documentElement.clientHeight);

    const bodyClientWidth = document.getElementById("body-client-width");
    bodyClientWidth.textContent = f(document.body.clientWidth);
    const bodyClientHeight = document.getElementById("body-client-height");
    bodyClientHeight.textContent = f(document.body.clientHeight);
};

const f = (n) => String(n).padStart(4, "0");

window.addEventListener("load", () => {
    showInfo();
});

window.addEventListener("resize", () => {
    showInfo();
});
