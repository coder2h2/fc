// fc.rs
// Rust native implementation of FileConnect (fc) module loader

use std::fs;
use std::io;
use std::process::Command;

pub struct FileConnectModule {
    pub filepath: String,
    pub text: String,
}

pub fn link(path: &str) -> io::Result<FileConnectModule> {
    let content = fs::read_to_string(path)?;
    Ok(FileConnectModule {
        filepath: path.to_string(),
        text: content,
    })
}

pub fn link_run(path: &str, args: &[&str]) -> io::Result<String> {
    let output = Command::new(path)
        .args(args)
        .output()?;
        
    if !output.status.success() {
        return Err(io::Error::new(io::ErrorKind::Other, "Script execution failed"));
    }
    
    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}
