/**
 * Created by ranuva on 5/28/16.
 */


var recentVersion = 0;
var pendingChanges = [];
var sentChanges = [];
var curDocText = '';
var insertText = function (event) {
    console.log(event.charCode);
    var ch = event.charCode;
    var p = document.getElementById("textarea").editor.getSelectedRange()[0];
    pendingChanges.push({'insert': {p: ch}});
};

var deleteText = function (event) {
    var key = event.keyCode;
    var pos = document.getElementById("textarea").editor.getSelectedRange();
    if (key == 8) {
        if (pos[0] == pos[1]) {
            pendingChanges.push({'delete': [pos[0], pos[1]]})
        }
        else {
            pendingChanges.push({'delete': [pos[0], pos[1] - 1]})
        }
    }// backspace
};

var pasteText = function (pasteInfo) {
    alert(pasteInfo.start + ',' + pasteInfo.end + ', text = ' + pasteInfo.text);
};

var detectPaste = function (e) {
    var textarea = document.getElementById("textarea");
    var sel = getTextAreaSelection(textarea);
    var clipboardData = e.clipboardData || e.originalEvent.clipboardData || window.clipboardData;
    var pastedData = clipboardData.getData('text');
    window.setTimeout(function () {
        var pastedTextLength = pastedData.length;
        var end = sel.end - 1;
        var start = sel.start - pastedTextLength;
        pasteText({
            start: start,
            end: end,
            length: pastedTextLength,
            text: pastedData
        });
    }, 1);
};

function getTextAreaSelection(textarea) {
    var start = textarea.editor.getSelectedRange()[0], end = textarea.editor.getSelectedRange()[1];
    return {
        start: start,
        end: end,
        length: end - start,
        text: textarea.value.slice(start, end)
    };
}

var PPS = {
    someMethod: function () {
        console.log(this.defaults);
    }
};