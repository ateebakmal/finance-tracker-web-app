const tableDiv = document.getElementById("table-div");
const overlay = document.getElementById("overlay");
const filterButton = document.getElementById("filter-button");
const closeFilterButton = document.getElementById("close-filter-button");
// const categoryDropdown = document.getElementById("category-dropdown");
const applyFilterButton = document.getElementById("apply-filter-button");
const resetButton = document.getElementById("reset-button");
const addTransactionButton = document.getElementById("add-transaction-button");
const closeAddTransactionButton = document.getElementById("close-add-transaction-button");
const innerAddTransactionButton = document.querySelector(".button-div > button");
const transactionTypeDropdown = document.getElementById("transaction-type-dropdown");
const transferDiv = document.getElementById("transfer-div");
const categoryDiv = document.getElementById("category-div");




document.getElementById("top-text").textContent = "Transactions"

async function update_transactions_table() {
    
    // Get table for income and expense:
    const income_and_expense_response = await fetch(`/api/get_recent_transactions_table/${10}`);
    const income_and_expense_table = await income_and_expense_response.text();
    // console.log(html_table);

    // Make the table loading text disappear
    document.getElementById("income-and-expense-table").parentElement.querySelector("#table-loading-text").style.display = "none";
    document.getElementById("income-and-expense-table").innerHTML = income_and_expense_table;

    // Update transactions Table

    const transaction_response = await fetch("/api/get_transfer_transactions_table");
    const transaction_response_table = await transaction_response.text();
    //Make the table loading text disappear 
    document.getElementById("transfer-table").parentElement.querySelector("#table-loading-text").style.display = "none";
    document.getElementById("transfer-table").innerHTML = transaction_response_table;
}

async function updateUserCategories() {
    const response = await fetch("/api/get_user_categories");
    const json_response = await response.json();
    const categories = json_response.categories; //List of all categories fetched from the server

    const categoryDropdowns = document.querySelectorAll("#category-dropdown");
    console.log(categoryDropdowns);
    categoryDropdowns.forEach( (dropdown)=>{
        
        dropdown.innerHTML = ""; //Remove all the inner childs inside category dropdown

        // add new categories
        categories.forEach((element) => {
        let option = document.createElement("option"); //Create an option tag
        option.value = element; // Set the value for option
        option.textContent = element[0].toUpperCase() + element.slice(1); //Set the tex
        dropdown.appendChild(option);

    });

    
} );
    // Add a all option in transaction dropdown. And make it appear on top
    categoryDropdown = document.querySelector(".filter-div #category-dropdown");
    const option = document.createElement("option");
    option.value = "all";
    option.text = "All";
    categoryDropdown.appendChild(option);
    categoryDropdown.value = "all";

}

async function updateAccounts(){
    const response = await fetch("api/get_user_accounts");
    const json = await response.json();
    
    const accounts = json.accounts;

    accountsDropdown = document.querySelectorAll(".account-dropdown");

    console.log(accountsDropdown);

    accountsDropdown.forEach( (dropdown)=>{

        accounts.forEach( (account)=>{

            const optionTag = document.createElement("option"); // Create an option tag
            optionTag.value = account// Set the value and text
            optionTag.text = account;
            dropdown.appendChild(optionTag)

        } );
    
    
    } );
}

async function addCategoryForUser(){
    // Add a onclick for close button inside this 
    document.querySelector(".add-category-popup-div .close-button").onclick = ()=>{
        document.getElementById("add-category-popup").style.display = "none";
    };
    console.log("We here");
    category = document.querySelector(".add-category-popup-div input").value;
    if(category === ""){
        showAlert("Invalid Category", "Enter some category")
    }else{
        // Call backend api and wait for response
        const response = await fetch("/api/add_user_category", {
            method : "POST",
            headers: {
                "Content-Type" : "application/json"
            },
            body: JSON.stringify({category_name : category})
        });

        // Get response from backend
        const json_response = await response.json();
        console.log(json_response);
        if (json_response.success){
            updateUserCategories();
            document.getElementById("add-category-popup").style.display = "none";
        }else{
            showAlert("Error", "Cannot insert this category")
        }
    }
}

async function addTransactionForUser(){
    selectedTransactionType = document.querySelector(".add-transaction-popup #transaction-type-dropdown").value;

    transactionName = document.getElementById("transaction-name-input").value;
    transactionAmount = document.querySelector(".amount-and-date-div #amount-input" ).value;
    transactionDate = document.querySelector(".amount-and-date-div #dateField").value;
    console.log(selectedTransactionType, transactionName, transactionAmount, transactionDate);

    // Error handling check if any necessary data is missing
    if(transactionName === "" || transactionAmount === "" || transactionDate === ""){
        showAlert("Invalid Transaction Data", "Input fields cannot be empty");
        return;
    }

    inputs = document.querySelectorAll(".add-transaction-div input");
    
    transactionData = {};

    inputs.forEach((input)=>{
    
        transactionData[input.name] = input.value;
    
    });

    dropdowns = document.querySelectorAll(".add-transaction-div select");
    dropdowns.forEach( (dropdown)=>{
        transactionData[dropdown.name] = dropdown.value; 
    } );

    // Error handling if transaction_type = "transfer" and both accounts are same
    if(selectedTransactionType === "transfer"){
        // Check if both from and to account is same
        if(transactionData.from_dropdown === transactionData.to_dropdown){
            showAlert("Invalid Transfer Data", "From and To accounts cannot be same");
            return;
        }
    }
    console.log(transactionData);


    // Send the POST request to backend and let it handle the functionality for all the cases
    const response = await fetch("/api/add_transaction" ,     {
                        method: "POST",
                        headers: {
                        "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ transactionData })
                        } );

    const json_response = await response.json()

    console.log("json_response : ",json_response)
    // To be added here, add an alert for success and failure
    if(json_response.success){
        successToast(json_response.message)
    }else{
        errorToast(json_response.message)
    }

    // Update the tables
    update_transactions_table();
    // Close the overlay
    document.getElementById("add-transaction-popup").style.display = "none";

}

async function applyFilter(){
    const filterDiv = document.getElementById("filter-div"); // Get the parent div
    const inputs = filterDiv.querySelectorAll("input"); // Select all input fields

    const filterData = {};

    inputs.forEach((input) => {
        filterData[input.name] = input.value; // Store each input's name-value pair
    });

    // Add the accounts and category selected in objects.
    // filterData.category = document.getElementById("category-dropdown").value; //Adding category field
    // filterData.account = document.getElementById("account-dropdown").value; //Adding category field

    // Add all dropdowns data to filterData JSON
    dropdowns = document.querySelectorAll(".filter-div select");
    dropdowns.forEach( (dropdown)=>{
        filterData[dropdown.name] = dropdown.value;
    } );

    // Some error handling
    // 1) Check if start date is less than end date
    
    // Reset time to midnight for accurate date comparison
    start_date = new Date(filterData.start_date);
    end_date = new Date(filterData.end_date);

    start_date.setHours(0,0,0,0);
    end_date.setHours(0,0,0,0);
    
    if(start_date > end_date){
        showAlert("Invalid Filter Data", "Enter valid date");
    }

    // 2) Amount Erros
    // 2.2 : Check if minimum amount in greater than max amount
    // 2.3 : Check if any amount is in negative

    //Converting amounts into numbers
    filterData.minimum_amount = Number(filterData.minimum_amount)
    filterData.maximum_amount = Number(filterData.maximum_amount)
    
    minAmount = filterButton.minimum_amount;
    maxAmount = filterButton.maximum_amount;

    if( minAmount !== 0 && maxAmount === 0 ){
        // If this condition is true we just let it pass
    }else if(minAmount > maxAmount
        || minAmount < 0 || maxAmount < 0){
        
        showAlert("Invalid Filter Data", "Enter valid amount data")
    }


    // 3) Check if user is filtering transfers and if both accounts are same
    if(filterData.filter_type === "transfer"){

        if(filterData.from_dropdown === filterData.to_dropdown){
            showAlert("Invalid Filter Data", "From and To accounts cannot be same");
            return
        }

    }
    console.log(filterData);

    // return;

    // Logic for getting data from backend
    // No matter the filter_type we call the same backend api
    // The api will perform processing and return an html table
    // At frontend, we will check filter_type and update the thing accordingly


    // Fetching filtered records from backend
    const response = await fetch("/api/get_filtered_transactions",{
        method: "POST",
        headers: {
        "Content-Type": "application/json"
        },
        body: JSON.stringify(filterData)
    });
    const html_table = await response.text()

    console.log(html_table);

    if (filterData.filter_type === "income_and_expense"){
        document.getElementById("income-and-expense-table").innerHTML = html_table;
    }else{
        document.getElementById("transfer-table").innerHTML = html_table;
    }
    overlay.style.display = "none";

}




addTransactionButton.onclick = ()=>{
    document.getElementById("add-transaction-popup").style.display = "flex";
};

closeAddTransactionButton.onclick = ()=>{
    document.getElementById("add-transaction-popup").style.display = "none";
};
filterButton.onclick = ()=>{
    overlay.style.display = "flex";
};

closeFilterButton.onclick = ()=>{
    overlay.style.display = "none";
};


applyFilterButton.onclick = ()=>{
    applyFilter();
};

// Event handler for add transaction button
// Inside add transaction pop-up
document.querySelector(".add-transaction-div .button-div button").onclick = ()=>{

    addTransaction();
};


resetButton.onclick = () => {
    const inputs = document.getElementById("filter-div").querySelectorAll("input");
    
    console.log(inputs);
    inputs.forEach((element)=>{
        element.value = "";
    });

    categoryDropdown.value = "all";

};

// Event handler for when clicks on add-category-button inside
// Add transaction popup
document.getElementById("add-category-button").onclick = ()=>{
    document.getElementById("add-category-popup").style.display = "flex";
};

// Event handler for when user clicks on add category button inside add-category-popup
document.querySelector(".add-category-popup-div .bottom button").onclick = addCategoryForUser;

// Event handler when clicking on add transaction inside add-transaction-popup
document.querySelector(".add-transaction-popup .button-div button").onclick = addTransactionForUser;

// Event handler when clickin on close in add category popup
document.querySelector(".add-category-popup-div .top button").onclick = ()=>{
    document.getElementById("add-category-popup").style.display = "none";
};
// This code takes care for changes in add-transaction-popup
transactionTypeDropdown.addEventListener('change', ()=>{
    const selectedOption = transactionTypeDropdown.value;
    console.log(selectedOption);

    if(selectedOption === "transfer"){
        document.querySelector(".add-transaction-div .category-div").style.display = "none";
        document.querySelector(".add-transaction-div .accounts-div").style.display = "none";
        document.querySelector(".add-transaction-div .transfer-div").style.display = "flex";
    }else if(selectedOption === "income"){
        document.querySelector(".add-transaction-div .category-div").style.display = "none";
        document.querySelector(".add-transaction-div .accounts-div").style.display = "block";
        document.querySelector(".add-transaction-div .transfer-div").style.display = "none";
    }else{
        document.querySelector(".add-transaction-div .category-div").style.display = "block";
        document.querySelector(".add-transaction-div .accounts-div").style.display = "block";
        document.querySelector(".add-transaction-div .transfer-div").style.display = "none";
    }
});

// Add an action listener of select while selecting filter type
document.getElementById("filter-type-dropdown").addEventListener( 'change' , function(){
    const selectedOption = this.value;
    
    if (selectedOption === "transfer") {
        document.querySelector(".filter-div .category-div").style.display = "none";
        document.querySelector(".filter-div .accounts-div").style.display = "none";
        document.querySelector(".filter-div .transfer-div").style.display = "flex";

    }else if(selectedOption === "income_and_expense"){
        document.querySelector(".filter-div .category-div").style.display = "block";
        document.querySelector(".filter-div .accounts-div").style.display = "block";
        document.querySelector(".filter-div .transfer-div").style.display = "none";
    }

});


update_transactions_table();
updateUserCategories();
updateAccounts();
flatpickr("#dateField", {
            dateFormat: "Y-m-d",
            altInput: false,
            altFormat: "F j, Y",
        });

flatpickr("#startDateField", {
    dateFormat: "Y-m-d",
    altInput: false,
    altFormat: "F j, Y"
});

flatpickr("#endDateField", {
    dateFormat: "Y-m-d",
    altInput: false,
    altFormat: "F j, Y"
});