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

// If no languagePluginLoader is available, fallback to Pyodide from CDN
if( !window.languagePluginLoader ) {
	var cdn = "https://pyodide-cdn2.iodide.io/v0.16.1/full/pyodide.js";
	console.debug(`Using Pyodide fallback from ${cdn}...`);
	var script = document.createElement("script");
	script.setAttribute("src", cdn);
	document.getElementsByTagName("head")[0].appendChild(script);
}
else {
	console.debug(`Using locally installed Pyodide...`);
}
