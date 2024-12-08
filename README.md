# Travault: A Tailored CRM for Travel Management Companies

## Project Overview

Travault is a data warehouse solution designed for smaller travel management companies (TMCs). Based on my three years of experience working for a boutique TMC, I've identified a gap in the market for affordable, feature-rich Customer Relationship Management (CRM) systems. While popular CRMs like HubSpot and Salesforce offer powerful tools, their costs can be prohibitive for smaller companies, and free versions often have significant limitations. Travault aims to provide a tailored, cost-effective alternative with enhanced functionality compared to free CRM versions.

View the programme [here](https://travault-686ad8887c30.herokuapp.com/).

## Key Features

1. **Sales Process Tracking**
   - Monitor prospect clients through various stages:
     - Qualified
     - In Discussion
     - Account Form Sent
     - Closed - Won
     - Closed - Lost
     - Added to the sales pipeline

2. **Client Management**
   - Ability to add and link contacts to the company
   - Activity log initiation to track the client's lifecycle
   - Options to log meetings, emails, phone calls, and create tickets
   - "Client Notes" tab for TMC consultants to update information on client operations (e.g., travel policies)

3. **Supplier Management**
   - Store supplier contact information
   - Record contractual details:
     - Payment terms
     - Payment frequency
     - Credit line
     - Form of payment
   - Activity log for supplier interactions (meetings, emails, phone calls, tickets)

4. **Ticket Dashboard**
   - Overview of all open/closed tickets
   - Toggle button for easy filtering
   - Categorisation of client-related or supplier-related tickets
   - Display of opening date and brief description
   - Detailed view with options to update or close tickets

5. **Supplier Contact Directory**
   - Centralised area for TMC consultants to access:
     - Industry contact information
     - Supplier details
     - TMC booking processes

## Benefits

- Cost-effective alternative to premium CRMs
- Tailored functionality for travel management companies
- Improved client and supplier relationship management
- Streamlined communication and issue resolution
- Enhanced data organization and accessibility

## Database Schema

### **1.1. Agency Table**

| **Field Name**       | **Data Type**    | **Constraints**                                      | **Description**                                   |
|---------------------|-----------------|----------------------------------------------------|--------------------------------------------------|
| `id`                | Integer (Auto)   | Primary Key                                         | Unique identifier for each agency                |
| `agency_name`       | Varchar(255)     | Not Null                                            | Name of the agency                               |
| `address`           | Varchar(255)     | Not Null                                            | Full address of the agency                       |
| `phone`             | Varchar(20)      | Not Null                                            | Contact phone number                             |
| `email`             | EmailField       | Not Null                                            | Contact email address                            |
| `website`           | URLField         | Null, Blank                                         | Website URL (optional)                           |
| `vat_number`        | Varchar(9)       | Unique, Not Null                                    | VAT number of the agency                         |
| `company_reg_number`| Varchar(8)       | Unique, Not Null                                    | Company registration number                      |
| `employees`         | Varchar(10)      | Choices (`EMPLOYEE_CHOICES`), Not Null              | Size of the agency in terms of employees         |
| `business_focus`    | Varchar(20)      | Choices (`BUSINESS_FOCUS_CHOICES`), Not Null        | Main business focus of the agency                |
| `contact_name`      | Varchar(100)     | Not Null                                            | Primary contact person's name                    |
| `created_at`        | DateTime         | Auto Now Add                                        | Timestamp when the agency was created            |
| `updated_at`        | DateTime         | Auto Now                                            | Timestamp when the agency was last updated       |

---

## **2. Agent Support App**

### **2.1. AgentSupportSupplier Table**

| **Field Name**          | **Data Type**    | **Constraints**                                      | **Description**                                  |
|-------------------------|-----------------|-----------------------------------------------------|-------------------------------------------------|
| `id`                   | Integer (Auto)   | Primary Key                                          | Unique identifier for each supplier             |
| `agency_id`            | Integer          | Foreign Key → `Agency(id)`, Not Null                 | Associated agency                               |
| `supplier_type`        | Varchar(50)      | Choices (`SUPPLIER_TYPES`), Not Null                 | Type of supplier (Air, Accommodation, etc.)     |
| `supplier_name`        | Varchar(100)     | Not Null                                             | Name of the supplier                             |
| `created_at`           | DateTime         | Auto Now Add                                         | Timestamp when the supplier was created         |
| `updated_at`           | DateTime         | Auto Now                                             | Timestamp when the supplier was last updated    |

---

## **3. Billing App**

### **3.1. StripeCustomer Table**

| **Field Name**          | **Data Type**    | **Constraints**                                      | **Description**                                  |
|-------------------------|-----------------|-----------------------------------------------------|-------------------------------------------------|
| `id`                   | Integer (Auto)   | Primary Key                                          | Unique identifier for each Stripe customer      |
| `agency_id`            | Integer          | One-to-One → `Agency(id)`, Not Null                  | Linked agency                                   |
| `stripe_customer_id`   | Varchar(255)     | Unique, Null, Blank                                  | Stripe customer identifier                      |
| `subscription_status`  | Varchar(50)      | Default `'inactive'`                                 | Status of the subscription (active, inactive)  |
| `created_at`           | DateTime         | Auto Now Add                                         | Timestamp when the record was created           |
| `updated_at`           | DateTime         | Auto Now                                             | Timestamp when the record was last updated      |

---

## **4. CRM App**

### **4.1. Company Table**

| **Field Name**          | **Data Type**    | **Constraints**                                      | **Description**                                  |
|-------------------------|-----------------|-----------------------------------------------------|-------------------------------------------------|
| `id`                   | Integer (Auto)   | Primary Key                                          | Unique identifier for each company             |
| `agency_id`            | Integer          | Foreign Key → `Agency(id)`, Not Null                 | Associated agency                               |
| `company_name`         | Varchar(255)     | Not Null                                             | Name of the company                             |
| `email`                | EmailField       | Not Null                                             | Contact email address                           |
| `created_at`           | DateTime         | Auto Now Add                                         | Timestamp when the company was created          |

---

## **5. Activity Log App**

### **5.1. Meeting Table**

| **Field Name**          | **Data Type**    | **Constraints**                                      | **Description**                                  |
|-------------------------|-----------------|-----------------------------------------------------|-------------------------------------------------|
| `id`                   | Integer (Auto)   | Primary Key                                          | Unique identifier for each meeting             |
| `subject`              | Varchar(255)     | Not Null                                             | Subject of the meeting                         |
| `company_id`           | Integer          | Foreign Key → `Company(id)`, Not Null                | Associated company                              |
| `date`                 | Date             | Not Null                                             | Date of the meeting                             |

---

## **6. Ticketing System**

### **6.1. Ticket Table**

| **Field Name**          | **Data Type**    | **Constraints**                                      | **Description**                                  |
|-------------------------|-----------------|-----------------------------------------------------|-------------------------------------------------|
| `id`                   | Integer (Auto)   | Primary Key                                          | Unique identifier for each ticket               |
| `company_id`           | Integer          | Foreign Key → `Company(id)`, Not Null                 | Associated company                              |
| `contact_id`           | Integer          | Foreign Key → `Contact(id)`, Null, Blank             | Associated contact                              |
| `agency_id`            | Integer          | Foreign Key → `Agency(id)`, Not Null                 | Associated agency                               |
| `owner_id`             | Integer          | Foreign Key → `CustomUser(id)`, Not Null             | User who owns the ticket                        |
| `priority`             | Varchar(10)      | Choices (`PRIORITY_CHOICES`), Not Null               | Priority of the ticket                          |
| `status`               | Varchar(20)      | Choices (`STATUS_CHOICES`), Default `'open'`         | Current status of the ticket                    |
| `created_at`           | DateTime         | Auto Now Add                                         | Timestamp when the ticket was created           |
| `updated_at`           | DateTime         | Auto Now                                             | Timestamp when the ticket was last updated      |

---

## **Relationships Overview**

- **Agency**
  - One-to-Many with CustomUser, AgentSupportSupplier, Billing, Company, Ticket

- **CustomUser**
  - Many-to-One with Agency

- **AgentSupportSupplier**
  - Many-to-One with Agency

- **StripeCustomer**
  - One-to-One with Agency

- **Company**
  - Many-to-One with Agency

- **Ticket**
  - Many-to-One with Company, Contact, Agency

## **Issues / Bugs**

### **1. CSS Loading Issues**

I had a lot of issues trying to get the CSS to load. After numerous troubleshooting attempts and consultations with ChatGPT, I discovered that the static file was in the incorrect directory. Additionally, I had an incorrect syntax in the `settings.py` file for `STATICFILES_DIRS`. Upon reviewing my previous walkthrough project, **Boutique Ado**, I was able to identify and correct the syntax for `STATICFILES_DIRS`, and everything started working as expected.

---

### **2. "Register" Link Not Working**

The "Register" link in my navigation bar was not properly directing users to the registration page. After reviewing all the code, I discovered that the issue was caused by a bug in the **JavaScript** logic. The incorrect JS code was affecting how the link was being resolved. After identifying the problem, I made the necessary adjustments and the issue was resolved.

---

### **3. AWS S3 Integration Issues**

I encountered problems linking **AWS S3** for users to upload PDFs. The setup process proved to be more challenging than expected, and I have yet to fully resolve it. Further investigation and guidance are required to get this feature working properly.

---

### **4. Back Button Bug in Contact Edit View**

When a user was editing a contact and clicked the "Back" button, they were redirected to a different contact, rather than the original one they were editing. After reviewing the `views.py` file, I realised that the logic for handling the "Back" functionality was flawed. The **edit_contact view** was not properly fetching the correct contact object. I updated the view logic to ensure that it references the correct contact, and the bug was successfully resolved.

---

### **5. URL Routing Bug for Add Transaction Fee**

After refining my code to ensure proper handling of the active tab, I ran into another bug related to URL resolution. Specifically, after adding a fee, the URL incorrectly resolved to the **company_detail view** instead of the **add_transaction_fee view**. This was a tricky issue to debug as there were no syntax errors or obvious mistakes.

To resolve it, I used several debugging techniques, including:

- **Print statements** for tracking URL paths
- **Logging** key information at various points in the view
- **Using ChatGPT** to review potential causes

After a thorough review, I discovered that the **URL patterns were not prioritised correctly**. The `company_detail_with_tab` path was matching before `add_transaction_fee`, causing the wrong view to be triggered. To fix it, I adjusted the URL patterns to ensure that **add_transaction_fee** had a higher priority in the URL resolver. After this change, everything worked perfectly.

### **6. Field Duplication Bug in Agency Model**

While working on the **Agency model**, I realised I had two fields representing the same data: **`name`** and **`agency_name`**. To streamline the model, I decided to remove the **`name`** field and rely solely on **`agency_name`**.

#### **Issue**

Once I removed the **`name`** field, I encountered multiple errors during testing. The errors occurred wherever the code still referenced **`agency.name`**, which no longer existed. This affected several areas of the code, including:

- **View logic** where `agency.name` was being used.
- **Logger messages** that referenced `agency.name` for debugging.
- **Templates** where `agency.name` was used for displaying information.

#### **Debugging Steps**

To resolve this issue, I took the following steps:

- **Searched for all instances** of `agency.name` in the project files.
- **Replaced `agency.name` with `agency.agency_name`** where applicable.
- **Added a `__str__()` method** to the Agency model to avoid referencing `agency.agency_name` directly.
- **Ran tests** to ensure no further errors appeared when creating, editing, or viewing agency-related objects.

#### **Resolution**

- **Updated all references** of `agency.name` to **`agency.agency_name`** in the views, templates, and logger messages.
- **Implemented a `__str__()` method** in the Agency model to allow direct use of `str(agency)`, which automatically returns

**`agency.agency_name`**.

- **Tested the application thoroughly**, and no errors were found in areas where the previous errors occurred.

With these changes, I ensured a more consistent reference to the agency name and reduced the risk of this issue recurring in future development.

---

## **Testing Report**

---

### **Registration**

- ✅ **Successful register** — Successful
- ✅ **Registration email sent** — Successful
- ✅ **After confirming registration, login** — Successful
- ✅ **After login, ask for payment** — Successful
- ✅ **Create new users** — Successful
- ✅ **New user registration email sent** — Successful
- ✅ **Payment not asked for users** — Successful

---

### **Agent Support**

- ❌ **Add new supplier** — **Unsuccessful**
  - **Cause**: Bug caused by a duplicate field that was removed from the database.
  - **Solution**: Made small adjustments to the `views.py`. After refining the code, it now adds the supplier **successfully**.
- ✅ **Website opens in a new page** — Successful
- ✅ **Edit supplier** — Successful
- ✅ **Add process during editing** — Successful
- ✅ **Add PDF** — Successful
- ✅ **Delete agent supplier** — Successful

---

### **The Vault (CRM)**

#### **During the add company process:**

- ✅ **Fetch data from Diffbolt** — Successful
  - **Note**: It does not always work as it depends on where the data is stored on the website.
- ✅ **Company added** — Successful

---

#### **Activity and Contact Management**

- ❌ **Last activity timestamp not showing in the table**
  - **Cause**: No logic existed for it to be displayed.
  - **Solution**: Updated `models.py`, `app.py`, and created `update_last_activity.py` and `signals.py`. After these changes, the timestamp showed **successfully**.
- ✅ **Add company contact** — Successful
- ✅ **Edit company contact** — Successful
- ✅ **Delete company contact** — Successful
- ✅ **Add company notes** — Successful
- ✅ **Edit company notes** — Successful
- ✅ **Delete company notes** — Successful
- ✅ **Add fees** — Successful
- ✅ **Edit fees** — Successful

---

#### **Call, Email, and Meeting Logs**

- ✅ **Log a call** — Successful
- ✅ **Log an email with a reminder** — Successful
- ✅ **Log a meeting with a reminder** — Successful

---

#### **Ticketing System**

- ✅ **Create a ticket** — Successful
- ✅ **Update full ticket** — Successful
  - 📧 **Email received after creation of ticket** — Successful
- ✅ **Change ticket status** — Successful
  - 📧 **Email received after status change** — Successful
- ✅ **Add action to ticket** — Successful
  - 📧 **Email received after adding action** — Successful
- ✅ **Change ticket status to 'closed'** — Successful
  - 🔒 **After ticket closure, user could not edit or delete anything** — Successful
- ✅ **Saved subject shows when user starts searching** — Successful
- ✅ **Update action taken** — Successful
- ✅ **Delete action** — Successful
- ✅ **Back buttons working**:
  - **Back to company (x2)** — **Partially Successful**
    - 🔍 **Issue**: The second "Back to company" button didn't take the user to the correct tab.
    - **Solution**: Fixed the syntax in the HTML, and the button now works as expected.
  - ✅ **Back to all tickets (x2)** — Successful
- ✅ **Delete ticket** — Successful
- ✅ **Reopen ticket after closure** — Successful

---

#### **Ticket Subject Management**

- ✅ **Manage Ticket Subjects** — Successful
  - ✅ **Edit** — Successful
  - ✅ **Delete** — Successful
  - ✅ **Add** — Successful
  - ✅ **Back to tickets button works** — Successful

---

#### **Open a Ticket from Ticket View**

- ✅ **Open a ticket from ticket view** — Successful

---

### **Profile**

- ✅ **Update name and email** — Successful
  - 📧 **Email verification sent after updating email** — Successful
  - ❌ **Attempt to change email to one already in the database**:
    - **Issue**: It was changed initially, but only on verification did the system block the change.
    - **Solution**: Updated the logic in the `profile_view` function. Now it works as expected.

---

### **Manage Users**

- ✅ **Add new user** — Successful
  - 📧 **Verification email sent** — Successful
  - 🔐 **User needs to create a password** — Successful
- ✅ **Edit user details** — Successful

---

### **Agency Profile**

- ✅ **Update agency profile** — Successful

---

### **Billing**

- ✅ **View number of users** — Successful
- ✅ **View total cost per user and total cost for all users** — Successful
- ✅ **Update payment method (redirect to Stripe)** — Successful

---

### **Logout**

- ✅ **User successfully logged out** — Successful

## **Summary of Technologies**

| **Category**        | **Technology/Tool**          | **Purpose**                                          |
|--------------------|-----------------------------|-----------------------------------------------------|
| **Framework**       | [Django](https://www.djangoproject.com/) | Web development framework                           |
| **Storage**         | [AWS S3](https://aws.amazon.com/s3/)     | Media file storage                                  |
| **Server**          | [Heroku](https://www.heroku.com/)       | Cloud platform for app deployment                  |
| **Database**        | [PostgreSQL](https://www.postgresql.org/)| Relational database for storing data               |
| **Queue**           | [Celery](https://docs.celeryq.dev/en/stable/), [Redis](https://redis.io/) | Background job processing & message brokering      |
| **Cache**           | [Redis](https://redis.io/)               | Cache layer and message broker                     |
| **Authentication**  | [Django Allauth](https://django-allauth.readthedocs.io/en/latest/), [Django OTP](https://django-otp-official.readthedocs.io/en/latest/) | User authentication, 2FA support                   |
| **Payment**         | [Stripe](https://stripe.com/)           | Payment processing                                 |
| **Email**           | [Gmail SMTP](https://www.google.com/gmail/) | Email service for notifications                    |
| **Environment**     | [dotenv](https://pypi.org/project/python-dotenv/), [os](https://docs.python.org/3/library/os.html) | Securely load environment variables                |
| **CI/CD**           | [Heroku CI/CD](https://devcenter.heroku.com/articles/heroku-cli) | Continuous deployment to Heroku                   |
| **Package Management** | pip, requirements.txt   | Package and dependency management                  |
| **Logging**         | Django Logging, Custom Logs | Logs errors to file and console                   |
| **File Handling**   | [pathlib](https://docs.python.org/3/library/pathlib.html) | Cross-platform path handling                      |
| **Templates**       | Django Templates            | HTML templates for rendering views                |
| **Security**        | CSRF, Clickjacking Protection | Security measures for user interactions         |
| **Frontend**        | [HTML](https://developer.mozilla.org/en-US/docs/Web/HTML), [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS), [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript), [Bootstrap](https://getbootstrap.com/) | Frontend development technologies                |
| **Automation**      | [GitHub Actions](https://github.com/features/actions) | CI/CD for continuous deployment                    |
| **Error Handling**  | Custom Middleware           | Enforce payment, log errors to files              |
| **Assistance**      | [ChatGPT](https://openai.com/)            | AI assistance for support, queries, and guidance  |
