# Presenting Labs 7 and 8

Open [the visual presentation](presentation.pdf) for the explanation and [the speaking notes](teaching-note.md) for what to say on each slide. The presentation uses simple vector diagrams, so the text and arrows stay sharp when projected.

For preparation from the task and core concepts, read the [Lab 7 visual study brief](../lab7/teaching-note.pdf) and [Lab 8 visual study brief](../lab8/teaching-note.pdf). Each uses the report's concept illustrations, points to its evidence pages and includes a ten-minute reading and practice route. The full teaching notes contain fifteen likely and five harder questions per lab, with checking answers after the prompts.

Use [the course study guide](course-study.md) to connect the four published course sessions to these two labs. It develops the prerequisites and the questions behind the code. The separate lab teaching notes trace the actual source and put practice answers after the questions.

| Material | Lab 7: Linux | Lab 8: xv6 |
| --- | --- | --- |
| Required source and run commands | [Open Lab 7](../lab7/README.md) | [Open Lab 8](../lab8/README.md) |
| Measured answers | [report.md](../lab7/report.md) | [notes.md](../lab8/notes.md) |
| Printable report | [report.pdf](../lab7/report.pdf) | [report.pdf](../lab8/report.pdf) |
| Full explanation and source traces | [teaching-note.md](../lab7/teaching-note.md) | [teaching-note.md](../lab8/teaching-note.md) |

For a short presentation, follow the diagrams for `fork`, `exec`, redirection, the Linux pipeline, EOF, the xv6 call path and `pingpong`, then demonstrate the programs. The remaining slides explain prerequisites, the measured results, optional prime filters and connections to the earlier filesystem labs. Use the full route when there is time for a longer explanation.

Before presenting, explain these three mechanisms aloud without reading: successful `exec` does not return; an empty pipe with a remaining writer is not EOF; the parent's reply `read` makes ping come before pong. Then attempt a changed-condition question from the speaking notes. A completed guide and successful program run do not establish independent understanding.

The [recorded execution session](execution-session-2026-10-19.txt) contains the 19 October Linux build/run output and xv6 build, boot and experiments. The original screenshots are in the separate lab assets folders and are embedded beside the report answers.
