using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Security.Cryptography;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.Win32;

class Setup {
    const string Version="2.0.0-beta.9";
    const string PayloadSha="__PAYLOAD_SHA__";
    const string RegKey=@"Software\Microsoft\Windows\CurrentVersion\Uninstall\IdleboardBeta";
    static string Local { get { return Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData); } }
    static string Target { get { return Path.Combine(Local,"Programs","IdleboardBeta",Version); } }
    static Stream Payload() {
        var stream=Assembly.GetExecutingAssembly().GetManifestResourceStream("IdleboardPayload.zip");
        using(var hash=SHA256.Create()) {
            string actual=BitConverter.ToString(hash.ComputeHash(stream)).Replace("-","").ToLowerInvariant();
            if(actual!=PayloadSha)throw new InvalidDataException("O instalador está corrompido. Baixe novamente.");
        }
        stream.Position=0;return stream;
    }
    static void Shortcut(string path,string executable) {
        Type type=Type.GetTypeFromProgID("WScript.Shell");
        object shell=Activator.CreateInstance(type);
        object link=type.InvokeMember("CreateShortcut",BindingFlags.InvokeMethod,null,shell,new object[]{path});
        Type linkType=link.GetType();
        linkType.InvokeMember("TargetPath",BindingFlags.SetProperty,null,link,new object[]{executable});
        linkType.InvokeMember("WorkingDirectory",BindingFlags.SetProperty,null,link,new object[]{Path.GetDirectoryName(executable)});
        linkType.InvokeMember("Save",BindingFlags.InvokeMethod,null,link,null);
        System.Runtime.InteropServices.Marshal.FinalReleaseComObject(link);
        System.Runtime.InteropServices.Marshal.FinalReleaseComObject(shell);
    }
    static void Install() {
        if(!Environment.Is64BitOperatingSystem)throw new InvalidOperationException("Esta beta requer Windows de 64 bits.");
        if(Directory.Exists(Target))throw new InvalidOperationException("Esta versão já está instalada. Use o atalho ou desinstale antes de instalar novamente.");
        string parent=Path.GetFullPath(Path.Combine(Local,"Programs","IdleboardBeta"));
        Directory.CreateDirectory(parent);
        string stage=Path.Combine(parent,"stage-"+Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(stage);
        try {
            using(var stream=Payload())using(var zip=new ZipArchive(stream,ZipArchiveMode.Read)) {
                foreach(var entry in zip.Entries) {
                    string path=Path.GetFullPath(Path.Combine(stage,entry.FullName));
                    if(!path.StartsWith(stage+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Arquivo fora do pacote.");
                    if(String.IsNullOrEmpty(entry.Name)){Directory.CreateDirectory(path);continue;}
                    Directory.CreateDirectory(Path.GetDirectoryName(path));
                    using(var input=entry.Open())using(var output=File.Create(path))input.CopyTo(output);
                }
            }
            Directory.Move(stage,Target);
            string data=Path.Combine(Local,"IdleboardBeta");Directory.CreateDirectory(data);
            string uninstall=Path.Combine(data,"UninstallBeta.exe");
            File.Copy(Path.Combine(Target,"UninstallBeta.exe"),uninstall,true);
            string executable=Path.Combine(Target,"ZasaBoardBeta.exe");
            string menu=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Programs),"ZasaBoard Beta 2");
            Directory.CreateDirectory(menu);
            Shortcut(Path.Combine(menu,"ZasaBoard Beta 2.lnk"),executable);
            Shortcut(Path.Combine(menu,"Desinstalar.lnk"),uninstall);
            Shortcut(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory),"ZasaBoard Beta 2.lnk"),executable);
            using(var key=Registry.CurrentUser.CreateSubKey(RegKey)) {
                key.SetValue("DisplayName","ZasaBoard Beta 2");key.SetValue("DisplayVersion",Version);
                key.SetValue("Publisher","manzarek");key.SetValue("InstallLocation",Target);
                key.SetValue("DisplayIcon",executable);key.SetValue("UninstallString","\""+uninstall+"\"");
                key.SetValue("NoModify",1,RegistryValueKind.DWord);key.SetValue("NoRepair",1,RegistryValueKind.DWord);
            }
        } finally {
            string full=Path.GetFullPath(stage);
            if(full.StartsWith(parent+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase) && Directory.Exists(full))Directory.Delete(full,true);
        }
    }
    [STAThread]
    static int Main(string[] args) {
        bool silent=Array.IndexOf(args,"--silent")>=0;
        try {
            if(Array.IndexOf(args,"--verify")>=0){using(var stream=Payload())using(var zip=new ZipArchive(stream,ZipArchiveMode.Read)){if(zip.Entries.Count<20)throw new InvalidDataException();}return 0;}
            if(silent){Install();return 0;}
            Application.EnableVisualStyles();
            var form=new Form {Text="Instalar ZasaBoard Beta 2",ClientSize=new Size(510,235),StartPosition=FormStartPosition.CenterScreen,FormBorderStyle=FormBorderStyle.FixedDialog,MaximizeBox=false,Font=new Font("Segoe UI",10)};
            var label=new Label {Text="ZasaBoard Beta 2 "+Version+"\n\nGerenciamento de sessões de jogos no Windows.\nInstala somente para este usuário, sem pedir administrador.\nPerfis e logins começam vazios e ficam no seu computador.",Location=new Point(22,20),Size=new Size(465,145)};
            var button=new Button {Text="Instalar",Location=new Point(365,178),Size=new Size(120,35)};
            form.Controls.Add(label);form.Controls.Add(button);
            bool installing=false,finished=false;
            form.FormClosing+=(sender,e)=>{if(installing)e.Cancel=true;};
            button.Click+=async(sender,e)=>{
                if(finished){form.Close();return;}
                installing=true;button.Enabled=false;label.Text="Instalando o aplicativo…\nAguarde a conclusão.";
                try {
                    await Task.Run((Action)Install);
                    label.Text="Instalação concluída.\n\nUse o atalho ZasaBoard Beta 2 na área de trabalho.\nO Windows precisa ter Microsoft Edge WebView2 Runtime.";
                    button.Text="Concluir";button.Enabled=true;installing=false;finished=true;
                } catch(Exception error) {
                    installing=false;finished=true;label.Text="Não foi possível instalar.\n\n"+error.Message;button.Text="Fechar";button.Enabled=true;
                }
            };
            Application.Run(form);return 0;
        } catch(Exception error) {
            if(!silent)MessageBox.Show(error.Message,"ZasaBoard Beta 2",MessageBoxButtons.OK,MessageBoxIcon.Error);
            return 1;
        }
    }
}
