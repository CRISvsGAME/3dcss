class FrameClock {
    private onFrame: ((fps: number) => void) | null;
    private fps = 0;
    private last = performance.now();
    private delta = 0;
    private smooth = 0.1;
    private frame: number | null = null;

    constructor(onFrame: ((fps: number) => void) | null = null) {
        this.onFrame = onFrame;
    }

    private _tick = (now: number = performance.now()): void => {
        this.delta = now - this.last;
        this.last = now;
        this.fps += (1000 / this.delta - this.fps) * this.smooth;

        if (this.onFrame) {
            this.onFrame(this.fps);
        }
    };

    private _loop = (now: number): void => {
        this._tick(now);
        this.frame = requestAnimationFrame(this._loop);
    };

    public start(): void {
        this.last = performance.now();
        this.frame = requestAnimationFrame(this._loop);
    }

    public stop(): void {
        if (this.frame !== null) {
            cancelAnimationFrame(this.frame);
            this.frame = null;
        }
    }
}

const f = (n: number): string => String(n).padStart(4, "0");

const frameClockDisplay = document.getElementById("frame-clock-display");

const frameClock = new FrameClock((fps) => {
    if (frameClockDisplay) {
        frameClockDisplay.textContent = fps.toFixed(0);
    }
});

frameClock.start();

const showInfo = (): void => {
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

window.addEventListener("load", () => {
    showInfo();
});

window.addEventListener("resize", () => {
    showInfo();
});
