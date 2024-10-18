var socket = io();

function displayCurrentTime() {
    console.log("displayCurrentTime")
    const currentTimeElement = document.getElementById('currentTime');
    const currentTime = moment();
    const formattedTime = currentTime.format('YYYY-MM-DD HH:mm:ss');
    currentTimeElement.textContent = `Current time: ${formattedTime}`;   
}

document.addEventListener("DOMContentLoaded", function(){

    
    const messageInputEl = document.getElementById("message-input")
    const myBtnEl = document.getElementById("my-button")
    const messageList = document.getElementById("messageList")
    


    function callApiPlayground() {
        console.log("callApiPlayground")


        const userMessageText = messageInputEl.value.trim();
        const textAreaEl = document.getElementById("text-area")


        axios.post('/api/playground', { user_input: userMessageText })
            .then(response => {

                console.log(response.data);
                   
                textAreaEl.className = "textarea"
                textAreaEl.textContent = response.data
                

            })
            .catch(error => {
                console.error(error);
            });
            messageInputEl.value = "";
            messageInputEl.focus()
            

    };



    myBtnEl.addEventListener("click", callApiPlayground);

    messageInputEl.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            callApiPlayground()
        }
    });

    // listening to values from backend
    socket.on("square", data => {
        console.log(data)
        const elMessage = document.createElement("li")
        elMessage.textContent = data
        messageList.appendChild(elMessage)
    })




});



