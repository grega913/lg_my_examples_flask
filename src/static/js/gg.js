




document.addEventListener("DOMContentLoaded", function(){

    const myBtnEl = document.getElementById("my-button")
    const messageInputEl = document.getElementById("message-input")
    



    function callApiGg() {
        console.log("callApiGg")


        const userMessageText = messageInputEl.value.trim();

        const textAreaEl = document.getElementById("text-area")


        axios.post('/api/gg', { user_input: userMessageText })
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



    myBtnEl.addEventListener("click", callApiGg);

    messageInputEl.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            callApiGg()
        }
    });







});












