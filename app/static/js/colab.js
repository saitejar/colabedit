/**
 * Created by ranuva on 5/28/16.
 */

function logOut() {
    var guestUserName = document.getElementById("UserName").value;
    document.getElementById("loginSection").style.display = "block";
    document.getElementById("textareaSection").style.display = "none";
    localStorage.removeItem("userCount");
    localStorage.removeItem("userPosition");
    if (typeof heartBeatSetTimeout !== 'undefined') {
        clearTimeout(heartBeatSetTimeout);
    }
    if (typeof sendChangesSetTimeout !== 'undefined') {
        clearTimeout(sendChangesSetTimeout);
    }
    if (typeof getUserNamesSetTimeout !== 'undefined') {
        clearTimeout(getUserNamesSetTimeout);
    }

    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        eraseCookie(cookies[i].split("=")[0]);
    }

    $.ajax({
        url: '/deinitializeCall',
        type: 'POST',
        dataType: 'json',
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify({userName: guestUserName}),
        success: function (data, sStatus, jqXHR) {
            console.log(data);
        }
    });
}


var recentVersion = 0;
var pendingChanges = {};

var curDocText = '';
var ppsTags = ['0', '1'];
var pps = new Map();
var ppsAck = new Map();
pps.set('0', 0);
pps.set('1', 0);
ppsAck.set('0', true);
ppsAck.set('1', true);
ppsTags.sort();
var acknowledged = true;
var lastReceivedGreatestSeqNum;


var insertText = function (event) {
    var ch = event.charCode;
    var pos = document.getElementById("textarea").editor.getSelectedRange()[0];
    var tag = PPS.insert(pos, ch);
    console.log("tag = " + tag);
    pendingChanges[tag] = ch;
    console.log(pendingChanges);
};

var deleteText = function (event) {
    var key = event.keyCode, deleteTag;
    var pos = document.getElementById("textarea").editor.getSelectedRange();
    if (key == 8) {
        console.log('deleted');
        if (pos[0] != 0 && pos[1] == pos[0]) {
            deleteTag = PPS.delete(pos[0]);
            if (deleteTag != null) {
                PPS.hide(deleteTag);
                pendingChanges[deleteTag] = 0;
            }
        }
        else if(pos[1]>pos[0]){
            var deleteTags = [];
            for (var p = pos[0] + 1; p <= pos[1]; p++) {
                deleteTag = PPS.delete(p);
                if (deleteTag != null) {
                    deleteTags.push(deleteTag);
                }
            }
            for(p in deleteTags){
                PPS.hide(deleteTags[p]);
                pendingChanges[deleteTags[p]] = 0;
            }
        }
    }// backspace ?
};

var pasteText = function (pasteInfo) {
    var ch, tag;
    for (var step = pasteInfo.start; step <= pasteInfo.end; step++) {
        ch = pasteInfo.text.charCodeAt(step - pasteInfo.start);
        tag = PPS.insert(step, ch);
        pendingChanges[tag] = ch;
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

var PPS = function () {
    return {
        hide: function (tag) {
            tag = String(tag);
            pps.set(tag, 0);
            ppsAck.set(tag, false);
        },

        index: function (tag) {
            ppsTags.sort();
            var pos = 0;
            for (var t in ppsTags) {
                if (ppsTags[t] == tag){
                    return pos;
                }
                if (pps.get(ppsTags[t]) != 0) {
                    pos += 1;
                }
            }
            return -1;
        },

        delete: function (pos) {
            var count = 0;
            var found = false;
            var tag;
            ppsTags.sort();
            var deleteTag= '0';
            for (tag in ppsTags) {
                if (pps.get(ppsTags[tag]) != 0) {
                    count += 1;
                }
                if (count == pos) {
                    found = true;
                    deleteTag = ppsTags[count];
                    break;
                }
            }
            if (found == true) {
                return deleteTag;
            }
            return null;
        },
        attach: function (tag, ch) {
            tag = String(tag);
            var element = document.querySelector("trix-editor"), pos;
            ppsAck.set(tag, true);
            ch = parseInt(ch);
            if (ch != 0) {
                pps.set(tag, ch);
                ppsTags.push(tag);
                ppsTags.sort();
                pos = PPS.index(tag);
                var currentCurPos = document.getElementById("textarea").editor.getSelectedRange()[0];
                element.editor.setSelectedRange([pos, pos]);
                element.editor.insertString(String.fromCharCode(ch));
                if(pos > currentCurPos)
                    element.editor.setSelectedRange([currentCurPos, currentCurPos]);
                else if(pos <= (currentCurPos - 1))
                    element.editor.setSelectedRange([currentCurPos+1, currentCurPos+1]);
            }
            else {
                    var currentCurPos = document.getElementById("textarea").editor.getSelectedRange()[0];
                    pos = PPS.index(tag);
                    element.editor.setSelectedRange([pos + 1, pos + 1]);
                    element.editor.deleteInDirection("backward");
                    pps.set(tag, ch);
                    if (pos > currentCurPos) {
                       element.editor.setSelectedRange([currentCurPos, currentCurPos]);
                    } else {
                       element.editor.setSelectedRange([currentCurPos - 1, currentCurPos - 1]);
                    }
            }
        },
        add: function (tagx, tagy, ch) {
            tagx = Big(tagx);
            tagy = Big(tagy);
            var tag = (tagx.add(tagy)).div(2) + '';
            pps.set(tag, ch);
            ppsTags.push(tag);
            ppsTags.sort();
            ppsAck.set(tag, false);
            return tag;
        },
        insert: function (pos, ch) {
            Big.DP = 20000;
            var index = Big(localStorage.getItem('userPosition'));
            var numClients = Big(localStorage.getItem('userCount'));
            var tag, lowB = 0;
            var found = false;
            ppsTags.sort();
            for (tag in ppsTags) {
                if (pps.get(ppsTags[tag]) != 0) {
                    lowB += 1;
                }
                if (lowB == pos) {
                    found = true;
                    break;
                }
            }


            var lB = lowB, rB = lowB + 1, lAck, rAck, ltag, rtag;
            ltag = Big(ppsTags[lB]);
            rtag = Big(ppsTags[rB]);
            if (ppsAck.get(ppsTags[lB]) == false && ppsAck.get(ppsTags[rB]) == true) {
                var left = ppsTags.slice(0, lB).reverse();
                for (tag in left) {
                    if (ppsAck.get(left[tag]) == true) {
                        lAck = Big(left[tag]);
                        break;
                    }
                }
                ltag = Big(ppsTags[lB]);
                rtag = lAck.add((index.add(1)).times(Big(ppsTags[rB]).minus(lAck)).div(numClients));

            }
            else if (ppsAck.get(ppsTags[lB]) == true && ppsAck.get(ppsTags[rB]) == false) {
                var right = ppsTags.slice(rB + 1, ppsTags.length);
                for (tag in right) {
                    if (ppsAck.get(right[tag]) == true) {
                        rAck = Big(right[tag]);
                        break;
                    }
                }
                rtag = Big(ppsTags[rB]);
                ltag = Big(ppsTags[lB]).add(index.times(rAck.minus(Big(ppsTags[lB]))).div(Big(numClients)));
            }
            else if (ppsAck.get(ppsTags[lB]) == true && ppsAck.get(ppsTags[rB]) == true) {
                ltag = Big(ppsTags[lB]).add(index.times(Big(ppsTags[rB]).minus(Big(ppsTags[lB]))).div(numClients));
                rtag = Big(ppsTags[lB]).add((index.add(1)).times(Big(ppsTags[rB]).minus(Big(ppsTags[lB]))).div(numClients));
            }
            else if (ppsAck.get(ppsTags[lB]) == false && ppsAck.get(ppsTags[rB]) == false) {
                ltag = Big(ppsTags[lB]);
                rtag = Big(ppsTags[rB]);
            }
            else {

            }
            if (found == true) {
                ltag = ltag + '';
                rtag = rtag + '';
                tag = PPS.add(ltag, rtag, ch);
                return tag;
            }
            return null;
        },


        piece: function (lb, ub) {
            ppsTags.sort();
            var lP = ppsTags.indexOf(String(lb)), rP = ppsTags.indexOf(String(ub)), tag;
            if (lP < 0 || rP < 0) {
                return null;
            }
            var curText = "";
            var slice = ppsTags.slice(lP, rP + 1)
            for (var t in slice) {
                tag = slice[t];
                if (pps.get(tag) != 0) {
                    curText += String.fromCharCode(pps.get(tag));
                }
            }
            return curText;
        }
    }
}();

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function createCookie(name, value, days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        var expires = "; expires=" + date.toGMTString();
    }
    else var expires = "";
    document.cookie = name + "=" + value + expires + "; path=/";
}
function eraseCookie(name) {
    createCookie(name, "", -1);
}

var flag = 0;

function heartbeat(guestName) {

    var heartBeatSetTimeout = setInterval(function () {
            var times = new Date().getTime();
            var position = document.getElementById("textarea").editor.getSelectedRange()[0];
            PPS.piece(0, 1);
            $.ajax({
                url: '/heartbeat',
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify({
                    userName: guestName,
                    timeStamp: times,
                    cursorPosition: position,
                    lastGreatestSequenceNumber: lastReceivedGreatestSeqNum
                }),
                success: function (data) {

                    if (data != 'None') {
                        console.log("heartbeat sent and received : User Count : " + data.userCount);
                        console.log("heartbeat sent and received : User Position : " + data.userPosition);
                        console.log("ENTIRE : " + JSON.stringify(data));
                        if (typeof(Storage) !== "undefined") {
                            localStorage.setItem("userCount", parseInt(data.userCount));
                            localStorage.setItem("userPosition", parseInt(data.userPosition));
                        }
                        console.log("Transaction : " + JSON.stringify(data.transactions));
                        if (JSON.stringify(data.transactions) != "{}") {
                            $.each(data.transactions, function (key, value) {
                                var id = parseInt(key);
                                if (id > lastReceivedGreatestSeqNum) {
                                    lastReceivedGreatestSeqNum = id;
                                }
                                console.log("ID : " + id);

                                $.each(value, function (k, v) {
                                    console.log("CHANGE: " + k + " , " + v);
                                    PPS.attach(k, v);
                                });
                            });
                        }
                    }
                }
            });
        }
        ,
        500
    ); //every 5 seconds
}

function startSendChanges() {
    var sendChangesSetTimeout = setInterval(function () {
            var times = new Date().getTime();
            var position = document.getElementById("textarea").editor.getSelectedRange()[0];
            if (acknowledged == true && Object.keys(pendingChanges).length > 0) {

                acknowledged = false;
                var sentChanges = {};
                console.log("pending: " + pendingChanges);
                for (key in pendingChanges) {
                    sentChanges[key] = pendingChanges[key];
                    delete pendingChanges[key];
                    console.log("Sentchanges: " + key);
                }
                var guestusername = document.getElementById("UserName").value;
                $.ajax({
                    url: '/sendChanges',
                    type: 'POST',
                    dataType: 'json',
                    timeout: 3000,
                    tryCounter: 0,
                    retryLimit: 10,
                    contentType: "application/json;charset=UTF-8",
                    data: JSON.stringify({
                        changesToBePushed: sentChanges,
                        userName : guestusername
                    }),
                    success: function (data, sStatus, jqXHR) {
                        acknowledged = true;
                        console.log("(insert) successfully sent and received the message in send changes: " + data);
                    },
                    error: function (xhr, textStatus, errorThrown) {
                        if (textStatus == 'timeout') {
                            this.tryCounter++;
                            if (this.tryCounter <= this.retryLimit) {
                                $.ajax(this);
                                return;
                            }
                            return;
                        }
                        if (xhr.status == 500) {
                            console.log("Server error while inserting");
                        } else {
                            console.log("unknown error while inserting");
                        }
                    }
                });
            }

        }
        ,
        1000
    );
};

function getUserNames() {
    var getUserNamesSetTimeout = setInterval(function () {
            $.ajax({
                url: '/sendUserNames',
                type: 'POST',
                dataType: 'json',
                timeout: 3000,
                tryCounter: 0,
                retryLimit: 10,
                contentType: "application/json;charset=UTF-8",
                data: JSON.stringify({
                    id: ''
                }),
                success: function (data, sStatus, jqXHR) {
                    console.log("USERS " + JSON.stringify(data));
                    document.getElementById("userNames").innerHTML = "";
                    for(var i = 0; i < data.length; i++){
                        document.getElementById("userNames").innerHTML += "<br/><img src='images/user.png' width='40px'/><span style='font-weight:bold;font-size:large'>";
                        document.getElementById("userNames").innerHTML += data[i];
                        document.getElementById("userNames").innerHTML += "</span>";
                        document.getElementById("userNames").innerHTML += "<br/>";
                    }

                },
                error: function (xhr, textStatus, errorThrown) {
                    if (textStatus == 'timeout') {
                        this.tryCounter++;
                        if (this.tryCounter <= this.retryLimit) {
                            $.ajax(this);
                            return;
                        }
                        return;
                    }
                    if (xhr.status == 500) {
                        console.log("Server error while inserting");
                    } else {
                        console.log("unknown error while inserting");
                    }
                }
            });
        }
        ,
        5000
    );
};

function performTasksForGuest(guestName) {
    document.getElementById("invalidGuestName").style.display = "none";
    document.getElementById("loginSection").style.display = "none";
    document.getElementById("textareaSection").style.display = "block";
    document.getElementById('textarea').value = "";
    document.getElementById('textarea').addEventListener("keypress", insertText);
    document.getElementById('textarea').addEventListener("keydown", deleteText);
    document.getElementById('textarea').addEventListener("paste", detectPaste);
    document.getElementById("displayName").textContent = guestName;
    lastReceivedGreatestSeqNum = -1;
    heartbeat(guestName);
    startSendChanges();
    getUserNames();
}


function loginAsGuest() {
    var
        guestName = document.getElementById("UserName").value;

    $.ajax({
        url: '/login',
        type: 'POST',
        dataType: 'json',
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify({userName: guestName}),
        success: function (data, sStatus, jqXHR) {
            if (data == "invalid") {
                document.getElementById("invalidGuestName").style.display = "block";
            } else {
                console.log("User Count : " + data.userCount + ", User pos : " + data.userPosition);
                if (typeof(Storage) !== "undefined") {
                    localStorage.setItem("userCount", parseInt(data.userCount));
                    localStorage.setItem("userPosition", parseInt(data.userPosition));
                }
                createCookie("guestCookie", guestName, 1);
                performTasksForGuest(guestName);
            }
        }
    });
}


function clearText() {
    $.ajax({
        url: '/clearTextArea',
        type: 'POST',
        dataType: 'json',
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify({userName: ''}),
        success: function (data, sStatus, jqXHR) {
            console.log("cleared");
        }
    });
}

window.onload = function () {
    logOut();
}