using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

class Launcher {
    [STAThread]
    static int Main(string[] args) {
        try {
            string root = AppDomain.CurrentDomain.BaseDirectory;
            bool smoke = Array.IndexOf(args, "--smoke-test") >= 0;
            var start = new ProcessStartInfo(Path.Combine(root, "runtime", smoke ? "python.exe" : "pythonw.exe"));
            start.Arguments = "\"" + Path.Combine(root, "bootstrap.py") + "\"" + (smoke ? " --smoke-test" : "");
            start.WorkingDirectory = root;
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            start.EnvironmentVariables["IDLEBOARD_EDICAO"] = "uso";
            start.EnvironmentVariables["IDLEBOARD_DADOS"] = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "IdleboardBeta", smoke ? "teste-sintetico" : "profiles");
            start.EnvironmentVariables["TCL_LIBRARY"] = Path.Combine(root,"runtime","tcl","tcl8.6");
            start.EnvironmentVariables["TK_LIBRARY"] = Path.Combine(root,"runtime","tcl","tk8.6");
            using (var process = Process.Start(start)) {
                if (!smoke) return 0;
                if (!process.WaitForExit(20000)) { process.Kill(); return 2; }
                return process.ExitCode;
            }
        } catch (Exception error) {
            MessageBox.Show("Não foi possível iniciar o Idleboard Beta.\n" + error.Message, "Idleboard Beta", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }
}
