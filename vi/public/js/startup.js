function postMessageChannelToFrame(frameId, origin, channel) {
	document.getElementById(frameId).contentWindow.postMessage("set-message-channel", origin, [channel])
}

window.addEventListener(
	"load",
	(event) => {
		window.init = new flare({
			// Prelude to be executed before fetching local modules
			prelude: ``,

			// Fetch location for locally available Python modules
			fetch: {
				"flare": {
					"path": "flare/flare",
					"optional": true //if this not exists you musst deliver this with in the root package
				},
				"vi": {
					"path": "."
				},
				"vi_plugins":{
					"path":"/vi_plugins/s",
					"optional": true
				}
			}
		});
	}
);
