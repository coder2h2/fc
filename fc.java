// fc.java
// Java native implementation of FileConnect (fc) loading logic

import java.nio.file.Files;
import java.nio.file.Paths;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class fc {
    public static String linkText(String filepath) throws Exception {
        return new String(Files.readAllBytes(Paths.get(filepath)));
    }

    public static String linkRun(String filepath, String... args) throws Exception {
        String[] cmd = new String[args.length + 1];
        cmd[0] = filepath;
        System.arraycopy(args, 0, cmd, 1, args.length);

        ProcessBuilder pb = new ProcessBuilder(cmd);
        Process process = pb.start();

        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder builder = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            builder.append(line).append("\n");
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Process failed with exit code: " + exitCode);
        }

        return builder.toString();
    }
}
