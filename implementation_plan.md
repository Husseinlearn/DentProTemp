# Implementation Plan - DentPro Control Panel & Multi-Role Unified Dashboard

We propose a state-of-the-art, beautifully designed role-based dashboard system for DentPro. When a user logs in and visits the index page (`/`), they will be dynamically routed based on their database role (`user_type` or associated `Role` record) to a personalized dashboard tailored to their daily operations. 

In addition to routing, we will build a gorgeous, dark-mode custom login page at `/accounts/login/` so that the authentication flow matches the clinic's premium aesthetic.

---

## User Review Required

> [!IMPORTANT]
> **Dynamic Routing & Access Control**
> * Visiting the home page `/` will dynamically load role-specific backend queries and render the corresponding dashboard template (Manager, Doctor, Receptionist, or Patient).
> * The dashboards will be fully responsive and styled with HSL tailored dark-mode colors, glassmorphic charts, hover-triggered micro-animations, and live dynamic data badges.
> * We will create a `core/views_web.py` to act as the primary dashboard router and aggregator.
> * For **Superusers & Managers**, we will provide a floating role-switcher dropdown in the navbar/header. This allows clinic administrators to instantly preview and test the Doctor, Receptionist, or Patient dashboard without logging out and back in.

---

## Proposed Changes

### ⚙️ Core Dashboard Router

We will replace the static patient redirect on the index path with a unified dynamic `DashboardView` that aggregates real-time SQL data based on the logged-in user's role.

---

#### [MODIFY] [urls.py](file:///d:/Computer_Scince_and_Information_Technology/Level_fourd/Semster_Two/ProjectIIII/templataaa/DentPro/DentPro/urls.py)
* Map the root path `path('', ...)` to the core web dashboard view instead of redirecting to `/patients/`.
* Change `path('', RedirectView.as_view(url='/patients/', permanent=False), name='index')` to include core web URLs or route `/` directly.

---

#### [MODIFY] [urls_web.py](file:///d:/Computer_Scince_and_Information_Technology/Level_fourd/Semster_Two/ProjectIIII/templataaa/DentPro/core/urls_web.py)
* Add `path('', views_web.DashboardView.as_view(), name='dashboard')` to core's web routes.

---

#### [NEW] [views_web.py](file:///d:/Computer_Scince_and_Information_Technology/Level_fourd/Semster_Two/ProjectIIII/templataaa/DentPro/core/views_web.py)
* Create a class-based view `DashboardView(LoginRequiredMixin, TemplateView)`:
  * **Role Identification**: Checks `request.user.user_type` (and falls back to manager/admin if superuser).
  * **Interactive Switcher**: Detects `?role=<role_name>` parameter for admins to switch views on the fly.
  * **Manager Data**: Aggregates total active patients count, total completed procedure revenue, billing snap metrics, and Doctor shares (completed procedure costs split by each doctor's revenue_share).
  * **Doctor Data**: Fetches doctor-specific today's appointments, completed procedures count today, and patients with high-risk health flags (chronic diseases/allergies).
  * **Receptionist Data**: Fetches today's full appointment list queue, and pending payment procedures.
  * **Patient Data**: Fetches the logged-in patient's upcoming appointments, universal tooth treatment logs, and prescribed medications.
  * **Mock Fallbacks**: Ensures that if the database is blank/sparse, the dashboards are still beautifully populated with realistic, interactive mock data to present a flawless initial setup.

---

### 🎨 Role-Specific Dashboard Views (Templates)

We will build gorgeous, dark-mode glassmorphic dashboards using the pre-downloaded local static Tailwind and Bootstrap libraries.

#### [NEW] [dashboard_manager.html](file:///d:/Computer_Scince_and_Information_Technology/Level_fourd/Semster_Two/ProjectIIII/templataaa/DentPro/templates/core/dashboard_manager.html)
* **Design & Feel**: High-end financial dark mode with HSL-colored trend cards and metric widgets.
* **Key Metrics**:
  * 💵 **Total Clinic Revenue**: Total billing for all completed treatments.
  * 👨‍⚕️ **Dentist Revenue Shares**: Clear grid displaying each doctor's total performed billing and their custom financial cut based on their `revenue_share` percentage.
  * 📈 **Growth Summary**: Visual list tracking patient onboarding progress and monthly earnings.
  * 🗂️ **Procedure Billing Snapshot**: Interactive distribution of Paid vs Pending treatments.
* **Quick Actions**: Add Doctor, Register Patient, Create New Appointment.

#### [NEW] [dashboard_doctor.html](file:///d:/Computer_Scince_and_Information_Technology/Level_fourd/Semster_Two/ProjectIIII/templataaa/DentPro/templates/core/dashboard_doctor.html)
* **Design & Feel**: Clinical & health-focused.
* **Key Metrics**:
  * 📅 **Today's Queue List**: Full scrollable queue displaying patients scheduled today and their status.
  * 🩺 **Medical Alert Cards**: Highlights patients in today's clinic with registered chronic diseases (e.g. Diabetes) or dangerous drug allergies.
  * 🦷 **Completed Treatments**: Counter of procedures completed by this doctor today.
* **Quick Actions**: Write Clinical Advice, View Patient Files, Start New Session.

#### [NEW] [dashboard_receptionist.html](file:///d:/Computer_Scince_and_Information_Technology/Level_fourd/Semster_Two/ProjectIIII/templataaa/DentPro/templates/core/dashboard_receptionist.html)
* **Design & Feel**: Ultra-efficient workflow dashboard.
* **Key Metrics**:
  * 🕒 **Appointment Registry & Queue**: Interactive live-updating list showing todays clinic schedule.
  * 💳 **POS Payments desk**: Real-time display of unpaid clinical procedures with options to collect payment.
* **Quick Actions**: Register Walk-in Patient, Book Appointment Slot.

#### [NEW] [dashboard_patient.html](file:///d:/Computer_Scince_and_Information_Technology/Level_fourd/Semster_Two/ProjectIIII/templataaa/DentPro/templates/core/dashboard_patient.html)
* **Design & Feel**: Warm, friendly, patient-focused portal.
* **Key Metrics**:
  * 🦷 **My Treatments & Tooth Card**: List of teeth treated (e.g., FDI tooth codes) and procedures performed.
  * 📅 **My Next Sessions**: Countdown card for the patient's next scheduled checkup.
  * 💊 **My Active Prescriptions**: Direct list of prescribed medications, dosages, and notes.

---

### 🔑 Authentication Enhancement

To complete the premium design of the control panel, we will replace the default/admin login redirect with a stunning custom dark-mode login interface.

#### [MODIFY] [urls_web.py](file:///d:/Computer_Scince_and_Information_Technology/Level_fourd/Semster_Two/ProjectIIII/templataaa/DentPro/accounts/urls_web.py)
* Add `/accounts/login/` and `/accounts/logout/` routes mapping to the new custom login/logout views.

#### [MODIFY] [views_web.py](file:///d:/Computer_Scince_and_Information_Technology/Level_fourd/Semster_Two/ProjectIIII/templataaa/DentPro/accounts/views_web.py)
* Implement `CustomLoginView` (using Django's `LoginView`) and `CustomLogoutView` (using Django's `LogoutView`).

#### [NEW] [login.html](file:///d:/Computer_Scince_and_Information_Technology/Level_fourd/Semster_Two/ProjectIIII/templataaa/DentPro/accounts/templates/accounts/login.html)
* **Design & Feel**: A breathtaking dark-mode login form with glassmorphism overlays, custom inputs, teal branding, and interactive validation states.

---

## Verification Plan

### Automated & Manual Verification
* **Multi-Role Login & Switching**:
  1. Go to `/` while not logged in -> verifies elegant redirect to `/accounts/login/`.
  2. Log in as a Manager/Admin -> verifies loading of `/` shows `dashboard_manager.html` with financial/business KPIs.
  3. Use the floating Role Switcher dropdown to preview the **Doctor**, **Receptionist**, and **Patient** dashboards.
  4. Verify that each dashboard is fully responsive, contains micro-animations (transitions, hover-glows), and adapts beautifully to mobile and desktop resolutions.
