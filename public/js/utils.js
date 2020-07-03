// If no languagePluginLoader is available, fallback to Pyodide from CDN
if( !window.languagePluginLoader ) {
	var cdn = "https://pyodide-cdn2.iodide.io/v0.15.0/full/pyodide.js";
	console.debug(`Using Pyodide fallback from ${cdn}...`);
	var script = document.createElement("script");
	script.setAttribute("src", cdn);
	document.getElementsByTagName("head")[0].appendChild(script);
}
else {
	console.debug(`Using locally installed Pyodide...`);
}

/*** SW for large Pyodide files ***/
/*
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
        navigator.serviceWorker.register('/vi/s/sw.js');
    });
}
*/

var preventViUnloading = 0;

window.onbeforeunload =
    function(e)
    {
        //console.log("preventViUnloading = %d", preventViUnloading);

        if( preventViUnloading )
        {
            e.returnValue = "Any unsafed data will get lost!";
            return e.returnValue;
        }
    };

function preventBack()
{
    window.history.forward();
}

setTimeout(preventBack(), 0);
window.onunload = function(){};
