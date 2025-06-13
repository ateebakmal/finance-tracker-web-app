# 💸 Finance Tracker Web App

A modern, full-stack **Personal Finance Tracker** that helps users **track expenses**, **manage budgets**, and **analyze financial health** with ease — built using , **Flask**, and **JavaScript + HTML/CSS** frontend.

---

## 🚀 Features

### ✅ Secure User Authentication
- Register with unique username and email
- Password-protected login with server-side validation
- Secure session handling

### 📊 Interactive Dashboard
- Real-time overview of total **income**, **expenses**, and **balance**
- Visual analytics including:
  - **Category-wise spending breakdown**
  - **Monthly income vs. expense trends**
- Dynamic and responsive UI

### 💼 Transaction Management
- Add **Income**, **Expense**, or **Transfer** transactions
- Include amount, date, category, and account
- View all transactions in a searchable, filterable table
- Edit or delete any entry with ease
- Filter by:
  - **Date range**
  - **Account**
  - **Category**
  - **Amount**

### 🧾 Budget Management
- Set **Daily**, **Weekly**, or **Monthly** budgets
- Assign budgets to specific categories or accounts
- Visual budget progress bars with **color-coded thresholds**
  - 🟢 Safe  
  - 🟡 Nearing Limit  
  - 🔴 Exceeded
- Alerts on limit breaches

### 🏦 Account Management
- Add and manage multiple financial accounts (e.g., Bank, Wallet, Cash)
- Track individual account balances
- Remove or rename accounts as needed
- Data reflects across all modules

### 📁 Database Integration
- All transactions, accounts, and user settings stored and managed through a robust backend

---

## 🛠 Tech Stack

| Layer         | Technology               |
|---------------|---------------------------|
| Frontend      | HTML5, CSS3, JavaScript (ES6) |
| Backend       | Python Flask              |
| Visualization | Matplotlib / Custom JS Charts |

---

## 📦 Installation (for Developers)

```bash
git clone https://github.com/your-username/finance-tracker.git
cd finance-tracker
python -m venv venv
source venv/bin/activate    # or venv\Scripts\activate (Windows)
pip install -r requirements.txt
python run.py
