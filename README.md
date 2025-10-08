Install the command-line tool:

```bash
npm i -g @lindy-robotics/cli
```

Modify `lindy.config.yaml` to connect to the robot. Test the connection:

```
lindy test
```

If all ok:

```
lindy push prod
```

Then check that process is running:

```
lindy status
```
