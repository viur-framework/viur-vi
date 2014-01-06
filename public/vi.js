
/** prevent unloading! **/
window.onbeforeunload = function() { return "Alle nicht gespeicherte Daten gehen verloren!"; };

function preventBack(){window.history.forward();}
    setTimeout("preventBack()", 0);
    window.onunload=function(){null};