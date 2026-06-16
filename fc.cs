// fc.cs
// C# native implementation of FileConnect (fc) loading logic

using System;
using System.IO;
using System.Diagnostics;

public static class fc {
    public static string LinkText(string filepath) {
        if (!File.Exists(filepath)) {
            throw new FileNotFoundException("FileConnect: file not found: " + filepath);
        }
        return File.ReadAllText(filepath);
    }

    public static string LinkRun(string filepath, string args) {
        ProcessStartInfo startInfo = new ProcessStartInfo() {
            FileName = filepath,
            Arguments = args,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        using (Process process = Process.Start(startInfo)) {
            using (StreamReader reader = process.StandardOutput) {
                string result = reader.ReadToEnd();
                process.WaitForExit();
                if (process.ExitCode != 0) {
                    string error = process.StandardError.ReadToEnd();
                    throw new Exception("Execution failed: " + error);
                }
                return result;
            }
        }
    }
}
