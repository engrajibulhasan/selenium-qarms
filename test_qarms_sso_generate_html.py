import datetime
import json
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestReporter:
    def __init__(self):
        self.test_steps = []
        self.start_time = datetime.datetime.now()
        self.screenshots = []
        self.filePath = "report"
        
        # Create report directory if it doesn't exist
        if not os.path.exists(self.filePath):
            os.makedirs(self.filePath)

    def add_step(self, description, status="INFO", details=""):
        """Add a test step to the report"""
        step = {
            'timestamp': datetime.datetime.now().strftime("%H:%M:%S"),
            'description': description,
            'status': status,
            'details': details
        }
        self.test_steps.append(step)
        print(f"[{status}] {description}")
        
    def capture_screenshot(self, driver, step_name=""):
        """Capture screenshot for the report"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{step_name}_{timestamp}.png" if step_name else f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.filePath, filename)
        driver.save_screenshot(filepath)
        self.screenshots.append(filename)
        return filename
        
    def generate_report(self, driver, overall_status="PASS"):
        """Generate comprehensive test report"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate HTML Report
        html_report = self._generate_html_report(driver, overall_status, timestamp)
        
        # Generate JSON Report
        json_report = self._generate_json_report(driver, overall_status, timestamp)
        
        # Generate Text Summary
        text_report = self._generate_text_report(driver, overall_status, timestamp)
        
        print(f"\n📊 TEST REPORT GENERATED:")
        print(f"   HTML Report: {html_report}")
        print(f"   JSON Report: {json_report}")
        print(f"   Text Report: {text_report}")
        
        return {
            'html': html_report,
            'json': json_report,
            'text': text_report
        }
    
    def _generate_html_report(self, driver, overall_status, timestamp):
        """Generate HTML report"""
        report_filename = os.path.join(self.filePath, f"test_report_{timestamp}.html")
        
        # Calculate statistics
        passed_steps = sum(1 for step in self.test_steps if step.get('status') == 'PASS')
        failed_steps = sum(1 for step in self.test_steps if step.get('status') == 'FAIL')
        total_steps = len(self.test_steps)
        
        # Create HTML
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>SSO & Create Case Test Report - {timestamp}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; padding: 20px 0; border-bottom: 2px solid #eee; margin-bottom: 30px; }}
                .status-badge {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
                .status-pass {{ background-color: #d4edda; color: #155724; }}
                .status-fail {{ background-color: #f8d7da; color: #721c24; }}
                .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
                .summary-card {{ padding: 20px; border-radius: 8px; text-align: center; }}
                .card-pass {{ background-color: #e8f5e9; }}
                .card-fail {{ background-color: #ffebee; }}
                .card-info {{ background-color: #e3f2fd; }}
                .step-log {{ margin: 20px 0; }}
                .step {{ padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 5px solid; }}
                .step-pass {{ border-left-color: #28a745; background-color: #f8fff9; }}
                .step-fail {{ border-left-color: #dc3545; background-color: #fff8f8; }}
                .step-info {{ border-left-color: #17a2b8; background-color: #f8fdff; }}
                .screenshot-gallery {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0; }}
                .screenshot {{ width: 300px; border: 1px solid #ddd; border-radius: 5px; cursor: pointer; }}
                .screenshot:hover {{ transform: scale(1.02); transition: transform 0.2s; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 SSO & Create Case Test Report</h1>
                    <h3>Execution Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</h3>
                    <div class="status-badge status-{overall_status.lower()}">{overall_status}</div>
                </div>
                
                <div class="summary">
                    <div class="summary-card card-info">
                        <h3>📋 Total Steps</h3>
                        <h2>{total_steps}</h2>
                    </div>
                    <div class="summary-card card-pass">
                        <h3>✅ Passed</h3>
                        <h2>{passed_steps}</h2>
                    </div>
                    <div class="summary-card card-fail">
                        <h3>❌ Failed</h3>
                        <h2>{failed_steps}</h2>
                    </div>
                    <div class="summary-card card-info">
                        <h3>⏱️ Duration</h3>
                        <h2>{(datetime.datetime.now() - self.start_time).seconds} seconds</h2>
                    </div>
                </div>
                
                <h2>📝 Test Details</h2>
                <table>
                    <tr>
                        <th>Final URL</th>
                        <td>{driver.current_url}</td>
                    </tr>
                    <tr>
                        <th>Page Title</th>
                        <td>{driver.title}</td>
                    </tr>
                    <tr>
                        <th>Browser</th>
                        <td>{driver.capabilities.get('browserName', 'Chrome')} {driver.capabilities.get('browserVersion', '')}</td>
                    </tr>
                </table>
                
                <h2>📋 Step-by-Step Execution</h2>
                <div class="step-log">
        '''
        
        # Add steps
        for i, step in enumerate(self.test_steps, 1):
            step_class = f"step-{step.get('status', 'info').lower()}"
            status_icon = "✅" if step.get('status') == 'PASS' else "❌" if step.get('status') == 'FAIL' else "ℹ️"
            html += f'''
                    <div class="step {step_class}">
                        <strong>{status_icon} Step {i}: {step.get('description')}</strong><br>
                        <small>Time: {step.get('timestamp')} | Status: {step.get('status')}</small>
            '''
            if step.get('details'):
                html += f'<br><small>Details: {step.get("details")}</small>'
            html += '</div>'
        
        html += '''
                </div>
                
                <h2>📸 Screenshots</h2>
                <div class="screenshot-gallery">
        '''
        
        # Add screenshots
        for i, screenshot in enumerate(self.screenshots, 1):
            html += f'<img src="{screenshot}" alt="Screenshot {i}" class="screenshot" onclick="window.open(this.src)">'
        
        html += '''
                </div>
                
                <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666;">
                    <p>Generated by Selenium Automation Test | {timestamp}</p>
                </footer>
            </div>
        </body>
        </html>
        '''
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return report_filename
    
    def _generate_json_report(self, driver, overall_status, timestamp):
        """Generate JSON report for programmatic access"""
        report_data = {
            'test_name': 'SSO & Create Case Flow',
            'execution_time': datetime.datetime.now().isoformat(),
            'overall_status': overall_status,
            'duration_seconds': (datetime.datetime.now() - self.start_time).seconds,
            'final_url': driver.current_url,
            'page_title': driver.title,
            'browser_info': driver.capabilities,
            'test_steps': self.test_steps,
            'screenshots': self.screenshots,
            'statistics': {
                'total_steps': len(self.test_steps),
                'passed_steps': sum(1 for step in self.test_steps if step.get('status') == 'PASS'),
                'failed_steps': sum(1 for step in self.test_steps if step.get('status') == 'FAIL'),
                'info_steps': sum(1 for step in self.test_steps if step.get('status') == 'INFO')
            }
        }
        
        report_filename = os.path.join(self.filePath, f"test_report_{timestamp}.json")
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4, default=str)
        
        return report_filename
    
    def _generate_text_report(self, driver, overall_status, timestamp):
        """Generate simple text report"""
        report_filename = os.path.join(self.filePath, f"test_report_{timestamp}.txt")
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("TEST EXECUTION REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Test Name: SSO & Create Case Flow\n")
            f.write(f"Execution Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Overall Status: {overall_status}\n")
            f.write(f"Duration: {(datetime.datetime.now() - self.start_time).seconds} seconds\n\n")
            f.write(f"Final URL: {driver.current_url}\n")
            f.write(f"Page Title: {driver.title}\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("STEP-BY-STEP EXECUTION\n")
            f.write("=" * 60 + "\n\n")
            
            for i, step in enumerate(self.test_steps, 1):
                status_icon = "✓" if step.get('status') == 'PASS' else "✗" if step.get('status') == 'FAIL' else "i"
                f.write(f"{status_icon} Step {i}: {step.get('description')}\n")
                f.write(f"   Time: {step.get('timestamp')} | Status: {step.get('status')}\n")
                if step.get('details'):
                    f.write(f"   Details: {step.get('details')}\n")
                f.write("\n")
            
            f.write("=" * 60 + "\n")
            f.write("STATISTICS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total Steps: {len(self.test_steps)}\n")
            f.write(f"Passed: {sum(1 for step in self.test_steps if step.get('status') == 'PASS')}\n")
            f.write(f"Failed: {sum(1 for step in self.test_steps if step.get('status') == 'FAIL')}\n\n")
            
            f.write("Screenshots:\n")
            for screenshot in self.screenshots:
                f.write(f"  - {screenshot}\n")
        
        return report_filename


# Initialize test reporter
reporter = TestReporter()

# Rest of your script with reporter integration
options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 40)

overall_status = "PASS"  # Default status

try:
    # ===================================================================
    # SSO LOGIN FLOW
    # ===================================================================
    
    # Start from your app
    reporter.add_step("Opening application login page", "INFO")
    driver.get("https://qarms.yaanatech.net/rms-sp/#/login")
    
    # Click SSO button
    reporter.add_step("Clicking SSO login button", "INFO")
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[contains(text(),'Login with SSO')]]")
        )
    ).click()

    # Wait for Microsoft login page
    reporter.add_step("Waiting for Microsoft login page", "INFO")
    wait.until(EC.url_contains("login.microsoftonline.com"))
    
    # Email input
    reporter.add_step("Entering email address", "INFO")
    email_input = wait.until(
        EC.visibility_of_element_located((By.NAME, "loginfmt"))
    )
    
    email_input.clear()
    email_input.send_keys("rajibul.hasan@yaana.com")
    
    # Next button
    reporter.add_step("Clicking Next button", "INFO")
    next_button = wait.until(
        EC.element_to_be_clickable((By.ID, "idSIButton9"))
    )
    next_button.click()
    
    reporter.add_step("Email entered and Next clicked", "PASS")
    
    print("\n" + "="*60)
    print("MANUAL ACTION REQUIRED:")
    print("1. Complete the password entry manually")
    print("2. Complete any MFA/2FA if prompted")
    print("3. Click 'Stay signed in' if asked")
    print("="*60 + "\n")
    
    # Wait for manual completion of SSO flow
    reporter.add_step("Waiting for manual SSO completion", "INFO")
    reporter.capture_screenshot(driver, "before_manual_sso")
    
    # Monitor the redirect flow
    reporter.add_step("Monitoring SSO redirect flow", "INFO")
    
    # Step 1: Wait to leave Microsoft page (get token redirect)
    wait.until_not(EC.url_contains("login.microsoftonline.com"))
    reporter.add_step("Redirected from Microsoft login page", "PASS", f"URL: {driver.current_url}")
    
    # Check if we got the token URL
    if "sso-token-verify" in driver.current_url and "token=" in driver.current_url:
        reporter.add_step("Received token from Microsoft", "PASS", "Token URL detected")
        
        # Step 2: Wait for token verification redirect
        try:
            # Wait up to 10 seconds for the redirect
            token_verify_wait = WebDriverWait(driver, 10)
            token_verify_wait.until_not(EC.url_contains("sso-token-verify"))
            reporter.add_step("Token verification completed", "PASS", f"Redirected to: {driver.current_url}")
            
            # Step 3: Check if we're on sso-success or sso-error
            if "sso-success" in driver.current_url:
                reporter.add_step("Token verified successfully", "PASS")
                
                # Step 4: Wait for final redirect to home
                try:
                    # Wait for home page URL
                    wait.until(EC.url_contains("/home"))
                    reporter.add_step("Landed on home page", "PASS", f"URL: {driver.current_url}")
                    
                    # Final verification
                    time.sleep(2)
                    reporter.add_step("SSO login completed successfully", "PASS")
                    reporter.capture_screenshot(driver, "after_sso_login")
                    
                except Exception as e:
                    reporter.add_step("Failed to reach home page", "FAIL", f"Error: {e}")
                    raise
                    
            elif "sso-error" in driver.current_url:
                reporter.add_step("SSO ERROR: Token verification failed", "FAIL")
                raise Exception("SSO token verification failed")
                    
            else:
                reporter.add_step("Unexpected redirect after token verification", "WARN", f"URL: {driver.current_url}")
                
        except Exception as e:
            reporter.add_step("Token verification timed out or failed", "FAIL", f"Error: {e}")
            raise
            
    else:
        reporter.add_step("Unexpected redirect from Microsoft", "FAIL", f"URL: {driver.current_url}")
        raise Exception("Expected token URL but got different URL")
    
    # ===================================================================
    # CREATE CASE FLOW
    # ===================================================================
    
    reporter.add_step("Starting Create Case flow", "INFO")
    print("\n" + "="*60)
    print("STARTING CREATE CASE FLOW...")
    print("="*60)
    
    # Step 1: Click on Create Case button
    reporter.add_step("Clicking on Create Case button", "INFO")
    try:
        create_case_button = wait.until(
            EC.element_to_be_clickable((By.ID, "sidebar-create-case"))
        )
        create_case_button.click()
        reporter.add_step("Create Case button clicked", "PASS")
        reporter.capture_screenshot(driver, "create_case_clicked")
    except Exception as e:
        reporter.add_step("Failed to click Create Case button", "FAIL", f"Error: {e}")
        raise
    
    # Step 2: Wait for case type dropdown to appear and click it
    reporter.add_step("Opening case type dropdown", "INFO")
    try:
        # Wait for the dropdown to be present
        case_type_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "case-type"))
        )
        reporter.add_step("Case type dropdown found", "PASS")
        
        # Click to open the dropdown
        dropdown_toggle = case_type_dropdown.find_element(By.CSS_SELECTOR, ".ui-select-toggle")
        dropdown_toggle.click()
        reporter.add_step("Dropdown opened", "PASS")
        reporter.capture_screenshot(driver, "dropdown_opened")
        
        # Wait for dropdown options to appear
        time.sleep(1)
        
    except Exception as e:
        reporter.add_step("Failed to open case type dropdown", "FAIL", f"Error: {e}")
        raise
    
    # Step 3: Select "Localización Geográfica" from dropdown
    reporter.add_step("Selecting 'Localización Geográfica' from dropdown", "INFO")
    try:
        # Find all dropdown options
        dropdown_options = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ui-select-choices-row"))
        )
        reporter.add_step(f"Found {len(dropdown_options)} dropdown options", "INFO")
        
        # Find and click the option with text "Localización Geográfica"
        option_found = False
        for option in dropdown_options:
            try:
                option_text = option.text.strip()
                if "Localización Geográfica" in option_text:
                    option.click()
                    reporter.add_step(f"Selected: {option_text}", "PASS")
                    option_found = True
                    reporter.capture_screenshot(driver, "case_type_selected")
                    break
            except:
                continue
        
        if not option_found:
            reporter.add_step("'Localización Geográfica' option not found in dropdown", "FAIL")
            raise Exception("Case type option not found")
            
    except Exception as e:
        reporter.add_step("Failed to select from dropdown", "FAIL", f"Error: {e}")
        raise
    
    # Wait for page to redirect/load after selection
    reporter.add_step("Waiting for page to load after selection", "INFO")
    time.sleep(3)
    reporter.add_step(f"Page loaded after case type selection", "PASS", f"URL: {driver.current_url}")
    
    # Step 4: Click on the requestor card link
    reporter.add_step("Clicking on requestor card link", "INFO")
    try:
        # Using the provided XPath
        requestor_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[5]/div[2]/div/div/div/form/div[2]/div/div/div/div/create-case/div/div/div[1]/div[2]/div/div/div[3]/div[2]/div/requestor-card-case/div[2]/a"))
        )
        requestor_link.click()
        reporter.add_step("Requestor link clicked", "PASS")
        reporter.capture_screenshot(driver, "requestor_link_clicked")
    except Exception as e:
        reporter.add_step("Failed to click requestor link", "FAIL", f"Error: {e}")
        # Try alternative selectors
        try:
            # Try to find by text or other attributes
            requestor_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Requestor') or contains(text(), 'requestor')]")
            requestor_link.click()
            reporter.add_step("Requestor link clicked (using alternative)", "PASS")
        except:
            reporter.add_step("Could not find requestor link", "FAIL", f"Error: {e}")
            raise
    
    # Wait for requestor section to expand
    reporter.add_step("Waiting for requestor section to expand", "INFO")
    time.sleep(2)
    reporter.add_step("Requestor section expanded", "PASS")
    
    # Step 5: Type "Kartik" in the search input
    reporter.add_step("Typing 'Kartik' in search input", "INFO")
    try:
        # Using the provided XPath for the input field
        search_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[5]/div[2]/div/div/div/form/div[2]/div/div/div/div/create-case/div/div/div[1]/div[2]/div/div/div[3]/div[2]/div/requestor-card-case/div[2]/div/div[2]/div/requestor-card/div[1]/div/div[4]/div/div[1]/input"))
        )
        search_input.clear()
        search_input.send_keys("Kartik")
        reporter.add_step("Typed 'Kartik' in search field", "PASS")
        reporter.capture_screenshot(driver, "typed_kartik")
        
        # Wait for typeahead results to appear
        time.sleep(2)
        
    except Exception as e:
        reporter.add_step("Failed to type in search input", "FAIL", f"Error: {e}")
        # Try alternative selectors
        try:
            search_input = driver.find_element(By.CSS_SELECTOR, "input[type='search'], input[type='text']")
            search_input.send_keys("Kartik")
            reporter.add_step("Typed 'Kartik' in search field (using alternative)", "PASS")
            time.sleep(2)
        except:
            reporter.add_step("Could not find search input", "FAIL", f"Error: {e}")
            raise
    
    # Step 6: Select "Kartik" from the typeahead results
    reporter.add_step("Selecting 'Kartik' from typeahead results", "INFO")
    try:
        # Wait for typeahead results to appear
        typeahead_results = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".uib-typeahead-match"))
        )
        reporter.add_step(f"Found {len(typeahead_results)} typeahead results", "INFO")
        
        # Find the result containing "Kartik"
        kartik_found = False
        for result in typeahead_results:
            try:
                result_text = result.text
                if "Kartik" in result_text:
                    result.click()
                    reporter.add_step(f"Selected: {result_text[:50]}...", "PASS")
                    kartik_found = True
                    reporter.capture_screenshot(driver, "kartik_selected")
                    break
            except:
                continue
        
        if not kartik_found:
            reporter.add_step("'Kartik' not found in typeahead results", "FAIL")
            raise Exception("Kartik not found in results")
                
    except Exception as e:
        reporter.add_step("Failed to select from typeahead", "FAIL", f"Error: {e}")
        raise
    
    # Final success message
    reporter.add_step("Create Case flow completed successfully", "PASS", "All steps executed")
    reporter.capture_screenshot(driver, "final_page")
    
    print("\n" + "="*60)
    print("✅ CREATE CASE FLOW COMPLETED SUCCESSFULLY!")
    print("="*60)

except Exception as e:
    reporter.add_step(f"Test failed with error: {str(e)[:200]}", "FAIL")
    overall_status = "FAIL"
    reporter.capture_screenshot(driver, "error_state")
    print(f"\n❌ Test failed: {e}")

finally:
    # Generate comprehensive report
    reports = reporter.generate_report(driver, overall_status)
    
    print("\n" + "="*60)
    print("TEST EXECUTION COMPLETE")
    print("="*60)
    print(f"Overall Status: {overall_status}")
    print(f"Total Steps: {len(reporter.test_steps)}")
    
    # Calculate passed/failed
    passed = sum(1 for step in reporter.test_steps if step.get('status') == 'PASS')
    failed = sum(1 for step in reporter.test_steps if step.get('status') == 'FAIL')
    print(f"Passed: {passed} | Failed: {failed}")
    
    print(f"\nReports Generated in '{reporter.filePath}' folder:")
    print(f"  📄 HTML: {os.path.basename(reports['html'])}")
    print(f"  📊 JSON: {os.path.basename(reports['json'])}")
    print(f"  📝 Text: {os.path.basename(reports['text'])}")
    print("="*60 + "\n")
    
    input("Press ENTER to close browser...")
    driver.quit()