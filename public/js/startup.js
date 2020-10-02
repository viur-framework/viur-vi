function postMessageChannelToFrame(frameId, origin, channel) {
	document.getElementById(frameId).contentWindow.postMessage("set-message-channel", origin, [channel])
}

window.addEventListener(
		"load",
		(event) => {
			window.init = new init({
				// Prelude to be executed before fetching local modules
				prelude: ``,

				// Fetch location for locally available Python modules
				fetch: {
					"flare": {
						"path": "flare/flare"
					},
					"vi": {
						"path": "."
					}
				}
			});
		}
);