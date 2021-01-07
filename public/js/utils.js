
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
