using System;
using System.IO;
using System.Windows.Forms;
using Microsoft.Win32;

class Uninstall {
    internal const string Version = "2.0.0-beta.9";
    [STAThread]
    static int Main(string[] args) {
        bool silent=Array.IndexOf(args,"--silent")>=0;
        string local=Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        string target=Path.GetFullPath(Path.Combine(local,"Programs","IdleboardBeta",Version));
        string expected=Path.GetFullPath(Path.Combine(local,"Programs","IdleboardBeta"))+Path.DirectorySeparatorChar;
        FileStream guard=null;
        try {
            if (!target.StartsWith(expected,StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Destino inválido.");
            if (!silent && MessageBox.Show("Remover o ZasaBoard Beta 2? Seus perfis e logins locais serão preservados.","Desinstalar",MessageBoxButtons.YesNo,MessageBoxIcon.Question)!=DialogResult.Yes) return 0;
            string data=Path.Combine(local,"IdleboardBeta","profiles");
            Directory.CreateDirectory(data);
            guard=new FileStream(Path.Combine(data,".idleboard-app.lock"),FileMode.OpenOrCreate,FileAccess.ReadWrite,FileShare.ReadWrite);
            guard.Lock(0,1);
            if (Directory.Exists(target)) Directory.Delete(target,true);
            string desktop=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory),"ZasaBoard Beta 2.lnk");
            if (File.Exists(desktop)) File.Delete(desktop);
            string menu=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Programs),"ZasaBoard Beta 2");
            foreach(string name in new[]{"ZasaBoard Beta 2.lnk","Desinstalar.lnk"}) {
                string file=Path.Combine(menu,name);if(File.Exists(file))File.Delete(file);
            }
            if (Directory.Exists(menu) && Directory.GetFileSystemEntries(menu).Length==0) Directory.Delete(menu);
            Registry.CurrentUser.DeleteSubKeyTree(@"Software\Microsoft\Windows\CurrentVersion\Uninstall\IdleboardBeta",false);
            if (!silent) MessageBox.Show("Aplicativo removido. Os dados locais foram preservados em:\n"+data,"ZasaBoard Beta 2");
            return 0;
        } catch(Exception error) {
            if(!silent)MessageBox.Show("Feche o ZasaBoard Beta 2 e tente novamente.\n"+error.Message,"Não foi possível desinstalar",MessageBoxButtons.OK,MessageBoxIcon.Error);
            return 1;
        } finally {if(guard!=null)guard.Dispose();}
    }
}
