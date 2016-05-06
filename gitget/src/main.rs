#[macro_use]
extern crate lazy_static;
extern crate regex;

use std::env;
use std::process;
use std::fs;

use regex::Regex;


fn usage(prog: &str, env_var: &str) {
    println!("Usage: {} giturl [gopath]
git clone giturl gopath/src/giturl

Must supply gopath parameter or set {} environment variable.",
             prog,
             env_var);
}

/// If flag is given, returns it. 
/// If not, envrionment variable is read.
fn env_flag(env_var: &str, flag: Option<String>) -> Option<String> {
    if flag.is_some() {
        flag
    } else {
        match env::var(env_var) {
            Ok(x) => Some(x),
            Err(_) => None,
        }
    }
}



fn git_url_to_path(url: &str) -> Option<String> {
    lazy_static! {
        static ref GIT_URL: Regex = Regex::new(r"(?:.+@)?([^@:/]+):?(?:\d+)?([^:]+)$").unwrap();
    }

    match GIT_URL.captures(url) {
        Some(cap) => {
            Some(format!("{}/{}",
                         cap.at(1).unwrap(),
                         cap.at(2).unwrap().trim_right_matches(".git").trim_left_matches("/")))
        }
        None => None,
    }
}

fn main() {
    let GOPATH = "GOPATH";
    let mut args = env::args();
    let prog = args.next().unwrap();
    let mut argv = args;
    if argv.len() < 1 {
        usage(prog.as_str(), GOPATH);
        process::exit(1);
    }
    let giturl = argv.next().unwrap();
    let maybe_gopath = env_flag(GOPATH, argv.next());
    if maybe_gopath.is_none() {
        usage(prog.as_str(), GOPATH);
        process::exit(1);
    }
    let gopath = maybe_gopath.unwrap();

    let target_dir = match git_url_to_path(giturl.as_str()) {
        Some(p) => format!("{}/src/{}", gopath, p),
        None => {
            println!("Invalid giturl: {}", giturl.as_str());
            usage(prog.as_str(), GOPATH);
            process::exit(1);
        }

    };

    if fs::metadata(target_dir.as_str()).is_err() {
        println!("mkdir -p {}", target_dir.as_str());
        println!("git clone {} {}", giturl.as_str(), target_dir.as_str());
        // if fs::create_dir_all(targetDir.as_str()).is_err() {
        //     println!("Failed to create dir: {}", targetDir.as_str());
        //     process::exit(1);
        // }
    } else {
        println!("Directory already exists: {}", target_dir.as_str());
        process::exit(1);
    }


}

#[cfg(test)]
mod tests {
    use git_url_to_path;


    #[test]
    fn test_github_ssh() {
        let result = git_url_to_path("git@github.com:user/project.git");
        assert!(result.is_some());
        assert_eq!("github.com/user/project", result.unwrap());
    }

    #[test]
    fn test_github_https() {
        let result = git_url_to_path("https://github.com/user/project.git");
        assert!(result.is_some());
        assert_eq!("github.com/user/project", result.unwrap());
    }

    #[test]
    fn test_github_https_with_port() {
        let result = git_url_to_path("https://user@github.com:443/user/project.git");
        assert!(result.is_some());
        assert_eq!("github.com/user/project", result.unwrap());
    }
}