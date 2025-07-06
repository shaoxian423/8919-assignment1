
# Azure Auth0 Flask Setup

## 🎥 Video Demonstration

[![Watch the video](https://img.youtube.com/vi/S-MBQgTe8c8/hqdefault.jpg)](https://www.youtube.com/watch?v=B4SgXNXt4tg)

Click the image above or [watch the demo on YouTube](https://www.youtube.com/watch?v=B4SgXNXt4tg).

## ⚙️ Setup and Deployment Instructions

### 0. Sign Up for Auth0

- Visit [Auth0 Docs](https://auth0.com/docs) and sign up for an account.
- Create a new application:
  - Choose "Regular Web Application" and select Python.
  - Download the sample code zip and note the **AUTH0_DOMAIN**, **AUTH0_CLIENT_ID**, and **AUTH0_CLIENT_SECRET**.

### 1. Set Up Azure Resources

#### Create a Resource Group
```bash
az group create --name 8919lab2 --location canadacentral
```

#### Create an App Service Plan
```bash
az appservice plan create --name 8919lab2Plan --resource-group 8919lab2 --sku FREE --location canadacentral --is-linux
```

#### Create a Web App
```bash
az webapp create --resource-group 8919lab2 --plan 8919lab2Plan --name my8919lab2v2 --runtime "PYTHON|3.9" --deployment-local-git
```
- Note the Git URL (e.g., `https://duanquiz2user@my8919lab2v2.scm.azurewebsites.net/my8919lab2v2.git`).

#### Configure Git Remote
```bash
git remote add azure https://duanquiz2user@my8919lab2v2.scm.azurewebsites.net/my8919lab2v2.git
```

### 2. Clone the Repository
```bash
git clone https://github.com/shaoxian423/8919lab1.git
cd 8919lab1
```

### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```
Ensure `requirements.txt` includes:
```text
flask==2.3.3
authlib==1.3.1
python-dotenv==1.0.0
gunicorn==22.0.0
```
- Copy `.env.example` to `.env` and fill in your Auth0 credentials (**do not commit `.env` to GitHub!**).

### 5. Configure Environment Variables for Azure

In **Azure Portal > my8919lab2v2 > Configuration > Application settings**, add:
```
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
APP_SECRET_KEY=your-flask-secret-key
PORT=3000
```

### 6. Set Startup Command

In **Azure Portal > my8919lab2v2 > Configuration > General settings**, set Startup Command:
```text
gunicorn --bind=0.0.0.0 app:application
```

### 7. Deploy the Application
```bash
git add .
git commit -m "Deploy enhanced Flask app with Auth0 and logging"
git push azure master
```
Enter your Azure deployment credentials when prompted.

### 8. ▶️ Run the App

Open in browser:
```
https://my8919lab2v2.azurewebsites.net
```

### 9. 🔐 Protected Route

Access:
```
https://my8919lab2v2.azurewebsites.net/protected
```
✔ If logged in → see name + email  
❌ If not logged in → redirected to Auth0 login

### 10. 📝 Enable and View Logs

#### Enable Logs:

In **Azure Portal > my8919lab2v2 > Monitoring > Diagnostic settings**:
- Add a diagnostic setting.
- Check **AppServiceConsoleLogs** and **Application Logging (Filesystem)**.
- Send to Log Analytics workspace (e.g., `myLogAnalyticsWorkspace`).

Or in **App Service logs**, enable **Application Logging (Filesystem)** with level **Information**.

#### View Logs:

- **Log Stream:** Go to **Monitoring > Log stream** for real-time logs.
- **Log Analytics Workspace > Logs**, run:
```kql
AppServiceConsoleLogs
| where TimeGenerated > ago(15m)
| where ResultDescription contains '"event": "protected_route_access"'
| extend ParsedLog = parse_json(ResultDescription)
| summarize AccessCount = count() by user_id = tostring(ParsedLog.user_id)
| where AccessCount > 10
```
## Alert:
1. Create the Alert Rule
	•	In the Logs query results page, click + New alert rule.
	•	Under Condition, select:
	•	Query results > 0
	•	Set evaluation period to 15 minutes, frequency to 5 minutes.

2. Create an Action Group
	•	If you don’t have one, create a new Action Group:
	•	Add an Email notification with your email address.
	•	Give the action group a name (e.g., EmailAdmins).

3. Configure the Alert
	•	Alert rule name: Protected route abuse detected
	•	Severity: 3 (Low)
	•	Action Group: Select the one you just created.
	•	Enable alert rule on creation: ✔️ Checked

4. Save and Test

Test by accessing /protected multiple times in 15 minutes. Once the threshold is crossed, an email notification will be sent.

- **Kudu Console:** [https://my8919lab2v2.scm.azurewebsites.net](https://my8919lab2v2.scm.azurewebsites.net) > Debug console > LogFiles/Application.

---
© 2025 Shaoxian Duan · CST8919 Assignment 1
