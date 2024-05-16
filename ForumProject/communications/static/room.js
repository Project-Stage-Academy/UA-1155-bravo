console.log("Sanity check from room.js.");

const roomName = JSON.parse(document.getElementById('roomName').textContent);

let chatLog = document.querySelector("#chatLog");
let chatMessageInput = document.querySelector("#chatMessageInput");
let chatMessageSend = document.querySelector("#chatMessageSend");
let onlineUsersSelector = document.querySelector("#onlineUsersSelector");

// adds a new option to 'onlineUsersSelector'
function onlineUsersSelectorAdd(value) {
    if (document.querySelector("option[value='" + value + "']")) return;
    let newOption = document.createElement("option");
    newOption.value = value;
    newOption.innerHTML = value;
    onlineUsersSelector.appendChild(newOption);
}

// removes an option from 'onlineUsersSelector'
function onlineUsersSelectorRemove(value) {
    let oldOption = document.querySelector("option[value='" + value + "']");
    if (oldOption !== null) oldOption.remove();
}

// focus 'chatMessageInput' when user opens the page
chatMessageInput.focus();

const ENTER_KEY_CODE = 13;
// submit if the user presses the enter key
chatMessageInput.onkeyup = function(e) {
    if (e.keyCode === ENTER_KEY_CODE) {  // enter key
        chatMessageSend.click();
    }
};

chatMessageSend.onclick = function() {
    if (chatMessageInput.value.length === 0) return;
    chatSocket.send(JSON.stringify({
        "message": chatMessageInput.value,
    }));
    chatMessageInput.value = "";
};

// Function to handle incoming messages
function handleIncomingMessage(data) {
    chatLog.value += `${data.user}: ${data.message}\n`;
    chatLog.scrollTop = chatLog.scrollHeight;
}

// Function to handle user list updates
function handleUserList(data) {
    data.users.forEach(user => onlineUsersSelectorAdd(user));
}

// Function to handle user join
function handleUserJoin(data) {
    chatLog.value += `${data.user} joined the room.\n`;
    onlineUsersSelectorAdd(data.user);
    chatLog.scrollTop = chatLog.scrollHeight;
}

// Function to handle user leave
function handleUserLeave(data) {
    chatLog.value += `${data.user} left the room.\n`;
    onlineUsersSelectorRemove(data.user);
    chatLog.scrollTop = chatLog.scrollHeight;
}

// Function to connect to WebSocket and setup event handlers
function connect() {
    chatSocket = new WebSocket("ws://" + window.location.host + "/ws/chat/" + roomName + "/");

    chatSocket.onopen = function(e) {
        console.log("Successfully connected to the WebSocket.");
    }

    chatSocket.onclose = function(e) {
        console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 2s...");
        setTimeout(function() {
            console.log("Reconnecting...");
            connect();
        }, 2000);
    };

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log(data);

        switch (data.type) {
            case "chat_message":
                handleIncomingMessage(data);
                break;
            case "user_list":
                handleUserList(data);
                break;
            case "user_join":
                handleUserJoin(data);
                break;
            case "user_leave":
                handleUserLeave(data);
                break;
            default:
                console.error("Unknown message type!");
                break;
        }
    };

    chatSocket.onerror = function(err) {
        console.log("WebSocket encountered an error: " + err.message);
        console.log("Closing the socket.");
        chatSocket.close();
    }
}

connect();