var socket = io();


document.addEventListener("DOMContentLoaded", function(){

    
    const messageInputEl = document.getElementById("message-input")
    const myBtnEl = document.getElementById("my-button")
    const loadingSpinner = document.getElementById('loading-spinner')
    loadingSpinner.style.display = 'none'


    function callApiDatapoint3() {
        console.log("callApiDatapoint3")

        const userMessageText = messageInputEl.value.trim();

        const textAreaEl = document.getElementById("text-area")

        const loadingSpinner = document.getElementById('loading-spinner')
        loadingSpinner.style.display = 'block';

        axios.post('/api/quick_start/part3', { user_input: userMessageText })
            .then(response => {

                loadingSpinner.style.display = 'none'
                console.log(response.data);
                   
                textAreaEl.className = "textarea"
                textAreaEl.textContent = response.data
                

            })
            .catch(error => {
                console.error(error);
                loadingSpinner.style.display = 'none';
            });
            messageInputEl.value = "";
            messageInputEl.focus()

    };



    myBtnEl.addEventListener("click", callApiDatapoint3);

    messageInputEl.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            callApiDatapoint3()
        }
    });


    socket.on("graph_part3", data => {
        console.log(data)
        const elMessage = document.createElement("li")
        elMessage.textContent = data
        messageList.appendChild(elMessage)
    })





});