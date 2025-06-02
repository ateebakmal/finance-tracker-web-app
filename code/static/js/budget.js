function updateTopText(){
    document.querySelector(".main-content .dashboard-top #top-text").textContent = "Budgets"
}

function openTab(evt, tabId) {
    // Hide all tab contents
    document.querySelectorAll(".tab-content").forEach(tab => tab.classList.remove("active"));
    
    // Deactivate all tab links
    document.querySelectorAll(".tab-link").forEach(tab => tab.classList.remove("active"));

    // Show the selected tab content
    document.getElementById(tabId).classList.add("active");

    // Activate the clicked tab
    evt.currentTarget.classList.add("active");
}

// Function to add categories of user
async function updateUserCategories() {
    const response = await fetch("/api/get_user_categories");
    const json_response = await response.json();
    const categories = json_response.categories; //List of all categories fetched from the server

    const categoryDropdowns = document.querySelectorAll("#category-dropdown");
    categoryDropdowns.forEach( (dropdown)=>{
        
        // dropdown.innerHTML = ""; //Remove all the inner childs inside category dropdown

        // add new categories
        categories.forEach((element) => {
        let option = document.createElement("option"); //Create an option tag
        option.value = element; // Set the value for option
        option.textContent = element[0].toUpperCase() + element.slice(1); //Set the tex
        dropdown.appendChild(option);

    });

    
} );

}


// Function to validate amount



// Function to add budget
async function addBudgetForUser(){
    // Extract Data
    budgetData = {
        budget_name : document.getElementById("budget_name_input").value,
        budget_type : document.getElementById("budget_type_dropdown").value,
        category : document.getElementById("category-dropdown").value,
        amount : Number(document.getElementById("amount-input").value)
    }

    console.log(budgetData);

    const response = await fetch("/api/add_user_budget", {
            method : "POST",
            headers: {
                "Content-Type" : "application/json"
            },
            body: JSON.stringify(budgetData)
        });
    const json_response = await response.json()

    console.log(json_response);

    if(json_response.success){
        successToast("Successfully added the budget");
        document.getElementById("add-budget-popup").style.display = "none";
    }else{
        errorToast("Some issue occured");
    }
}

function isValidNumber(str) {
    return !isNaN(str) && str.trim() !== "";
}


// -----------------Action listeners
// Add an action listener for close-add-budget-button
document.getElementById("close-add-budget-button").onclick = ()=>{
    document.getElementById("add-budget-popup").style.display = "none";
};

// Action listener for add budget inside add budget popup
document.querySelector(".add-budget-popup .button-div button").onclick = ()=>{

    // Check if budget name is empty
    budgetNameInput = document.getElementById("budget_name_input").value;
    if( budgetNameInput === "" ){
        errorToast("Budget Name Cannot Be Empty");
        document.getElementById("budget_name_input").style.border = "1px solid red";
        return;
    }


    // Check if amount is null or less than 0
    amount_input = document.getElementById("amount-input").value;
    if(amount_input === ""){
        errorToast("Amount Cannot Be Empty");
        document.getElementById("amount-input").style.border = "1px solid red";
        return;
    }


    if (!isValidNumber(amount_input)) {
        errorToast("Enter a valid amount");
        document.getElementById("amount-input").style.border = "1px solid red";
        return
    }
    addBudgetForUser();
};


// ----------------Calling functions
updateUserCategories();
updateTopText();