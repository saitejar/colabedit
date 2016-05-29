/**
 * Created by ranuva on 5/28/16.
 */


var recentVersion = 0;
var pendingChanges = [];
var sentChanges = [];
var curDocText = '';
var insertText = function (event) {
    var ch = event.charCode;
    var pos = document.getElementById("textarea").editor.getSelectedRange()[0];
    var tag = PPS.insert(pos, ch);
    pendingChanges.push({'insert': [tag, ch]});
};

var deleteText = function (event) {
    var key = event.keyCode;
    var pos = document.getElementById("textarea").editor.getSelectedRange();
    if (key == 8) {
        if(pos[0]==0 && pos[1]==0){
            return;
        }
        for(var p=pos[0]+1; p<=pos[1]; p++){
            PPS.delete(p);
        }
        if (pos[0] == pos[1]) {
            pendingChanges.push({'delete': [pos[0], pos[1]]})
        }
        else {
            pendingChanges.push({'delete': [pos[0], pos[1] - 1]})
        }
    }// backspace
};

var pasteText = function (pasteInfo) {
    var ch, tag;
    for(var step=pasteInfo.start; step<=pasteInfo.end; step++){
        ch = pasteInfo.text.charCodeAt(step-pasteInfo.start);
        tag = PPS.insert(step, ch);
        pendingChanges.push({'insert': [tag, ch]});
    }
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

var PPS = function(){
    var ppsTags = [0, 1];
    ppsTags.sort();
    var pps = new Map();
    var ppsAck = new Map();
    pps.set(0,0);
    pps.set(1,0);
    ppsAck.set(0, true);
    ppsAck.set(1, true);
    return {

        hide: function (tag) {
            pps.set(tag, 0);
            ppsAck.set(tag, false);
        },

        delete: function (pos) {
            var count = 0;
            var found = false;
            var tag;
            for (tag in ppsTags) {
                if(pps.get(parseFloat(tag)) != 0){
                    count+=1;
                }
                if(count == pos){
                    found = true;
                    break;
                }
            }
            if(found == true)
                PPS.hide(ppsTags[count]);
        },

        add: function (tagx, tagy, ch) {
            var tag = (tagx+tagy)/2;
            pps.set(tag, ch);
            ppsTags.push(tag);
            ppsTags.sort();
            ppsAck.set(tag, false);
            return tag;
        },
        insert: function(pos, ch){
            var index = 0, numClients = 1;
            var tag, lowB = 0;
            var found = false;
            ppsTags.sort();
            for (tag in ppsTags) {
                if(pps.get(ppsTags[tag]) != 0){
                    lowB += 1;
                }
                if(lowB == pos){
                    found = true;
                    break;
                }
            }

            var lB = lowB, rB = lowB+1, lAck, rAck, ltag, rtag;
            ltag = ppsTags[lB]; rtag = ppsTags[rB];
            if(ppsAck.get(ppsTags[lB])==false && ppsAck.get(ppsTags[rB])==true){
                var left = ppsTags.slice(0,lB).reverse();
                for(tag in left) {
                    if (ppsAck.get(left[tag]) == true) {
                        lAck = left[tag];
                        break;
                    }
                }
                ltag = ppsTags[lB];
                rtag = lAck + (index + 1) * (ppsTags[rB] - lAck) / numClients;

            }
            else if(ppsAck.get(ppsTags[lB])==true && ppsAck.get(ppsTags[rB])==false){
                var right = ppsTags.slice(rB+1,ppsTags.length);
                for(tag in right) {
                    if (ppsAck.get(right[tag]) == true) {
                        rAck = right[tag];
                        break;
                    }
                }
                rtag = ppsTags[rB];
                ltag = ppsTags[lB] + index  * (rAck - ppsTags[lB]) / numClients;
            }
            if(found == true){
                tag = PPS.add(ltag, rtag, ch);
                return tag;
            }
            return null;
        },
        
        piece: function(lb, ub) {
            var lP = ppsTags.indexOf(lb), rP = ppsTags.indexOf(ub), tag;
            if(lP<0 && rP<0){
                return null;
            }
            var curText = "";
            var slice = ppsTags.slice(lP, rP+1)
            for(tag in slice){
                tag = slice[tag];
                if(pps.get(tag) != 0) {
                    curText += String.fromCharCode(pps.get(tag));
                }
            }
            return curText;
        }
    }
}();