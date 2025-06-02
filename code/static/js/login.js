const signInButton = document.getElementById("sign-in-btn");

function extractTextFields(){
    // This function returns all the input fields present on the page, In our case (email, password)
    const email = document.getElementById("email-input").value;
    const password = document.getElementById("password-input").value;
    return {email , password};
}
function emptyFields(){
    const {email,password} = extractTextFields();

    if(email === "" || password === ""){
        showAlert("Login Error", "Username and password is required")
        return true;
    }

    return false;
}

async function sendData(){
    const {email,password} = extractTextFields();

    // Send the POST request to the /signup endpoint with the data in JSON format

    const response = await fetch("/",{
        method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials : "include",
      body: JSON.stringify({ email, password}),
    }); 

    console.log("Sent Request");

    const result = await response.json();
    console.log(result);

    if (result.success === false){
        showAlert("Sign In Error",result.message);
    }

    if(result.success === true){
        window.location.href = "/dashboard"
    }
}
signInButton.addEventListener("click",function(){
    if(emptyFields()){
        console.log("Email or Password Is empty");
        return;
    }

    console.log("Email or Password Is Not empty")
    sendData();
});