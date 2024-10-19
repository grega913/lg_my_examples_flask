var socket = io();


document.addEventListener("DOMContentLoaded", function(){

    
    const messageInputEl = document.getElementById("message-input")
    const myBtnEl = document.getElementById("my-button")
    const loadingSpinner = document.getElementById('loading-spinner')
    loadingSpinner.style.display = 'none'

    const btnProceed = document.getElementById("btnProceed")
    btnProceed.style.display = "none"
   


    function callApiDatapoint4() {
        console.log("callApiDatapoint4")

        const userMessageText = messageInputEl.value.trim();

        const textAreaEl = document.getElementById("text-area")

        const loadingSpinner = document.getElementById('loading-spinner')
        loadingSpinner.style.display = 'block';

        axios.post('/api/quick_start/part4', { user_input: userMessageText })
            .then(response => {

                loadingSpinner.style.display = 'none'
                console.log(response.data);

                textAreaEl.className = "textarea"
                textAreaEl.textContent = response.data

                if (response.data == "tools") {
                    console.log("tools indeed")
                    btnProceed.style.display = "block"
                }
               

            })
            .catch(error => {
                console.error(error);
                loadingSpinner.style.display = 'none';
            });
            messageInputEl.value = "";
            messageInputEl.focus()

    };



    myBtnEl.addEventListener("click", callApiDatapoint4);

    messageInputEl.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            callApiDatapoint4()
        }
    });





    socket.on("graph_part4", data => {
        console.log(data)
        const elMessage = document.createElement("li")
        elMessage.textContent = data
        messageList.appendChild(elMessage)
    })





});




function btnProceed() {
    console.log("btnTest")
    // Get the button element
    const btnOne = document.getElementById('btnProceed');

    // Add an event listener to the button
    btnOne.addEventListener('click', function() {
    // Call the function to log a message to the console
        console.log('Proceed Btn clicked!');
        socket.emit("part4_proceed", true)
    });
}