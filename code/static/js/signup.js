

function checkEmptyData(){
      // Retrieve the input values
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const confirm_password = document.getElementById('confirm_password').value;
      const username = document.getElementById("username-input").value;
      if (email === "" || password === "" || confirm_password === "" || username === ""){
        errorToast("None of the fields can be empty");
        // showAlert("Signup Error", "None of the fields can be empty");
        return true;
      }

      return false;
}

function checkPasswordAndConfirmPassword(){
  // Retrieve the input values
  const password = document.getElementById('password').value;
  const confirm_password = document.getElementById('confirm_password').value;
  if(password !== confirm_password){
    errorToast("Password and Confirm Password should be same");
    // showAlert("Signup Error", "Password and Confirm Password should be same");
    return true;
  }

  return false;
}

// This function sends data to your Flask endpoint via a POST request.
async function sendData() {
    // Retrieve the input values
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirm_password = document.getElementById('confirm_password').value;
    const username = document.getElementById('username-input').value;
    // Send the POST request to the /signup endpoint with the data in JSON format
    const response = await fetch('/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password , confirm_password, username}),
    });
  
    console.log("Sent request")
    // Await and parse the JSON response
    const result = await response.json();
    
    // Check if response is success or failure
    if (result.success === false){
      errorToast(result.message);
      // showAlert("Signup Error", result.message);
    }else{
      successToast("Account registered successfully");
      // showAlert("Account Registered", "Account Registered Successfully");
    }
    console.log(result);
  }
  
  // When the document is fully loaded, attach a click event listener to the signup button.
  document.addEventListener('DOMContentLoaded', () => {
    const signupButton = document.getElementById('sign-up-button');
    if (signupButton) {
      signupButton.addEventListener('click', (event) => {
        
        if( checkEmptyData()){
          return
        }

        if (checkPasswordAndConfirmPassword()){
          console.log("I am inside second if")
          return;
        }

        console.log("I am here")
        event.preventDefault();  // Prevent any default button behavior
        sendData();              // Call the async function to send the data
      });
    }
  });


//Check if all fields are entered
  