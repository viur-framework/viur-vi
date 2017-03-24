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

/*** BUGSNAG ***/

function logError(msg, url, line, col, error)
{
    if( !url || url == "" || !url.indexOf("http://127.0.0.1")
                                || !url.indexOf("http://localhost") )
        return; /* Ignore */

    // DISABLED FOR NOW IT MAKES NO SENSE IN DEVELOPMENT VERSIONS...
    //Bugsnag.notify(error.toString(), msg.toString());
}

/*** ONLY PERMIT PASTING OF RAW TEXT ***/

function removeTags(e)
{
    var clipboardData = e.clipboardData || window.clipboardData;
    var pastedData = clipboardData.getData("Text");

    cleanedData = pastedData.replace(/<\/?[^>]+(>|$)/g, "");
    //console.log(e.target);

    if((e.target.tagName.toLowerCase() === "div")
        || (e.target.tagName.toLowerCase() === "textarea"))
    {
        e.stopPropagation();
        e.preventDefault();

        e.target.innerHTML = newPaste(e.target, e.target.innerHTML, cleanedData);
    }
    else if(e.target.tagName.toLowerCase() === "input")
    {
        e.stopPropagation();
        e.preventDefault();

        e.target.value = newPaste(e.target, e.target.value, cleanedData);
    }
}

function newPaste(target, text, paste)
{
    var pos = getPosition(target);
    return text.substr(0, pos) + paste + text.substr(pos);
}

function getPosition(elem)
{
    var pos = 0;

    // IE Support
    if(document.selection)
    {
        elem.focus();
        var sel = document.selection.createRange();
        sel.moveStart('character', -elem.value.length);
        pos = sel.text.length;
    }
    // Firefox & Chrome support
    else if(elem.selectionStart || elem.selectionStart == '0')
        pos = elem.selectionStart;

    return pos;
}

document.addEventListener("paste", removeTags);
