const showInfo = () => {
  const windowInnerWidth = document.getElementById("window-inner-width");
  windowInnerWidth.textContent = window.innerWidth;
  const windowInnerHeight = document.getElementById("window-inner-height");
  windowInnerHeight.textContent = window.innerHeight;

  const htmlClientWidth = document.getElementById("html-client-width");
  htmlClientWidth.textContent = document.documentElement.clientWidth;
  const htmlClientHeight = document.getElementById("html-client-height");
  htmlClientHeight.textContent = document.documentElement.clientHeight;

  const bodyClientWidth = document.getElementById("body-client-width");
  bodyClientWidth.textContent = document.body.clientWidth;
  const bodyClientHeight = document.getElementById("body-client-height");
  bodyClientHeight.textContent = document.body.clientHeight;
};

window.addEventListener("load", () => {
  showInfo();
});

window.addEventListener("resize", () => {
  showInfo();
});
