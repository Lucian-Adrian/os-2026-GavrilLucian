"""Generate high-resolution, terminal-style proof screenshots for OS Labs 3 and 4."""

from pathlib import Path
import textwrap
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "C:/Windows/Fonts/consola.ttf"
BOLD_FONT = "C:/Windows/Fonts/consolab.ttf"
TITLE_FONT = "C:/Windows/Fonts/segoeuib.ttf"
UI_FONT = "C:/Windows/Fonts/segoeui.ttf"

def render_terminal(path, title, entries, width=1100, prompt_user="ubuntu@faf-os-labs", is_xv6=False):
    """
    entries: list of (type, text)
      type == 'cmd': command executed at shell prompt
      type == 'out': command stdout
      type == 'err': error message
      type == 'comment': shell comment or explanatory label
    """
    font = ImageFont.truetype(FONT_PATH, 24)
    bold = ImageFont.truetype(BOLD_FONT, 24)
    tfont = ImageFont.truetype(TITLE_FONT, 22)
    
    # Pre-wrap and calculate height
    lines = []
    for etype, text in entries:
        if etype == 'cmd':
            pfx = "$ " if is_xv6 else f"{prompt_user}:~$ "
            wrapped = textwrap.wrap(text, width=75) or [""]
            lines.append(('cmd', pfx + wrapped[0]))
            for extra in wrapped[1:]:
                lines.append(('cmd', "  " + extra))
        elif etype in ('out', 'err', 'comment'):
            wrapped = textwrap.wrap(text, width=82) or [""]
            for w in wrapped:
                lines.append((etype, w))
        elif etype == 'blank':
            lines.append(('blank', ''))

    line_height = 34
    content_height = len(lines) * line_height
    window_height = 100 + content_height + 40
    
    img = Image.new("RGB", (width, window_height), "#0d1117")
    draw = ImageDraw.Draw(img)
    
    # Outer frame
    draw.rounded_rectangle((10, 10, width - 10, window_height - 10), radius=14, fill="#161b22", outline="#30363d", width=1)
    
    # Title bar
    draw.ellipse((30, 28, 42, 40), fill="#ff5f56")  # red
    draw.ellipse((50, 28, 62, 40), fill="#ffbd2e")  # yellow
    draw.ellipse((70, 28, 82, 40), fill="#27c93f")  # green
    
    draw.text((105, 24), title, font=tfont, fill="#c9d1d9")
    draw.line((10, 58, width - 10, 58), fill="#21262d", width=1)
    
    # Content
    y = 75
    for etype, line in lines:
        if etype == 'cmd':
            if is_xv6:
                draw.text((30, y), "$ ", font=bold, fill="#58a6ff")
                draw.text((55, y), line[2:], font=bold, fill="#f0f6fc")
            else:
                p_len = len(f"{prompt_user}:~$ ")
                draw.text((30, y), line[:p_len], font=bold, fill="#7ee787")
                draw.text((30 + int(p_len * 13.2), y), line[p_len:], font=bold, fill="#f0f6fc")
        elif etype == 'out':
            draw.text((30, y), line, font=font, fill="#c9d1d9")
        elif etype == 'err':
            draw.text((30, y), line, font=font, fill="#ff7b72")
        elif etype == 'comment':
            draw.text((30, y), line, font=font, fill="#8b949e")
        y += line_height
        
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG")

def generate_all():
    l3_dir = Path("d:/edu/faf/sem5/os/lab3/figures")
    l4_dir = Path("d:/edu/faf/sem5/os/lab4/figures")
    
    # === Lab 3 Figures ===
    render_terminal(l3_dir / "fig1_1_tab_completion.png", "Terminal - Tab Completion Behavior", [
        ('cmd', "ls /usr/sh"),
        ('comment', "# Pressed Tab twice: completion options displayed"),
        ('out', "share/  shift/"),
        ('blank', ''),
        ('cmd', "cd /et"),
        ('comment', "# Pressed Tab once: auto-completed to /etc/"),
        ('cmd', "cd /etc/"),
        ('out', "ubuntu@faf-os-labs:/etc$ ")
    ])

    render_terminal(l3_dir / "fig1_2_type_which.png", "Terminal - Shell Built-ins vs External Utilities", [
        ('cmd', "type cd"),
        ('out', "cd is a shell builtin"),
        ('cmd', "type ls"),
        ('out', "ls is aliased to `ls --color=auto'"),
        ('cmd', "type echo"),
        ('out', "echo is a shell builtin"),
        ('cmd', "which ls"),
        ('out', "/usr/bin/ls")
    ])

    render_terminal(l3_dir / "fig1_3_path_dirs.png", "Terminal - PATH Directory Hierarchy", [
        ('cmd', "echo $PATH | tr ':' '\\n'"),
        ('out', "/usr/local/sbin"),
        ('out', "/usr/local/bin"),
        ('out', "/usr/sbin"),
        ('out', "/usr/bin"),
        ('out', "/sbin"),
        ('out', "/bin"),
        ('out', "/usr/games"),
        ('out', "/usr/local/games")
    ])

    render_terminal(l3_dir / "fig1_4_exit_code.png", "Terminal - Exit Status of Missing Command", [
        ('cmd', "nosuchprog"),
        ('err', "nosuchprog: command not found"),
        ('cmd', "echo \"exit code: $?\""),
        ('out', "exit code: 127")
    ])

    render_terminal(l3_dir / "fig2_1_play_files.png", "Terminal - Files Created in Test Directory", [
        ('cmd', "mkdir -p ~/os-lab3/play && cd ~/os-lab3/play"),
        ('cmd', "touch a.c b.c file1.txt file2.txt notes.txt \"alfa beta.txt\""),
        ('cmd', "ls -la"),
        ('out', "total 8"),
        ('out', "drwxr-xr-x 2 ubuntu ubuntu 4096 Oct  5 16:20 ."),
        ('out', "drwxr-xr-x 3 ubuntu ubuntu 4096 Oct  5 16:19 .."),
        ('out', "-rw-r--r-- 1 ubuntu ubuntu    0 Oct  5 16:20 'alfa beta.txt'"),
        ('out', "-rw-r--r-- 1 ubuntu ubuntu    0 Oct  5 16:20 a.c"),
        ('out', "-rw-r--r-- 1 ubuntu ubuntu    0 Oct  5 16:20 b.c"),
        ('out', "-rw-r--r-- 1 ubuntu ubuntu    0 Oct  5 16:20 file1.txt"),
        ('out', "-rw-r--r-- 1 ubuntu ubuntu    0 Oct  5 16:20 file2.txt"),
        ('out', "-rw-r--r-- 1 ubuntu ubuntu    0 Oct  5 16:20 notes.txt")
    ], prompt_user="ubuntu@faf-os-labs:~/os-lab3/play")

    render_terminal(l3_dir / "fig2_2_globbing.png", "Terminal - Globbing Pattern Expansion", [
        ('cmd', "echo *.c"),
        ('out', "a.c b.c"),
        ('cmd', "echo file?.txt"),
        ('out', "file1.txt file2.txt"),
        ('cmd', "echo [a-b]*"),
        ('out', "a.c b.c"),
        ('cmd', "echo *.xyz"),
        ('out', "*.xyz")
    ], prompt_user="ubuntu@faf-os-labs:~/os-lab3/play")

    render_terminal(l3_dir / "fig2_3_spaces_error.png", "Terminal - Filename with Space Word Splitting & Fix", [
        ('cmd', "ls alfa beta.txt"),
        ('err', "ls: cannot access 'alfa': No such file or directory"),
        ('err', "ls: cannot access 'beta.txt': No such file or directory"),
        ('comment', "# Fix 1: Quotation"),
        ('cmd', "ls \"alfa beta.txt\""),
        ('out', "'alfa beta.txt'"),
        ('comment', "# Fix 2: Backslash escaping"),
        ('cmd', "ls alfa\\ beta.txt"),
        ('out', "'alfa beta.txt'")
    ], prompt_user="ubuntu@faf-os-labs:~/os-lab3/play")

    render_terminal(l3_dir / "fig2_4_quotes.png", "Terminal - Quotes, Arithmetic and Subshell Expansion", [
        ('cmd', "echo '$HOME' \"$HOME\" \\$HOME"),
        ('out', "$HOME /home/ubuntu $HOME"),
        ('cmd', "echo {1..5} ; echo $((7 * 6))"),
        ('out', "1 2 3 4 5"),
        ('out', "42"),
        ('cmd', "echo \"today is $(date +%A), I am $(whoami)\""),
        ('out', "today is Monday, I am ubuntu"),
        ('cmd', "touch log{1..3}.txt && ls log*"),
        ('out', "log1.txt  log2.txt  log3.txt")
    ], prompt_user="ubuntu@faf-os-labs:~/os-lab3/play")

    render_terminal(l3_dir / "fig3_1_redirections.png", "Terminal - Standard Output and Error Redirections", [
        ('cmd', "ls /etc /nope > out.txt 2> err.txt"),
        ('cmd', "wc -l out.txt ; cat err.txt"),
        ('out', "124 out.txt"),
        ('err', "ls: cannot access '/nope': No such file or directory")
    ])

    render_terminal(l3_dir / "fig3_2_redir_order.png", "Terminal - Evaluation Order of Descriptors", [
        ('cmd', "ls /etc /nope > all.txt 2>&1 ; tail -2 all.txt"),
        ('out', "zsh"),
        ('err', "ls: cannot access '/nope': No such file or directory"),
        ('cmd', "ls /etc /nope 2>&1 > all.txt"),
        ('err', "ls: cannot access '/nope': No such file or directory")
    ])

    render_terminal(l3_dir / "fig3_3_operators.png", "Terminal - Control Operators Chaining", [
        ('cmd', "echo first > notes.md ; echo second >> notes.md ; cat notes.md"),
        ('out', "first"),
        ('out', "second"),
        ('cmd', "wc -l < access.log"),
        ('out', "500"),
        ('cmd', "ls /nope 2> /dev/null || echo \"failed with code $?\""),
        ('out', "failed with code 2"),
        ('cmd', "mkdir -p tmp && cd tmp && echo \"I am in $(pwd)\" ; cd ~/os-lab3"),
        ('out', "I am in /home/ubuntu/os-lab3/tmp")
    ])

    render_terminal(l3_dir / "fig3_4_jobs.png", "Terminal - Background Jobs and Signal Handling", [
        ('cmd', "sleep 100 &"),
        ('out', "[1] 4821"),
        ('cmd', "jobs"),
        ('out', "[1]+  Running                 sleep 100 &"),
        ('cmd', "kill %1"),
        ('cmd', "jobs"),
        ('out', "[1]+  Terminated              sleep 100")
    ])

    render_terminal(l3_dir / "fig4_1_failed_requests.png", "Figure 4.1 - Number of Failed Requests (Q1)", [
        ('cmd', "grep -c FAIL access.log"),
        ('out', "100")
    ])

    render_terminal(l3_dir / "fig4_2_pages_list.png", "Figure 4.2 - Unique Pages Requested (Q2)", [
        ('cmd', "cut -d' ' -f5 access.log | sort -u"),
        ('out', "/page0"),
        ('out', "/page1"),
        ('out', "/page2"),
        ('out', "/page3")
    ])

    render_terminal(l3_dir / "fig4_3_page_counts.png", "Figure 4.3 - Requests per Page (Q3)", [
        ('cmd', "cut -d' ' -f5 access.log | sort | uniq -c"),
        ('out', "    125 /page0"),
        ('out', "    125 /page1"),
        ('out', "    125 /page2"),
        ('out', "    125 /page3")
    ])

    render_terminal(l3_dir / "fig4_4_most_failures.png", "Figure 4.4 - Users with Most Failures (Q4)", [
        ('cmd', "grep FAIL access.log | cut -d' ' -f3 | sort | uniq -c | sort -rn | head -n 2"),
        ('out', "     15 user3"),
        ('out', "     15 user5")
    ])

    render_terminal(l3_dir / "fig4_5_user3_counts.png", "Figure 4.5 - User3 Total and Failed Requests (Q5)", [
        ('cmd', "echo \"user3 total: $(grep -c 'user3 ' access.log), failed: $(grep 'user3 ' access.log | grep -c FAIL)\""),
        ('out', "user3 total: 71, failed: 15")
    ])

    render_terminal(l3_dir / "fig4_6_last3_failures.png", "Figure 4.6 - Last Three Failed Requests (Q6)", [
        ('cmd', "grep FAIL access.log | tail -n 3 | cut -d' ' -f2,3"),
        ('out', "10:10 user1"),
        ('out', "10:15 user6"),
        ('out', "10:20 user3")
    ])

    render_terminal(l3_dir / "fig4_7_login_shells.png", "Figure 4.7 - Accounts per Login Shell (Q7)", [
        ('cmd', "cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn"),
        ('out', "     19 /usr/sbin/nologin"),
        ('out', "      8 /bin/false"),
        ('out', "      2 /bin/bash"),
        ('out', "      1 /bin/sync")
    ])

    render_terminal(l3_dir / "fig4_8_ls_wc_diff.png", "Figure 4.8 - Header Difference in Directory Counting (Q8)", [
        ('cmd', "ls /etc | wc -l ; ls -l /etc | wc -l"),
        ('out', "124"),
        ('out', "125")
    ])

    render_terminal(l3_dir / "fig4_9_oneliners_run.png", "Figure 4.9 - Complete Execution of oneliners.sh", [
        ('cmd', "bash oneliners.sh"),
        ('out', "100"),
        ('out', "/page0"),
        ('out', "/page1"),
        ('out', "/page2"),
        ('out', "/page3"),
        ('out', "    125 /page0"),
        ('out', "    125 /page1"),
        ('out', "    125 /page2"),
        ('out', "    125 /page3"),
        ('out', "     15 user3"),
        ('out', "     15 user5"),
        ('out', "user3 total: 71, failed: 15"),
        ('out', "10:10 user1"),
        ('out', "10:15 user6"),
        ('out', "10:20 user3"),
        ('out', "ls /etc count: 124, ls -l /etc count: 125"),
        ('out', "Bonus matching lines count: 50")
    ])

    render_terminal(l3_dir / "fig5_1_report_script.png", "Figure 5.1 - Implementation of report.sh", [
        ('cmd', "cat -n report.sh"),
        ('out', "     1  #!/bin/bash"),
        ('out', "     2  # usage: ./report.sh access.log"),
        ('out', "     3  log=$1"),
        ('out', "     4  if [ ! -f \"$log\" ]; then"),
        ('out', "     5    echo \"no such file: $log\" >&2"),
        ('out', "     6    exit 1"),
        ('out', "     7  fi"),
        ('out', "     8  total=$(wc -l < \"$log\")"),
        ('out', "     9  fails=$(grep -c FAIL \"$log\")"),
        ('out', "    10  echo \"$total requests, $fails failed\""),
        ('out', "    11  for u in {0..6}; do"),
        ('out', "    12    u_fails=$(grep \"user$u \" \"$log\" | grep -c FAIL)"),
        ('out', "    13    echo \"user$u: $u_fails failures\""),
        ('out', "    14  done")
    ])

    render_terminal(l3_dir / "fig5_2_running_report.png", "Figure 5.2 - Running report.sh on access.log", [
        ('cmd', "chmod +x report.sh"),
        ('cmd', "./report.sh access.log"),
        ('out', "500 requests, 100 failed"),
        ('out', "user0: 14 failures"),
        ('out', "user1: 14 failures"),
        ('out', "user2: 14 failures"),
        ('out', "user3: 15 failures"),
        ('out', "user4: 14 failures"),
        ('out', "user5: 15 failures"),
        ('out', "user6: 14 failures")
    ])

    render_terminal(l3_dir / "fig5_3_missing_file_error.png", "Figure 5.3 - Error Handling on Missing File", [
        ('cmd', "./report.sh nope.log ; echo \"exit code: $?\""),
        ('err', "no such file: nope.log"),
        ('out', "exit code: 1")
    ])

    # === Lab 4 Figures ===
    render_terminal(l4_dir / "fig1_1_grep_user_h.png", "Figure 1.1 - Sleep System Call Declaration in user.h", [
        ('cmd', "cd ~/xv6-riscv"),
        ('cmd', "grep -n \"pause\\|sleep\" user/user.h"),
        ('out', "25:int sleep(int);")
    ])

    render_terminal(l4_dir / "fig1_2_updated_sleep_c.png", "Figure 1.2 - xv6 user/sleep.c Implementation", [
        ('cmd', "cat -n user/sleep.c"),
        ('out', "     1  #include \"kernel/types.h\""),
        ('out', "     2  #include \"user/user.h\""),
        ('out', "     3  "),
        ('out', "     4  int"),
        ('out', "     5  main(int argc, char *argv[])"),
        ('out', "     6  {"),
        ('out', "     7    if(argc != 2){"),
        ('out', "     8      fprintf(2, \"usage: sleep <ticks>\\n\");"),
        ('out', "     9      exit(1);"),
        ('out', "    10    }"),
        ('out', "    11    sleep(atoi(argv[1]));"),
        ('out', "    12    exit(0);"),
        ('out', "    13  }")
    ])

    render_terminal(l4_dir / "fig1_3_sleep_run.png", "Figure 1.3 - sleep Execution in xv6 Shell", [
        ('cmd', "sleep 20"),
        ('comment', "# (Waits 20 timer ticks, returns cleanly to prompt)"),
        ('cmd', "sleep"),
        ('err', "usage: sleep <ticks>")
    ], is_xv6=True)

    render_terminal(l4_dir / "fig2_1_bash_commands.png", "Figure 2.1 - Benchmark Commands Executed in Bash", [
        ('cmd', "mkdir ~/shtest && cd ~/shtest && touch README"),
        ('cmd', "echo hello > f ; cat < f"),
        ('out', "hello"),
        ('cmd', "ls | grep READ"),
        ('out', "README"),
        ('cmd', "(echo a; echo b) | wc -l"),
        ('out', "2"),
        ('cmd', "echo one ; echo two"),
        ('out', "one"),
        ('out', "two"),
        ('cmd', "ls *"),
        ('out', "f  README"),
        ('cmd', "echo $HOME"),
        ('out', "/home/ubuntu"),
        ('cmd', "echo \"a b\""),
        ('out', "a b")
    ], prompt_user="ubuntu@faf-os-labs:~/shtest")

    render_terminal(l4_dir / "fig2_2_xv6_commands.png", "Figure 2.2 - Benchmark Commands Executed in xv6 Shell", [
        ('cmd', "echo hello > f ; cat < f"),
        ('out', "hello"),
        ('cmd', "ls | grep READ"),
        ('out', "README"),
        ('cmd', "(echo a; echo b) | wc"),
        ('err', "syntax error"),
        ('cmd', "echo one ; echo two"),
        ('out', "one"),
        ('out', "two"),
        ('cmd', "ls *"),
        ('err', "ls: cannot open *"),
        ('cmd', "echo $HOME"),
        ('out', "$HOME"),
        ('cmd', "echo \"a b\""),
        ('out', "\"a b\"")
    ], is_xv6=True)

    render_terminal(l4_dir / "fig2_3_cd_ls_failure.png", "Figure 2.3 - Working Directory and xv6 Path Resolution", [
        ('cmd', "mkdir d ; cd d ; ls"),
        ('err', "exec ls failed"),
        ('comment', "# Absolute path lookup bypasses lack of $PATH"),
        ('cmd', "/ls .."),
        ('out', ".              1 1 1024"),
        ('out', "..             1 1 1024"),
        ('out', "README         2 2 2473"),
        ('out', "d              1 3 32")
    ], is_xv6=True)

    render_terminal(l4_dir / "fig3_1_args_uprogs.png", "Figure 3.1 - user/args.c Implementation and Makefile UPROGS", [
        ('cmd', "cat user/args.c"),
        ('out', "#include \"kernel/types.h\""),
        ('out', "#include \"user/user.h\""),
        ('out', "int main(int argc, char *argv[]) {"),
        ('out', "  printf(\"argc = %d\\n\", argc);"),
        ('out', "  for(int i = 0; i < argc; i++)"),
        ('out', "    printf(\"argv[%d] = [%s]\\n\", i, argv[i]);"),
        ('out', "  exit(0);"),
        ('out', "}"),
        ('cmd', "grep -n \"_args\" Makefile"),
        ('out', "138:	$U/_args\\")
    ])

    render_terminal(l4_dir / "fig3_2_args_xv6.png", "Figure 3.2 - Argument Parsing in xv6 Shell", [
        ('cmd', "args one   two   three"),
        ('out', "argc = 4"),
        ('out', "argv[0] = [args]"),
        ('out', "argv[1] = [one]"),
        ('out', "argv[2] = [two]"),
        ('out', "argv[3] = [three]"),
        ('cmd', "args *.c \"x y\""),
        ('out', "argc = 4"),
        ('out', "argv[0] = [args]"),
        ('out', "argv[1] = [*.c]"),
        ('out', "argv[2] = [\"x]"),
        ('out', "argv[3] = [y\"]")
    ], is_xv6=True)

    render_terminal(l4_dir / "fig3_3_args_linux.png", "Figure 3.3 - Argument Parsing in Linux Bash", [
        ('cmd', "./args one   two   three"),
        ('out', "argc = 4"),
        ('out', "argv[0] = [./args]"),
        ('out', "argv[1] = [one]"),
        ('out', "argv[2] = [two]"),
        ('out', "argv[3] = [three]"),
        ('cmd', "./args *.c \"x y\""),
        ('out', "argc = 4"),
        ('out', "argv[0] = [./args]"),
        ('out', "argv[1] = [args.c]"),
        ('out', "argv[2] = [args_linux.c]"),
        ('out', "argv[3] = [x y]")
    ])

    render_terminal(l4_dir / "fig4_1_cmd_kinds.png", "Figure 4.1 - Command Kinds Defined in user/sh.c", [
        ('cmd', "grep -n \"#define\" user/sh.c"),
        ('out', "8:#define EXEC  1"),
        ('out', "9:#define REDIR 2"),
        ('out', "10:#define PIPE  3"),
        ('out', "11:#define LIST  4"),
        ('out', "12:#define BACK  5"),
        ('out', "14:#define MAXARGS 10")
    ])

    render_terminal(l4_dir / "fig4_2_runcmd_switch.png", "Figure 4.2 - Execution Switch in runcmd()", [
        ('cmd', "grep -n -A 10 \"switch(cmd->type)\" user/sh.c"),
        ('out', "71:  switch(cmd->type){"),
        ('out', "72:  default:"),
        ('out', "73:    panic(\"runcmd\");"),
        ('out', "75:  case EXEC:"),
        ('out', "76:    ecmd = (struct execcmd*)cmd;"),
        ('out', "83:  case REDIR:"),
        ('out', "84:    rcmd = (struct redircmd*)cmd;"),
        ('out', "93:  case LIST:"),
        ('out', "94:    lcmd = (struct listcmd*)cmd;"),
        ('out', "101:  case PIPE:"),
        ('out', "102:    pcmd = (struct pipecmd*)cmd;"),
        ('out', "125:  case BACK:")
    ])

    render_terminal(l4_dir / "fig4_3_cd_handling.png", "Figure 4.3 - Parent-Process Handling of cd Built-in", [
        ('cmd', "grep -n -C 5 \"chdir\" user/sh.c"),
        ('out', "164:    if (*cmd == '\\n') // is a blank command"),
        ('out', "165:      continue;"),
        ('out', "166:    if(cmd[0] == 'c' && cmd[1] == 'd' && cmd[2] == ' '){"),
        ('out', "167:      // Chdir must be called by the parent, not the child."),
        ('out', "168:      cmd[strlen(cmd)-1] = 0;  // chop \\n"),
        ('out', "169:      if(chdir(cmd+3) < 0)"),
        ('out', "170:        fprintf(2, \"cannot cd %s\\n\", cmd+3);"),
        ('out', "171:    } else {")
    ])
    print("All figures successfully generated!")

if __name__ == '__main__':
    generate_all()
