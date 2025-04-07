# 📈 Group Progress Tracker

**Group Progress Tracker** is a web application designed to help teams track the progress of their group projects. It serves as a free alternative to platforms like monday.com.

![good.png](https://github.com/blakebrandon-hub/Team-Tracker-for-Project-Management/assets/50201165/b54c83a2-66cb-4d47-b222-2b985c4d4728)

## 🚀 Getting Started

1. **Sign Up:**
   - Navigate to the signup page and create an account.

2. **Log In:**
   - After signing up, you'll be redirected to the login page. Use your credentials to sign in.

3. **Create a Board:**
   - Once logged in, click on "Create Board" in the navbar.
   - Provide a board title, description, and set the board's privacy (private or public).

## 🛡️ User Roles & Permissions

### Board Creator Privileges:
- Edit board privacy settings.
- Update board title and description.
- Delete the board.
- Manage collaborators (add or remove).
- Create, update, and delete groups.
- Create, update, and delete tickets.
- Comment on tickets.

### Collaborator Privileges:
- Add collaborators.
- Create, update, and delete groups.
- Create, update, and delete tickets.
- Comment on tickets.

## 🛠️ Technologies Used

- **Backend:** Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (for development)
- **Deployment:** Heroku

## 🔧 Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/blakebrandon-hub/Group-Progress-Tracker.git
   cd Group-Progress-Tracker

2. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt

4. **Set Up Environment Variables:**
   Create a .env file in the root directory.
   Add necessary environment variables (e.g., SECRET_KEY, DATABASE_URL).

5. **Run the Application:**
   ```bash
   python app.py
   
6. **Access the Application:**

   Navigate to http://127.0.0.1:5000/ in your browser.

## ⚠️ Important Notes

- **Security:** Ensure that the `SECRET_KEY` is kept confidential and not exposed in public repositories.
- **Deployment:** For production, consider using a more robust database system and configure the application accordingly.

## 📜 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).



   



