#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

/* does the same as the shell command: ls /usr/bin | grep x | wc -l */
int main(void)
{
    int first[2];
    int second[2];
    if (pipe(first) < 0) { perror("pipe first"); return 1; }
    if (pipe(second) < 0) {
        perror("pipe second");
        close(first[0]);
        close(first[1]);
        return 1;
    }

    pid_t ls_pid = fork();
    if (ls_pid < 0) {
        perror("fork ls");
        close(first[0]);
        close(first[1]);
        close(second[0]);
        close(second[1]);
        return 1;
    }
    if (ls_pid == 0) {
        close(STDOUT_FILENO);
        if (dup(first[1]) != STDOUT_FILENO) {
            perror("dup ls");
            exit(1);
        }
        close(first[0]);
        close(first[1]);
        close(second[0]);
        close(second[1]);
        execlp("ls", "ls", "/usr/bin", (char *)NULL);
        perror("exec ls");
        exit(127);
    }

    pid_t grep_pid = fork();
    if (grep_pid < 0) {
        perror("fork grep");
        close(first[0]);
        close(first[1]);
        close(second[0]);
        close(second[1]);
        waitpid(ls_pid, NULL, 0);
        return 1;
    }
    if (grep_pid == 0) {
        close(STDIN_FILENO);
        if (dup(first[0]) != STDIN_FILENO) {
            perror("dup grep input");
            exit(1);
        }
        close(STDOUT_FILENO);
        if (dup(second[1]) != STDOUT_FILENO) {
            perror("dup grep output");
            exit(1);
        }
        close(first[0]);
        close(first[1]);
        close(second[0]);
        close(second[1]);
        execlp("grep", "grep", "x", (char *)NULL);
        perror("exec grep");
        exit(127);
    }

    pid_t wc_pid = fork();
    if (wc_pid < 0) {
        perror("fork wc");
        close(first[0]);
        close(first[1]);
        close(second[0]);
        close(second[1]);
        waitpid(ls_pid, NULL, 0);
        waitpid(grep_pid, NULL, 0);
        return 1;
    }
    if (wc_pid == 0) {
        close(STDIN_FILENO);
        if (dup(second[0]) != STDIN_FILENO) {
            perror("dup wc");
            exit(1);
        }
        close(first[0]);
        close(first[1]);
        close(second[0]);
        close(second[1]);
        execlp("wc", "wc", "-l", (char *)NULL);
        perror("exec wc");
        exit(127);
    }

    close(first[0]);
    close(first[1]);
    close(second[0]);
    close(second[1]);
    waitpid(ls_pid, NULL, 0);
    waitpid(grep_pid, NULL, 0);
    waitpid(wc_pid, NULL, 0);
    return 0;
}
