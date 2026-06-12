# Regression Test Checklist

Use this checklist before publishing a release. Record the tested version, date, and result for each test.

Version:
Date:
Tester:

## Browser Session Management

### Test 1: Smartschool -> Smartschool

Steps:
1. Start the application.
2. Start a Smartschool login.
3. Start a second Smartschool login.

Expected:
- Same browser window is reused.
- Browser has 2 tabs.
- No second normal browser window is created.

Result:
- [ ] Pass
- [ ] Fail
- Notes:

### Test 2: Google Admin -> Easy4U

Steps:
1. Start the application.
2. Start a Google Admin login.
3. Start an Easy4U login.

Expected:
- Same incognito browser is reused.
- Browser has 2 tabs.
- No second incognito browser window is created.

Result:
- [ ] Pass
- [ ] Fail
- Notes:

### Test 3: Normal Login -> Incognito Login

Steps:
1. Start the application.
2. Start a normal login.
3. Start an incognito login.

Expected:
- Exactly 2 browser windows exist:
  - 1 normal browser
  - 1 incognito browser
- No extra Chrome windows are created by the application.

Result:
- [ ] Pass
- [ ] Fail
- Notes:

### Test 4: Incognito Login -> Incognito Login -> Incognito Login

Steps:
1. Start the application.
2. Start an incognito login.
3. Start a second incognito login.
4. Start a third incognito login.

Expected:
- 1 incognito browser window.
- 3 tabs in that incognito browser.
- No normal browser is created unless a normal login was also started.

Result:
- [ ] Pass
- [ ] Fail
- Notes:

## Login Flows

### Test 5: Google Native Login

Steps:
1. Ensure Google Admin routes to `accounts.google.com`.
2. Start Google Admin login.
3. Complete the native Google login flow.

Expected:
- `FLOW_GOOGLE` is logged.
- Login succeeds.
- Browser remains open if captcha, MFA, or manual user interaction appears.

Result:
- [ ] Pass
- [ ] Fail
- Notes:

### Test 6: Google Admin With Microsoft Redirect

Steps:
1. Ensure Google Admin redirects to `login.microsoftonline.com`.
2. Start Google Admin login.
3. Complete the Microsoft SSO flow.

Expected:
- `FLOW_MICROSOFT` is logged.
- Microsoft session data is cleared only after the Microsoft redirect is confirmed.
- Login succeeds.
- Browser remains open if MFA or manual user interaction appears.

Result:
- [ ] Pass
- [ ] Fail
- Notes:

## Update And Shutdown

### Test 7: Update Existing Installation

Steps:
1. Install the current released version.
2. Add or verify saved credentials and configuration.
3. Run the new installer or `install.bat`.
4. Start the updated application.

Expected:
- Existing `SintMaartenCampusAutologin.exe` is stopped before files are replaced.
- Application binaries are replaced.
- `%LOCALAPPDATA%\SintMaartenCampusAutologin` is preserved.
- Encrypted credentials, config files, and user preferences are preserved.

Result:
- [ ] Pass
- [ ] Fail
- Notes:

### Test 8: Close Application

Steps:
1. Start the application.
2. Start at least one login so a browser session exists.
3. Close the application window.
4. Check Task Manager.

Expected:
- `SintMaartenCampusAutologin.exe` fully disappears from Task Manager.
- No application-owned Chrome sessions remain running.
- No background worker, scheduler, monitoring, Flask, or static-server thread remains.
- No reboot is required.

Result:
- [ ] Pass
- [ ] Fail
- Notes:
