document.querySelectorAll(".blink-image").forEach((element) => {

    const enabled =
        element.dataset.blink === "true";

    if (!enabled) {
        return;
    }

    const visibleTime =
        Number(element.dataset.visible) * 1000;

    const hiddenTime =
        Number(element.dataset.hidden) * 1000;

    function show() {

        element.style.visibility = "visible";

        setTimeout(
            hide,
            visibleTime
        );
    }

    function hide() {

        element.style.visibility = "hidden";

        setTimeout(
            show,
            hiddenTime
        );
    }

    show();
});