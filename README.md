# TT3 Log Scrubber Lite Version
================================
## Purpose

This tool is built to help test engineer on reducing the test log scrubbing time and reduce human error. 
The current problem that we have is test engineer spend a vast amount of time on searching for the failure keywords from the test tracker3 test log. 
Especially on the test effort which has multiple test units tested on multiple corners. Test engineer have to open the log of each test unit and each corner then manually search for failure keywords by search function on the browser.
This process is time-consuming and prone to human error. Important error message could be overlooked from this manual search process.

================================
## Instruction
1. Start the program by execute the python file name "tt3_log_scrubber_lite.py".
2. A window will popup asking for CEC username and password.

![image](https://github.com/user-attachments/assets/9d549ff3-e9cc-49f8-91a3-42fa5baf3d7a)


4. After authorized, back to the main window, user will input TT3 jobid# which would like to be processed.
   * Note: the tool supports multiple jobids separate by commas. The jobid will be processed in order manner.
  
![image](https://github.com/user-attachments/assets/56ec4061-8f73-4fd7-89f4-c4e3950a3d96)


5. Tool will ask on what type of search that user want to process on the jobid(s). User will need to input the option number.
   On this Lite version, tool supports three types of scrubbing,
     1. search by keyword : user can specify a keyword or multiple keywords to search (case sensitive only)
     2. search by regular expression : user can specify a single or multiple regular expression to search (case sensitvie only)
     3. search by predefined keyword : a list of keywords is already selected for the proper seach for each test scenarios.
        current version supports only "diag power cycling & traffic"
        
     * Note: Tool does not support multiple search types. Only single search type is allowed at a time.

![image](https://github.com/user-attachments/assets/1a56626e-de8b-4cf9-933f-c18fac3ce4fc)

6. Tool will ask if user need to specify corner number to process.
  - User can put a corner number or multiple corners separated by commas.
  - If need to process all corner, user will just leave blank and press enter.

![image](https://github.com/user-attachments/assets/4af18e2f-a13f-4cf6-8b96-10fa584c1195)

7. Tool will ask if user need to specify test unit number to process.
  - User can put a test unit number or multiple units separated by commas.
  - If need to process all test units, user will just leave blank and press enter.

![image](https://github.com/user-attachments/assets/344b4ad0-026a-4a48-9eb7-bd50f8a6af2a)

8. After that the program will start searching for keywords or regular expression as user selected.
   The result will be both printed out on the terminal and also be written into text files separated for each unit.

![image](https://github.com/user-attachments/assets/7a09a329-0f85-420f-8836-7bcd3cc4ee69)

![image](https://github.com/user-attachments/assets/4ed2f293-e40c-46ba-8708-27b565fa8c44)

9. A sample video clip on how to use the tool is attached on below.
    
 ![regular_expression_gif_screencastify](https://github.com/user-attachments/assets/72a2af5a-96ea-4108-91d9-19136f6f52b7)

   
