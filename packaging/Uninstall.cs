using System;
using System.IO;
using System.Windows.Forms;
using Microsoft.Win32;

class Uninstall {
    internal const string Version = "0.1.0-beta.1";
    [STAThread]
    static int Main(string[] args) {
        bool silent=Array.IndexOf(args,"--silent")>=0;
        string local=Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        string target=Path.GetFullPath(Path.Combine(local,"Programs","IdleboardBeta",Version));
        string expected=Path.GetFullPath(Path.Combine(local,"Programs","IdleboardBeta"))+Path.DirectorySeparatorChar;
        FileStream guard=null;
        try {
            if (!target.StartsWith(expected,StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Destino inválido.");
            if (!silent && MessageBox.Show("Remover o Idleboard Beta? Seus perfis e logins locais serão preservados.","Desinstalar",MessageBoxButtons.YesNo,MessageBoxIcon.Question)!=DialogResult.Yes) return 0;
            string data=Path.Combine(local,"IdleboardBeta","profiles");
            Directory.CreateDirectory(data);
            guard=new FileStream(Path.Combine(data,".idleboard-app.lock"),FileMode.OpenOrCreate,FileAccess.ReadWrite,FileShare.ReadWrite);
            guard.Lock(0,1);
            if (Directory.Exists(target)) Directory.Delete(target,true);
            string desktop=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory),"Idleboard Beta.lnk");
            if (File.Exists(desktop)) File.Delete(desktop);
            string menu=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Programs),"Idleboard Beta");
            foreach(string name in new[]{"Idleboard Beta.lnk","Desinstalar.lnk"}) {
                string file=Path.Combine(menu,name);if(File.Exists(file))File.Delete(file);
            }
            if (Directory.Exists(menu) && Directory.GetFileSystemEntries(menu).Length==0) Directory.Delete(menu);
            Registry.CurrentUser.DeleteSubKeyTree(@"Software\Microsoft\Windows\CurrentVersion\Uninstall\IdleboardBeta",false);
            if (!silent) MessageBox.Show("Aplicativo removido. Os dados locais foram preservados em:\n"+data,"Idleboard Beta");
            return 0;
        } catch(Exception error) {
            if(!silent)MessageBox.Show("Feche o Idleboard Beta e tente novamente.\n"+error.Message,"Não foi possível desinstalar",MessageBoxButtons.OK,MessageBoxIcon.Error);
            return 1;
        } finally {if(guard!=null)guard.Dispose();}
    }
}
