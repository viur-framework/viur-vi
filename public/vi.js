

var preventViUnloading = 0;
/** prevent unloading! **/

window.onbeforeunload =
    function(e)
    {
        console.log("preventViUnloading = %d", preventViUnloading);

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

function logError(msg, url, line, col, error)
{
    if( !url || url == "" || !url.indexOf("http://127.0.0.1")
                                || !url.indexOf("http://localhost") )
        return; /* Ignore */

    Bugsnag.notify(error.toString(), msg.toString());
}
