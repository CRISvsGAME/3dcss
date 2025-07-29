const showInfo = () => {
  const windowInnerWidth = document.getElementById("window-inner-width");
  windowInnerWidth.textContent = window.innerWidth;
  const windowInnerHeight = document.getElementById("window-inner-height");
  windowInnerHeight.textContent = window.innerHeight;
};

window.addEventListener("load", () => {
  showInfo();
});

window.addEventListener("resize", () => {
  showInfo();
});
