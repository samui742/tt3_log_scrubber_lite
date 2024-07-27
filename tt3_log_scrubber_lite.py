import re
import requests
import pyautogui
from art import text2art

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def extract_jobid_info(jobid):
    """To find out how many test units and corners on the provided jobid from html"""

    url = f"https://wwwin-testtracker3.cisco.com/trackerApp/cornerTest/{jobid}"
    response = requests.get(url, auth=(username, password))
    response.close()
    html = response.text

    uut_match = re.findall(r'UUT\d+ </span></td>', html)
    total_uut_list = []
    for match in uut_match:
        uut_id = re.search(r'\d+', match).group(0)
        if uut_id not in total_uut_list:
            total_uut_list.append(uut_id)

    corner_match = re.findall(r'data-cornerid="\d+"', html)
    total_corner_list = []
    for match in corner_match:
        corner_id = re.search(r'\d+', match).group(0)
        if corner_id not in total_corner_list:
            total_corner_list.append(corner_id)

    return total_corner_list, total_uut_list

def grab_switch_logs(uut, corner):
    """ Make a http request for switch log from tt3 and strip off all unnecessary parts"""

    url = f"https://wwwin-testtracker3.cisco.com/trackerApp/oneviewlog/switch{uut}.log?page=1&corner_id={corner}"

    response = requests.get(url, auth=(username, password))
    response.close()
    html_log = response.text

    try:
        content = html_log[html_log.index("Total testcases to execute"):html_log.index("/tmp/tt3")]

        corner_name_match = re.findall(r'cornerName :.*', html_log)
        corner_name_match = "".join(corner_name_match)
        corner_name = re.search(r': .*', corner_name_match).group(0).strip(': ').strip('Test').rstrip(" ")

    except ValueError:
        content = "unit " + str(uut) + (" log file was not found due to incomplete corner or unit is a link partner. Please check.")
        corner_name = "Incomplete"

    return content, url, corner_name

def user_selection (jobid, total_uut_list, total_corner_list):
    """ To offer user on selecting corner and uut to process then returned the selected list to process"""

    selected_corner_list = []
    selected_uut_list = []

    print(f'\nJOBID# {jobid} \nThere are total {len(total_corner_list)} corner(s)' + ' - Corner number: ',
          ','.join(map(str, range(1, len(total_corner_list) + 1))))
    corner_select = input(f'Press enter to search on all corners or specify corner number (using comma if there are '
                          f'multiples): ')
    print()

    if len(corner_select) == 0:
        print(f'\tuser selected all corners\n')
    else:
        print(f'\tuser selected corner {corner_select}\n')

    print(f'JOBID# {jobid} \nThere are total {len(total_uut_list)} unit(s)' + ' - Unit number: ', ','.join(map(str, total_uut_list)))
    uut_select = input(
        f'Press enter to search on all units or specify unit number (using comma if there are multiples): ')
    print()

    if len(uut_select) == 0:
        print(f'\tuser selected all units\n')
    else:
        print(f'\tuser selected unit {uut_select}\n')

    # Mapping between total and user selected
    if len(corner_select) == 0:
        selected_corner_list = total_corner_list
    else:
        corner_select = [x.strip() for x in corner_select.split(",")]
        for item in corner_select:
            selected_corner_list.append(total_corner_list[int(item) - 1])  # call value from corner_list by index

    if len(uut_select) == 0:
        selected_uut_list = total_uut_list
    else:
        uut_select = [x.strip() for x in uut_select.split(",")]
        for item in uut_select:
            if item in total_uut_list:
                selected_uut_list.append(int(item))

    return selected_corner_list, selected_uut_list

def handle_user_input (jobid_input, keyword_input):
    """function to covert multiple jobids and multiple keywords input from user into lists
    strip off commas and white spaces then append into lists
    also has code to support comma search and escape asterisk"""

    jobid_list = []
    if "," in str(jobid_input):
        jobid_list.extend(jobid_input.split(','))
        jobid_list = [item.strip() for item in jobid_list]
    else:
        jobid_list.append(str(jobid_input))

    keyword_list = []
    if "," in str(keyword_input):
        keyword_list = keyword_input.split(',')
        keyword_list = [item.strip() for item in keyword_list]
    else:
        keyword_list.append(str(keyword_input).strip())

    # Support comma search. User has to input as semicolon then code will replace to comma
    # Support asterisk search by adding backslash to escape asterisk
    if search_type != "custom_search" and search_type != "regexp_search":
        for i in range(len(keyword_list)):
            if ";" in keyword_list[i]:
                x = keyword_list[i].replace(";", ",")
                keyword_list[i] = x
            if "*" in keyword_list[i]:
                # x = keyword_list[i].replace("**", "\*\*")
                x = keyword_list[i].replace("*", "\*")
                keyword_list[i] = x

    return jobid_list, keyword_list

def log_search(jobid_input, keyword_input):
    """First make list of jobid and keyword from user input
    Second request html text of each jobid then find out how many corners and units on the jobid.
    Third ask user to select corner and uut to perform the search then create a new selected corner list and selected uut list.
    Forth make a log request then perform the search on each unit log then print out onscreen and write into text files.

    logs from tt3 then search for the keywords line by line
    then print out on the console and also write into a text file"""

    print('\n' + '=' * 150)
    jobid_list, keyword_list = handle_user_input(jobid_input, keyword_input)

    for jobid in jobid_list:
        total_corner_list, total_uut_list = extract_jobid_info(jobid)
        selected_corner_list, selected_uut_list = user_selection(jobid, total_uut_list, total_corner_list)
        for uut in selected_uut_list:
            result_file = f"{jobid}_uut{uut}_{search_type}_result.txt"
            with open(result_file, "w") as result_file:
                for corner in selected_corner_list:
                    content, url, corner_name = grab_switch_logs(uut, corner)
                    if len(keyword_input) != 0:
                        print("="*100)
                        print(f'jobid= {jobid} cornerid= {corner} cornername= {corner_name} unit= switch{uut}')
                        print("Searched Keyword(s) = ", keyword_list)
                        print(f'{url}')
                        print("="*100)
                        result_file.write("="*100 + "\n")
                        result_file.write(f'jobid= {jobid} cornerid= {corner} cornername= {corner_name} unit= switch{uut}' + "\n")
                        result_file.write(f"Searched Keyword(s) = , {keyword_list}" + "\n")
                        result_file.write(f"URL: {url}" + "\n")
                        result_file.write("="*100 + "\n")

                        lines = content.splitlines()
                        for line in lines:
                            # To handle crashed corner
                            if f'REMOVING switch{uut} FROM CURRENT CORNER - JOB' in line:
                                print(f'{bcolors.BOLD}{bcolors.WARNING} *** Corner is NOT completed, switch is removed from the current corner ***{bcolors.ENDC}')
                                result_file.write(
                                    '\nCorner is NOT completed, switch is removed from the current corner\n\n')
                            # To handle link partner unit which does not have log file
                            if "log file was not found due to incomplete corner or unit is a link partner. Please check" in line:
                                print(f'{bcolors.BOLD}{bcolors.WARNING}*** {line} ***{bcolors.ENDC}')
                                result_file.write(line + "\n")

                            for keyword in keyword_list:
                                # This part is for custom search which will not alter any content from what user input
                                if search_type == "custom_search":
                                    if keyword in line:
                                        print("\t\t\t" + f'{bcolors.OKCYAN}{line}{bcolors.ENDC}')
                                        result_file.write("\t\t\t" + line + "\n")
                                # This part is for regular expression search
                                elif search_type == "regexp_search":
                                    match_k = re.search(f"{keyword}", line)
                                    if match_k:
                                        print("\t\t\t" + f'{bcolors.OKCYAN}{line}{bcolors.ENDC}')
                                        result_file.write("\t\t\t" + line + "\n")
                                # This part is for pre-defined search
                                else:
                                    match_k = re.search(f"{keyword}", line)
                                    if match_k:
                                        if "TESTCASE START" in line:
                                            print("\t" + f'{line}')
                                            result_file.write("\t" + line + "\n")
                                        else:
                                            if "fail" in line.casefold():
                                                print("\t\t\t\t" + f'{bcolors.FAIL}{line}{bcolors.ENDC}')
                                                result_file.write("\t\t\t\t" + line + "\n")
                                            elif "pass" in line.casefold():
                                                print("\t\t\t\t" + f'{bcolors.OKGREEN}{line}{bcolors.ENDC}')
                                                result_file.write("\t\t\t\t" + line + "\n")
                                            else:
                                                print("\t\t\t" + f'{bcolors.OKCYAN}{line}{bcolors.ENDC}')
                                                result_file.write("\t\t\t" + line + "\n")
            result_file.close()
            print('\n' + '=' * 150)


if __name__ == '__main__':

    global username
    global password
    global search_type

    banner = text2art("EDVT TT3\nLog Scrubber\nLITE", space=1, font="small")
    print("\n" + banner + "\n")

    print('Enter CEC username and password in the popup window \n')

    username = pyautogui.prompt('input your cec username: ')
    password = pyautogui.password('input your password: ')
    if len(username) == 0 or len(password) == 0:
        print("Username and Password can't be blank. Please restart the program")
        quit()

    jobid_input = input("Enter JOBID (separate by comma for multiples): ")
    option = input(f'\nSelect type of search from below list \n\
    \n\
    1 - search by keywords "user can specify multiple keywords to search (case sensitive)" \n\
    2 - search by regular expression "user can specify regular expression to search (case sensitive)" \n\
    3 - diag powercycling & traffic "pre-defined keywords specifically for diag powercycling & traffic log scrubbing"\n\
    \n\nPlease enter the option number: ')

    if option == "1":
        search_type = "custom_search"
        keyword_input = input("Enter keywords separate by comma: ")
        log_search(jobid_input, keyword_input)

    if option == "2":
        search_type = "regexp_search"
        keyword_input = input("Enter regular expression format separate by comma: ")
        log_search(jobid_input, keyword_input)

    elif option == "3":
        search_type = "diag_traffic"
        keyword_input = "FAILED: Timeout, FAILED VALIDATION while, FAILED VALIDATION -, FAIL**  E, FAIL**  P, TESTCASE START -, Test\(s\) failed:, test\(s\) failed."  #9300
        keyword_input = "FAILED: Timeout, FAILED VALIDATION while, FAILED VALIDATION -, FAIL**, TESTCASE START -, Testcase Tag : TESTCASE START, Test\(s\) failed:, test\(s\) failed."  #9400
        # keyword_input = "FAILED: Timeout, FAILED VALIDATION while, FAILED VALIDATION -, FAIL**, Testcase Tag : TESTCASE START, Test\(s\) failed:, test\(s\) failed."  #9400
        log_search(jobid_input, keyword_input)
