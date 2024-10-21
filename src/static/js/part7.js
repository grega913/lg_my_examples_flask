

function displayCurrentTime_2() {
    console.log("displayCurrentTime_2")
    const currentTimeElement_2 = document.getElementById('currentTime_2');
    const currentTime = moment();
    const formattedTime = currentTime.format('YYYY-MM-DD HH:mm:ss');
    currentTimeElement_2.textContent = `Current time: ${formattedTime}`;   
}