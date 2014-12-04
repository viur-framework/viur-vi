

var preventViUnloading = true;
/** prevent unloading! **/
if (window.name!="fenster1") {
    window.onbeforeunload = function() {
        if( preventViUnloading ) {
            return "Alle nicht gespeicherte Daten gehen verloren!";
        } else {
            return null;
        }
    };
} else {
    window.close();
}


function preventBack(){window.history.forward();}
    setTimeout("preventBack()", 0);
    window.onunload=function(){null};


function logError(msg, url, line, col, error)
{
    if( !url || url == "" || !url.indexOf("http://127.0.0.1")
                                || !url.indexOf("http://localhost") )
        return; /* Ignore */

    Bugsnag.notify(error.toString(), msg.toString());
}
