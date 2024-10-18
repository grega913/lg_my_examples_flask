
/*
document.getElementById('my-button').addEventListener('click', function() {
  console.log("button clicked")
  axios.post('/api/gg', { user: "make a recipe with cucumber"} )

    .then(response => {
        console.log(response.data);
        textAreaEl.className = "resp_te"
        textAreaEl.textContent = response.data

        })
        .catch(error => {
            console.error(error);
        });
});
*/


function callPythonFunction() {

    const messageInput= document.getElementById('message-input');    
    const userMessageText = messageInput.value.trim();
    
    axios.post('/api/gg', { user: userMessageText } )

        .then(response => {
            console.log(response.data);
            textAreaEl.className = "resp_te"
            textAreaEl.textContent = response.data
            console.log("n")
            })
            .catch(error => {
                console.error(error);
            });
}
