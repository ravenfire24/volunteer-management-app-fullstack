# Volunteer Management System – Backend

This is the back-end API for the Volunteer Management System, built using **Flask**. It supports user Login, profile management, event coordination, volunteer matching, notifications, and volunteer history tracking for a nonprofit organization.

##  Technologies Used

- Python 3.10+
- Flask
- Flask-CORS
- Flask-RESTful
- and more..



---

##  Setup Instructions

### 1. Install Python and pip (if not already installed)

         sudo apt update && apt install python3 python3-pip -y && git clone https://github.com/group-08-fullstack/volunteer-management-app

### 2. 🛠️ Create and activate a virtual environment         
### On macOS/Linux:
         cd volunteer-management-app && cd Backend
         apt install python3.10-venv -y
         python3 -m venv venv
         source venv/bin/activate
### On Windows:  
         venv\Scripts\activate
         
### 3.  Install required dependencies
         pip install -r requirements.txt


###  4. Inside the api folder, Run the Flask server using
         flask --app app run --debug
         
###  5. Navigate into the Frontend folder and run the server
         cd Frontend && npm run dev
       

###   The app will be available at: http://127.0.0.1:5000/

## Vercel + Aiven MySQL

This repo now includes a Vercel entrypoint at `api/index.py`, a `vercel.json`
that serves the Vite frontend and rewrites `/api/...` to Flask, and backend
config that reads MySQL settings from environment variables.

Set these environment variables in Vercel for the project:

```text
MYSQL_HOST=mysql-vma-ttorta005.g.aivencloud.com
MYSQL_PORT=21957
MYSQL_USER=avnadmin
MYSQL_PASSWORD=<your Aiven password>
MYSQL_DB=defaultdb
JWT_SECRET_KEY=<long random secret>
MYSQL_SSL_CA_CONTENT=<paste the full contents of ca.pem>
```

For local backend development, copy `Backend/api/.env.example` to
`Backend/api/.env` and fill in the same values. Locally you can use
`MYSQL_SSL_CA=C:\Users\beyan\Downloads\ca.pem` instead of
`MYSQL_SSL_CA_CONTENT`.

After deployment, visit `/api/health`; it should return `{"status":"ok"}`.

##  Project Structure
![alt text](https://github.com/group-08-fullstack/volunteer-management-app/blob/main/tree-structure.png)

