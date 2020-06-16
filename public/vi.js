

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
	return;
}
