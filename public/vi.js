/*** CHECK BROWSER COMPATIBLITY ***/

/* We support Chrome, Firefox, Safari and MSIE >= 11 */
if( window.location.hash != "#skipbd"
        && !( window.chrome // Chromium
                || typeof InstallTrigger !== "undefined" //Firefox
                    || navigator.userAgent.toLowerCase().indexOf("safari") > -1 //Safari
                    || ( Object.hasOwnProperty.call( window, "ActiveXObject" )
                            && !window.ActiveXObject ) //MSIE11
                ) )
    window.location.href = "/vi/s/notsupported.html";

/*** CHECK HTTPS PROTOCOL USE ***/

if( window.location.protocol != "https:"
    && window.location.hostname != "localhost"
    && window.location.hostname != "127.0.0.1" )
    window.location.href = "https://" + window.location.hostname + window.location.pathname;

/*** PREVENT FROM UNLOADING ***/

var preventViUnloading = 0;
/** prevent unloading! **/

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

