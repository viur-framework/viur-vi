
/** prevent unloading! **/
if (window.name!="fenster1") {
    window.onbeforeunload = function() { return "Alle nicht gespeicherte Daten gehen verloren!"; };
} else {
    window.close();
}


function preventBack(){window.history.forward();}
    setTimeout("preventBack()", 0);
    window.onunload=function(){null};