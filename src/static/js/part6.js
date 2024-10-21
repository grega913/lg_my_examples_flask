var socket = io();


document.addEventListener("DOMContentLoaded", function(){

    
    const messageInputEl = document.getElementById("message-input")
    const myBtnEl = document.getElementById("my-button")
    const loadingSpinner = document.getElementById('loading-spinner')
    loadingSpinner.style.display = 'none'

    /*
    const btnProceed = document.getElementById("btnProceed")
    btnProceed.style.display = "none"
   */


    function callApiDatapoint6() {
        console.log("callApiDatapoint6")

        const userMessageText = messageInputEl.value.trim();

        const textAreaEl = document.getElementById("text-area")

        const loadingSpinner = document.getElementById('loading-spinner')
        loadingSpinner.style.display = 'block';

        axios.post('/api/quick_start/part6', { user_input: userMessageText })
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





    myBtnEl.addEventListener("click", callApiDatapoint5_1);

    messageInputEl.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            callApiDatapoint5_1()
        }
    });





    socket.on("graph_part6", data => {
        console.log(data)
        const elMessage = document.createElement("li")
        elMessage.textContent = data
        messageList.appendChild(elMessage)
    })





});



// connecting form2 html elements to functions
function btnsForm2() {
    console.log("btnsForm2")
    // Get the button element
    const messageInput2 = document.getElementById("message-input2")
    const btn1 = document.getElementById('btn1');
    const btn2 = document.getElementById('btn2');
    const btn3 = document.getElementById('btn3');

    // Add an event listener to the button
    btn1.addEventListener('click', function() {

        console.log('btn1 clicked!');
        console.log(messageInput2.value)

    
        callApiDatapoint5_2(messageInput2.value)
        messageInput2.value=""






        socket.emit("part5_btn1", true)
        messageInput2.value=""
    });

    btn2.addEventListener('click', function() {

        console.log('btn2 clicked!');
        console.log(messageInput2.value)


        callApiDatapoint5_3(val=messageInput2.value, part="part1")


        socket.emit("part5_btn2", true)
    });

        btn3.addEventListener('click', function() {

        console.log('btn3 clicked!');
        console.log(messageInput2.value)
        socket.emit("part5_btn3", true)
    });
}



/*

function callApiDatapoint5_2(val) {
        console.log(`callApiDatapoint5_2 with value: ${val}`)


        const loadingSpinner = document.getElementById('loading-spinner')
        loadingSpinner.style.display = 'block';

        
        
        axios.post('/api/quick_start/part5_2', { user_input: val })
            .then(response => {

                console.log(response.data);
            })
            .catch(error => {
                console.error(error);
                
            });
            loadingSpinner.style.display = 'none';
}



function callApiDatapoint5_3(val, part) {
        console.log(`callApiDatapoint5_3 with value: ${val} and ${part}`)


        const loadingSpinner = document.getElementById('loading-spinner')
        loadingSpinner.style.display = 'block';

        
        axios.post('/api/quick_start/part5_3', { user_input: val, part:part })
            .then(response => {

                console.log(response.data);
            })
            .catch(error => {
                console.error(error);
                
            });
            loadingSpinner.style.display = 'none';
}
    
*/