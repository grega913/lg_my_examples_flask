document.addEventListener("DOMContentLoaded", function(){

    
    const messageInputEl = document.getElementById("message-input")
    const myBtnEl = document.getElementById("my-button")
    

    function callApiDatapoint1() {
        console.log("callApiDatapoint1")


        const userMessageText = messageInputEl.value.trim();

        const textAreaEl = document.getElementById("text-area")


        axios.post('/api/quick_start/part1', { user_input: userMessageText })
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



    myBtnEl.addEventListener("click", callApiDatapoint1);

    messageInputEl.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            callApiDatapoint1()
        }
    });



});