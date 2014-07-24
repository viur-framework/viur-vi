

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


function logError(msg, url, line, col, error) {
    if( url.toLowerCase().indexOf("http://127.0.0.1")==0 || url.toLowerCase().indexOf("http://localhost")==0 ) {
        return;
    }
    Bugsnag.notify(error.toString(), msg.toString());
}