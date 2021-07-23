window.onload = function () {
    var el = document.getElementById("pyscripter");
    var version = "# version: Python3\n\n";
    var codeAreaTip = "# please edit your code here:\n";
    var codeStart = "# code start\n\n";
    var codeEnd = "# code end\n\n";
    var codeTip = "'''\nThis function is the entry of this program and\nit must be return your answer of current question.\n'''\n";
    var code = "def solution():\n\tpass";
    var initValue = version + code;//version + codeAreaTip + codeStart + codeEnd + codeTip + code;
    var myCodeMirror = CodeMirror.fromTextArea(el, {
        mode: "python", // Language mode
        theme: "neo", // theme
        keyMap: "sublime", // Fast key style
        lineNumbers: true, // set number
        smartIndent: true, // smart indent
        indentUnit: 4, // Smart indent in 4 spaces
        indentWithTabs: true, // Smart indent with tabs
        lineWrapping: true, //
        // Add line number display, folder and syntax detector to the slot
        gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter", "CodeMirror-lint-markers"],
        foldGutter: true, // Enable code folding in slots
        autofocus: true, // Autofocus
        matchBrackets: true, // Match end symbols, such as "],}"
        autoCloseBrackets: true, // Auto close symbol
        styleActiveLine: true, // Display the style of the selected row
       // lint: {
       //     "getAnnotations": pythonValidator,
       //     "async": true,
       // }
    });
    // Set the initial text, which can also be configured in the fromTextArea
    myCodeMirror.setOption("value", initValue);
    // Editor key listening
    //myCodeMirror.on("keypress", function() {
        // Show smart tips
    //    myCodeMirror.showHint(); // Note that the code at line 131 of show-hint.js in CodeMirror library is commented (code completion is blocked and intelligent prompt is provided)
    //});
};
