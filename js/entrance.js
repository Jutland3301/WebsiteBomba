const entranceScreen =
    document.getElementById("entrance-screen");

const entranceButton =
    document.getElementById("entrance-button");

const entranceAudio =
    document.getElementById("bgm");


if (entranceScreen && entranceButton) {

    const alreadyEntered =
        sessionStorage.getItem("websiteEntered") === "true";


    // Already entered during this tab session:
    // skip the entrance completely.
    if (alreadyEntered) {

        entranceScreen.remove();

    } else {

        entranceButton.addEventListener(
            "click",
            async () => {

                // Remember that the entrance has been passed.
                sessionStorage.setItem(
                    "websiteEntered",
                    "true"
                );

                const enabled =
                    localStorage.getItem("bgmEnabled") !== "false";

                if (enabled && entranceAudio) {

                    try {
                        await entranceAudio.play();
                    } catch {
                        // Continue entering even if playback fails.
                    }
                }

                entranceScreen.classList.add(
                    "entrance-hidden"
                );

                setTimeout(
                    () => {
                        entranceScreen.remove();
                    },
                    250
                );
            }
        );
    }
}