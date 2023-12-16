<img src="https://github.com/GatorEducator/cellveyor/blob/master/.github/images/cellveyor-logo.svg" alt="Cellveyor Logo"
    title="Cellveyor Logo" />

# Cellveyor

[![build](https://github.com/GatorEducator/cellveyor/actions/workflows/build.yml/badge.svg)](https://github.com/GatorEducator/cellveyor/actions/workflows/build.yml)
[![Code Style: black](https://img.shields.io/badge/Code%20Style-Black-blue.svg)](https://github.com/psf/black)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-blue.svg)](https://github.com/gkapfham/chasten/graphs/commit-activity)
[![License LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

## Example Command

```
poetry run cellveyor --spreadsheet-directory \
/home/gkapfham/working/data/gradebook/2023 --spreadsheet-file
CMPSC-203-Fall-2023-Gradebook.xlsx \
--sheet-name Main \
--key-attribute "Student GitHub" \
--key-value "gkapfham" \
--column-regexp "^(Summary Grade|Final Grade) .*$" \
--feedback-regexp "Summary Grade 1 - Feedback" \
--feedback-file /home/gkapfham/working/teaching/
github-classroom/feedback/all/feedback.yml \
--feedback-file /home/gkapfham/working/teaching/github-classroom/feedback/
developer-development/feedback-overall-course-assessment.yml \
--github-token <Private GitHub Acess Token> \
--github-organization Allegheny-Computer-Science-203-F2023 \
--github-repository-prefix computer-science-203-fall-2023-course-assessment \
--transfer-report
```

## 🎉 Introduction

- Cellveyor is a python program that produces assignment reports for students or
classes. Using Cellveyor will publicly give grade reports including feedback for
created assignments. Using the Cellveyor tool will quickly run and send reports to
members included in a locally created google spreadsheet. By running the command
created, this will quickly and automatically send out these reports in a very timely
and efficient fashion.

## 😂 Definitons

- Cellveyor is a tool that automatically produces a report based output by
analyzing a Google sheet
    - Student sentence: "I'm glad Cellveyor made it easy for me to see my grades
    from my classes, it's so easy to read and analyze."
    - Instructor sentence: "Cellveyor makes it much easier for me to tell my
    students what their grade looks like on a certain assignment or overall
    in the class"
    - Researchers sentence: "I found that Cellveyor is a very interesting tool that
    quickly and automatically does a task that is necessary in schooling"

## 🔋Features

- 🚀 Fully customizable command line interface
- ✨ Automated generation of grade-based reports sent to students
- 🪂 Rich command line interface with many various arguments

## ⚡️ Requirements

- Cellveyor git hub repository
- Local google sheet
- Git hub token

## 🔽 Installation

Follow these steps to install the Cellveyor program:
1. Copy the ssh key of the repo
2. ```Git clone``` the repository onto your personal computer
    - ```git clone (ssh key)```
3. Type ```poetry run cellveyor --help``` to learn how to use the tool

## 🎉 Creating `credentials.json` for Google Sheets API 🎉

### Step 1: Create a Google Cloud Console Account

1. Visit [Google Cloud Console](https://console.cloud.google.com/welcome?authuser=2&pli=1).
2. Click on **ENABLE APIS AND SERVICES**.
3. Create a new project by selecting **Create Project**, providing a project name, and clicking **Create**.

### Step 2: Enable Google Sheets API

1. In the Google Cloud Console, navigate to **Menu > APIs & Services > Library**.
2. Search for "Google Sheets API" and enable it.

### Step 3: Configure OAuth Consent Screen

1. In the Google Cloud Console, go to **Menu > APIs & Services > OAuth consent screen**.
2. Choose the User Type:
   - For new users, click on **External**. You can change this later.
3. Skip any information that is not required.
4. Skip adding scopes for now and click **Save and Continue**. You can add scopes in the future for specific app functionality.
5. If you selected External for user type, add test users:
   - Under **Test users**, click **Add users**.
   - Enter your email address and any other authorized test users, then click **Save and Continue**.

### Step 4: Review and Save

1. Review your app registration summary.
2. To make changes, click **Edit**. If the app registration looks OK, click **Back to Dashboard**.

### Step 5: Create Credentials

1. In the Google Cloud Console, navigate to **Menu > APIs & Services > Credentials**.
2. Click on **Create Credentials** and choose **OAuth client ID**.
3. Select the application type (e.g., Desktop App, Web Application).
4. Provide a name for the OAuth client ID.
5. Add authorized redirect URIs (if required).
6. Click **Create**.
7. Download the credentials as a JSON file by clicking on the download icon next to your newly created OAuth 2.0 Client ID.

### Step 6: Move and Use Credentials

1. Move the downloaded `credentials.json` file to the directory where your Python script or application will use it.
2. Use the `credentials.json` file in your script to authenticate with the Google Sheets API.

Now, your script should be able to access Google Sheets using the credentials obtained from the Google Cloud Console.

## 🎉 Creating Service Account Credentials for Google Sheets API 🎉

### Step 1: Create a Google Cloud Console Account

1. Visit [Google Cloud Console](https://console.cloud.google.com/welcome?authuser=2&pli=1).
2. Click on **ENABLE APIS AND SERVICES**.
3. Create a new project by selecting **Create Project**, providing a project name, and clicking **Create**.

### Step 2: Enable Google Sheets API

1. In the Google Cloud Console, navigate to **Menu > APIs & Services > Library**.
2. Search for "Google Sheets API" and enable it.

### Step 3: Create a Service Account

1. In the Google Cloud Console, navigate to **Menu > IAM & Admin > Service Accounts**.
2. Click on **Create Service Account**.
3. Provide a name and description for the service account.
4. Assign the **Project > Editor** role to the service account.
5. Click **Continue** and then **Done**.
6. Click on the newly created service account.
7. Navigate to the **Keys** tab and click on **Add Key** > **Create new key**.
8. Choose the key type as **JSON** and click **Create**.
9. Save the downloaded JSON file securely. This is your service account key file (`service_account_key.json`).

### Step 4: Share Google Sheets with Service Account

1. Open your Google Sheet.
2. Click on **Share** in the top right corner.
3. Share the sheet with the email address associated with your service account.

### Step 5: Use Service Account Key in Your Application

1. Move the downloaded `service_account_key.json` file to the directory where your Python script or application will use it.
2. Use the `service_account_key.json` file in your script to authenticate with the Google Sheets API.

Now, your script should be able to access Google Sheets using the service account credentials obtained from the Google Cloud Console. Ensure that the service account has the necessary permissions to access the Google Sheets you want to work with.
