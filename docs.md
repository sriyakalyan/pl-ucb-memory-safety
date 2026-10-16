`pl-memory-exploit` element

Displays a terminal environment with gdb capabilities. Contains a file editor for editing input file

## Customization

| Attribute | Type | Default | Description|
| ------ | --- | --- | --- |
| `input-program` | Python file | Empty Python file | File that the student edits within `pl-file-editor`. |
| `vulnerable-program` | Python file | — | File that the instructor provides that takes in output(s) from `input-program`. |
| `enable-aslr` | boolean | false | Randomizes memory locations of the stack and code between executions. |
| `enable-canary` | boolean | false | Randomizes and inserts a canary value directly after the buffer, which causes a segfault if modified. |
| `enable-non-exec-pages` | boolean | false | Prevents code stored in inputs and variables from being executed. |
| `enable-interact` | boolean | false | Allows for the usage of an interact API that allows for IO support between the input and vulnerable programs. |
| `width` | integer | 500 | Max characters per line for displaying Python code. |
| `shellcode-in-environ-var` | boolean | false | Places the shellcode inside of an environment variable. If false, provides shellcode within `input-program`. |

run with 
docker run -it --rm -p 3000:3000 \
  -v "$PWD:/course" \
  -v "$PWD/pl_ag_jobs:/jobs" \
  -e HOST_JOBS_DIR="$PWD/pl_ag_jobs" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --platform linux/amd64 \
  --add-host=host.docker.internal:172.17.0.1 \
  prairielearn/prairielearn 2>&1 | tee pl.log