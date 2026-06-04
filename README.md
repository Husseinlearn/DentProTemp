DentPro - Dental Clinic Management System

 Overview
DentPro is a modern and comprehensive Dental Clinic Management System designed to simplify and optimize the day-to-day operations of dental clinics. The system helps in managing patients, appointments, medical records, billing, staff permissions, dental charts, and communication between doctors and patients — all from a centralized, user-friendly platform.

This project is built using Django as the backend framework and PostgreSQL as the database, with full support for  REST APIs, making it suitable for both web and mobile integrations.

 Key Features
Patient Management: Register, update, and track patients' profiles, chronic diseases, allergies, and medical history.

Appointments: Schedule and manage appointments, with real-time status updates and reminders.

Medical Records: Keep detailed, structured records for each visit, including diagnosis, prescriptions, lab requests, and treatment plans.

Dental Charts: Visual dental charts (odontograms) to record procedures and tooth conditions.

Billing System: Issue invoices, manage payment methods, and generate financial reports.

User Roles & Permissions: Multi-role system (Admin, Doctor, Assistant, Receptionist) with granular permission control.
 Features Optional
Internal Messaging: Secure messaging between staff and doctors for better collaboration.

Notifications: Real-time notifications for appointments, tasks, and messages (in-app and via email).

Multilingual Support: Interface supports both Arabic and English based on user preferences or browser settings.

Logging and Audit: Full activity log for monitoring changes and user actions in the system.

File Attachments: Upload and manage files related to treatments, lab reports, or X-rays.

Reports and Analytics: Dashboard with statistics for doctors, patients, services, payments, and clinic performance.


| Layer             | Technology                           |
| ----------------- | ------------------------------------ |
| Backend           | Django (Python)                      |
| Database          | PostgreSQL                           |
| Frontend (Web)    | Flutter (web)                        |
| REST API          | Django REST Framework                |
| Authentication    | Custom User Model                    |
| Deployment        | Docker / Gunicorn / Nginx (Optional) |

 User Roles
Admin: Full access to all system functionalities and settings.

Doctor: Access to patient medical records, appointments, and treatment plans.

Receptionist: Handles appointment booking and patient registration.

Assistant: Limited access to medical records and operational tools.

Patient (optional): Can view appointments and communication via a portal (future feature).