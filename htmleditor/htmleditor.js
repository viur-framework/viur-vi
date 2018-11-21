function summernoteEditor(input) {
	// create summernote instance
	$(input).summernote({
		callbacks: {
			onChange: function (e) {
				var $selectionContainer = $(getSelection().getRangeAt(0).commonAncestorContainer);
				var $editor = $selectionContainer.closest(".note-editable");

				// in case we are joining two paragraphs or styling plain text, prevent span and inline style being inserted
				$editor.find("span[style]").contents().unwrap();
			},
			// clean html/css crud out of copied text before pasting
			onPaste: function (e) {
				var bufferText = ((e.originalEvent || e).clipboardData || window.clipboardData).getData('Text');
				e.preventDefault();
				$(input).summernote('insertText', bufferText);
			}
		},
		lang: 'de-DE',
		toolbar: [
			['style'],
			['Stil', ['bold', 'italic', 'underline']],
			['Alignment', ['alignLeft', 'alignCenter', 'alignRight', 'alignJustify']],
			['elements', ['link', 'viurPicture', 'table']],
			['list', ['ul', 'ol']],
			['indent', ['indentIn', 'indentOut']],
			['history', ['undo', 'redo']],
			['clear'],
			['codeview']
		],
		prettifyHtml: true,
		buttons: {
			alignLeft: customButton('note-icon-align-left', 'Linksbündig (CTRL+SHIFT+L)', 'justifyLeft'),
			alignCenter: customButton('note-icon-align-center', 'Zentrieren (CTRL+SHIFT+E)', 'justifyCenter'),
			alignRight: customButton('note-icon-align-right', 'Rechtsbündig (CTRL+SHIFT+R)', 'justifyRight'),
			alignJustify: customButton('note-icon-align-justify', 'Blocksatz CTRL+SHIFT+J', 'justifyFull'),
			indentIn: customButton('note-icon-align-indent', 'Einrückung + (CTRL+RIGHTBRACKET)', 'indent'),
			indentOut: customButton('note-icon-align-outdent', 'Einrückung - (CTRL+LEFTBRACKET)', 'outdent'),
			viurPicture: viurPictureBtn,
		},
		codemirror: { // codemirror options
			mode: 'text/html',
			htmlMode: true,
			lineNumbers: true
		},
		keyMap: {
			pc: {
				'ENTER': 'insertParagraph',
				'CTRL+Z': 'undo',
				'CTRL+Y': 'redo',
				'TAB': 'tab',
				'SHIFT+TAB': 'untab',
				'CTRL+B': 'bold',
				'CTRL+I': 'italic',
				'CTRL+U': 'underline',
				'CTRL+SHIFT+S': 'strikethrough',
				'CTRL+BACKSLASH': 'removeFormat',
				'CTRL+SHIFT+L': 'justifyLeft',
				'CTRL+SHIFT+E': 'justifyCenter',
				'CTRL+SHIFT+R': 'justifyRight',
				'CTRL+SHIFT+J': 'justifyFull',
				'CTRL+SHIFT+NUM7': 'insertUnorderedList',
				'CTRL+SHIFT+NUM8': 'insertOrderedList',
				'CTRL+LEFTBRACKET': 'outdent',
				'CTRL+RIGHTBRACKET': 'indent',
				'CTRL+NUM0': 'formatPara',
				'CTRL+NUM1': 'formatH1',
				'CTRL+NUM2': 'formatH2',
				'CTRL+NUM3': 'formatH3',
				'CTRL+NUM4': 'formatH4',
				'CTRL+NUM5': 'formatH5',
				'CTRL+NUM6': 'formatH6',
				'CTRL+ENTER': 'insertHorizontalRule',
				'CTRL+K': 'linkDialog.show'
			},

			mac: {
				'ENTER': 'insertParagraph',
				'CMD+Z': 'undo',
				'CMD+SHIFT+Z': 'redo',
				'TAB': 'tab',
				'SHIFT+TAB': 'untab',
				'CMD+B': 'bold',
				'CMD+I': 'italic',
				'CMD+U': 'underline',
				'CMD+SHIFT+S': 'strikethrough',
				'CMD+BACKSLASH': 'removeFormat',
				'CMD+SHIFT+L': 'justifyLeft',
				'CMD+SHIFT+E': 'justifyCenter',
				'CMD+SHIFT+R': 'justifyRight',
				'CMD+SHIFT+J': 'justifyFull',
				'CMD+SHIFT+NUM7': 'insertUnorderedList',
				'CMD+SHIFT+NUM8': 'insertOrderedList',
				'CMD+LEFTBRACKET': 'outdent',
				'CMD+RIGHTBRACKET': 'indent',
				'CMD+NUM0': 'formatPara',
				'CMD+NUM1': 'formatH1',
				'CMD+NUM2': 'formatH2',
				'CMD+NUM3': 'formatH3',
				'CMD+NUM4': 'formatH4',
				'CMD+NUM5': 'formatH5',
				'CMD+NUM6': 'formatH6',
				'CMD+ENTER': 'insertHorizontalRule',
				'CMD+K': 'linkDialog.show'
			}
		},
		styleTags: ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
		focus: true,
		dialogsInBody: true,
		disableDragAndDrop: true,
		airMode: false,
		height: 400,
		styleWithSpan: false
	});

	$('.note-editor').on("focusout", function () {
		setTimeout(function () {
			$(".note-popover").hide();
			$(".note-image-popover").hide();
		}, 100)
	});

	$("*").on("scroll", function () {
		$(".note-popover").hide();
		$(".note-image-popover").hide();
	});

	$.event.addProp('dataTransfer');
	// catch drag events and replace data with plaintext
	$("*").on('dragstart', function (e) {
		var plainStr = e.originalEvent.dataTransfer.getData("text/plain");
		e.dataTransfer.clearData();
		e.dataTransfer.setData("text/plain", plainStr);
	});

	return $(input);
}

window.top.summernoteEditor = summernoteEditor;

function customButton(className, tooltip, invokeCmd) {
	return function (context) {
		var ui = $.summernote.ui;

		// create button
		var button = ui.button({
			contents: '<i class="' + className + '"/>',
			tooltip: tooltip,
			container: 'body',
			click: function () {
				context.invoke(invokeCmd);
			}
		});

		return button.render(); // return button as jquery object
	}
}

var viurPictureBtn = function (context) {
	var ui = $.summernote.ui;

	// create button
	var button = ui.button({
		contents: '<i class="note-icon-picture"/>',
		tooltip: 'Bild',
		container: 'body',
		click: function () {
			var boneName = $(context.layoutInfo.note[0]).data('bonename');
			$('.viur-insert-image-btn[data-bonename="' + boneName + '"]').trigger('click');
		}
	});

	return button.render(); // return button as jquery object
};
