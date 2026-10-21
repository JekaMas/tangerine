// Package localctl owns Docker lifecycle only. Archive semantics and domain
// storage remain in recovery and app respectively; no Docker socket enters web.
package localctl

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"syscall"
	"time"
)

type Controller struct{ Root, Project, Runtime string }

var projectPattern = regexp.MustCompile(`^[a-z0-9][a-z0-9_-]*$`)

func (c Controller) command(ctx context.Context, args ...string) *exec.Cmd {
	return exec.CommandContext(ctx, "docker", args...)
}
func (c Controller) compose(ctx context.Context, args ...string) *exec.Cmd {
	prefix := []string{"compose", "--project-name", c.Project, "--env-file", filepath.Join(c.Root, ".env"), "--env-file", c.Runtime, "-f", filepath.Join(c.Root, "deploy/local/compose.yaml")}
	return c.command(ctx, append(prefix, args...)...)
}
func run(cmd *exec.Cmd) error {
	cmd.Stdout = io.Discard
	cmd.Stderr = io.Discard
	if e := cmd.Run(); e != nil {
		return errors.New("LOCAL_MAINTENANCE_FAILED: Docker action failed; saved data is retained. Check scripts/tangerine logs")
	}
	return nil
}
func (c Controller) running(ctx context.Context) ([]string, error) {
	out, e := c.compose(ctx, "ps", "--status", "running", "--services").Output()
	if e != nil {
		return nil, e
	}
	selected := []string{}
	for _, name := range strings.Fields(string(out)) {
		switch name {
		case "web", "api", "speech", "llm-lab":
			selected = append(selected, name)
		}
	}
	return selected, nil
}
func (c Controller) volume(ctx context.Context, name string) bool {
	return c.command(ctx, "volume", "inspect", c.Project+"_"+name).Run() == nil
}
func (c Controller) snapshotArgs(ctx context.Context, restore bool) []string {
	args := []string{"run", "--rm", "--no-deps", "--user", "0", "-T"}
	for _, name := range []string{"models", "lab"} {
		volume := map[string]string{"models": "speech-models", "lab": "lab-data"}[name]
		if restore || c.volume(ctx, volume) {
			mount := "/snapshot-" + name + ":ro"
			if restore {
				mount = "/restore-" + name
			}
			args = append(args, "-v", c.Project+"_"+volume+":"+mount)
		}
	}
	mode := "snapshot-create"
	if restore {
		mode = "snapshot-restore"
	}
	return append(args, "api", mode)
}
func (c Controller) Backup(ctx context.Context, name string) (result map[string]any, err error) {
	if !regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9_.-]*\.tar\.gz$`).MatchString(name) {
		return nil, errors.New("BACKUP_NAME_INVALID: use a basename ending .tar.gz")
	}
	destination := filepath.Join(c.Root, "data/backups", name)
	if _, e := os.Lstat(destination); !os.IsNotExist(e) {
		return nil, errors.New("BACKUP_EXISTS: select a new destination")
	}
	if e := os.MkdirAll(filepath.Dir(destination), 0700); e != nil {
		return nil, e
	}
	file, e := os.CreateTemp(filepath.Dir(destination), ".partial-*")
	if e != nil {
		return nil, e
	}
	defer os.Remove(file.Name())
	defer file.Close()
	active, e := c.running(ctx)
	if e != nil {
		return nil, e
	}
	if len(active) > 0 {
		if e = run(c.compose(ctx, append([]string{"stop"}, active...)...)); e != nil {
			return nil, e
		}
	}
	// Restore only services that were running, including on interrupted export.
	defer func() {
		if len(active) > 0 {
			end, cancel := context.WithTimeout(context.Background(), 90*time.Second)
			defer cancel()
			if resumeErr := run(c.compose(end, append([]string{"start"}, active...)...)); resumeErr != nil && err == nil {
				err = errors.New("BACKUP_SAVED_RESTART_REQUIRED: snapshot saved; run scripts/tangerine start to recover services")
			}
		}
	}()
	cmd := c.compose(ctx, c.snapshotArgs(ctx, false)...)
	cmd.Stdout = file
	cmd.Stderr = io.Discard
	if e = cmd.Run(); e != nil {
		return nil, errors.New("BACKUP_FAILED: snapshot is incomplete; previous workspace retained")
	}
	if e = file.Sync(); e != nil {
		return nil, e
	}
	if e = file.Close(); e != nil {
		return nil, e
	}
	// Publish exclusively. A concurrent export must never replace a saved backup.
	if e = os.Link(file.Name(), destination); e != nil {
		return nil, e
	}
	return map[string]any{"status": "complete", "backup": destination, "secrets_included": false, "inference_calls": 0}, nil
}
func (c Controller) Restore(ctx context.Context, archive, target string) (map[string]any, error) {
	if !projectPattern.MatchString(target) || target == c.Project {
		return nil, errors.New("RESTORE_TARGET_INVALID: choose a new project name")
	}
	if e := c.command(ctx, "info").Run(); e != nil {
		return nil, e
	}
	for _, kind := range []string{"container", "volume"} {
		args := []string{"ps", "-aq", "--filter", "label=com.docker.compose.project=" + target}
		if kind == "volume" {
			args = []string{"volume", "ls", "-q", "--filter", "label=com.docker.compose.project=" + target}
		}
		out, e := c.command(ctx, args...).Output()
		if e != nil {
			return nil, e
		}
		if len(strings.TrimSpace(string(out))) > 0 {
			return nil, errors.New("RESTORE_TARGET_EXISTS: existing resources are preserved")
		}
	}
	for _, volume := range []string{"postgres-data", "minio-data", "speech-models", "lab-data", "provider-credentials"} {
		if c.command(ctx, "volume", "inspect", target+"_"+volume).Run() == nil {
			return nil, errors.New("RESTORE_TARGET_EXISTS: existing named volume retained")
		}
	}
	runtime := filepath.Join(c.Root, "data/config/restores", target, "runtime.env")
	if _, e := os.Stat(filepath.Dir(runtime)); !os.IsNotExist(e) {
		return nil, errors.New("RESTORE_TARGET_EXISTS: target configuration already exists")
	}
	file, e := os.Open(archive)
	if e != nil {
		return nil, errors.New("BACKUP_MISSING: supply an existing backup archive")
	}
	defer file.Close()
	// Configure is executed by the same source-built image; no host runtimes.
	if e = os.MkdirAll(filepath.Dir(filepath.Dir(runtime)), 0700); e != nil {
		return nil, e
	}
	if e = os.Mkdir(filepath.Dir(runtime), 0700); e != nil {
		return nil, e
	}
	configure := c.command(ctx, "run", "--rm", "--user", fmt.Sprintf("%d:%d", os.Getuid(), os.Getgid()), "-v", filepath.Join(c.Root, ".env")+":/operator.env:ro", "-v", filepath.Dir(runtime)+":/runtime", "-e", "TANGERINE_OPERATOR_FILE=/operator.env", "-e", "TANGERINE_RUNTIME_DIR=/runtime", c.Project+"-api:local", "configure")
	if e = run(configure); e != nil {
		return nil, e
	}
	next := Controller{Root: c.Root, Project: target, Runtime: runtime}
	for _, service := range []string{"api", "minio", "speech", "web"} {
		if e = run(c.command(ctx, "tag", c.Project+"-"+service+":local", target+"-"+service+":local")); e != nil {
			return nil, e
		}
	}
	// Mark failed targets explicitly; never select a partially restored namespace.
	status := filepath.Join(filepath.Dir(runtime), "status")
	_ = os.WriteFile(status, []byte("incomplete\n"), 0600)
	if e = run(next.compose(ctx, "up", "-d", "--wait", "--wait-timeout", "120", "postgres", "minio")); e != nil {
		return nil, e
	}
	cmd := next.compose(ctx, next.snapshotArgs(ctx, true)...)
	cmd.Stdin = file
	var output strings.Builder
	cmd.Stdout = &output
	cmd.Stderr = io.Discard
	if e = cmd.Run(); e != nil {
		return nil, errors.New("RESTORE_FAILED: corrupt, incompatible or incomplete backup; previous workspace remains selected. Failed target retained for inspection")
	}
	var result map[string]any
	if e = json.Unmarshal([]byte(output.String()), &result); e != nil {
		return nil, e
	}
	if e = os.WriteFile(status, []byte("ready\n"), 0600); e != nil {
		return nil, e
	}
	result["project"] = target
	result["selected"] = false
	return result, nil
}
func (c Controller) Switch(ctx context.Context, target string) (map[string]any, error) {
	if !projectPattern.MatchString(target) {
		return nil, errors.New("WORKSPACE_INVALID")
	}
	runtime := filepath.Join(c.Root, "data/config/restores", target, "runtime.env")
	original, _ := os.ReadFile(filepath.Join(c.Root, "data/config/original-project"))
	if target == strings.TrimSpace(string(original)) {
		runtime = filepath.Join(c.Root, "data/config/runtime.env")
	} else {
		status, e := os.ReadFile(filepath.Join(filepath.Dir(runtime), "status"))
		if e != nil || string(status) != "ready\n" {
			return nil, errors.New("WORKSPACE_NOT_READY: complete restore before selecting it")
		}
	}
	if _, e := os.Stat(runtime); e != nil {
		return nil, errors.New("CONFIG_MISSING: workspace credentials are required")
	}
	if target == c.Project {
		return map[string]any{"status": "selected", "project": target}, nil
	}
	active, e := c.running(ctx)
	if e != nil {
		return nil, e
	}
	if len(active) > 0 {
		if e = run(c.compose(ctx, append([]string{"stop"}, active...)...)); e != nil {
			return nil, e
		}
	}
	next := Controller{Root: c.Root, Project: target, Runtime: runtime}
	selected := false
	defer func() {
		if !selected {
			end, cancel := context.WithTimeout(context.Background(), 90*time.Second)
			defer cancel()
			_ = run(next.compose(end, "stop", "web", "api", "speech"))
			if len(active) > 0 {
				_ = run(c.compose(end, append([]string{"start"}, active...)...))
			}
		}
	}()
	if e = run(next.compose(ctx, "up", "-d", "--wait", "--wait-timeout", "180", "web")); e != nil {
		return nil, errors.New("WORKSPACE_SWITCH_FAILED: previous workspace retained and restarted")
	}
	marker := filepath.Join(c.Root, "data/config/active-project")
	tmp := marker + ".new"
	if e = os.WriteFile(tmp, []byte(target+"\n"), 0600); e != nil {
		return nil, e
	}
	if e = os.Rename(tmp, marker); e != nil {
		return nil, e
	}
	selected = true
	return map[string]any{"status": "selected", "project": target, "previous_project": c.Project, "previous_volumes": "retained", "inference_calls": 0}, nil
}
func Command(ctx context.Context, root, project, runtime string, args []string, out io.Writer) error {
	c := Controller{root, project, runtime}
	lock, e := os.OpenFile(filepath.Join(root, "data/config/.maintenance-lock"), os.O_CREATE|os.O_RDWR, 0600)
	if e != nil {
		return e
	}
	defer lock.Close()
	if e = syscall.Flock(int(lock.Fd()), syscall.LOCK_EX|syscall.LOCK_NB); e != nil {
		return errors.New("WORKSPACE_BUSY: another local maintenance action is running")
	}
	defer syscall.Flock(int(lock.Fd()), syscall.LOCK_UN)
	if runtime == filepath.Join(root, "data/config/runtime.env") {
		marker := filepath.Join(root, "data/config/original-project")
		f, e := os.OpenFile(marker, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
		if e == nil {
			_, _ = f.WriteString(project + "\n")
			_ = f.Close()
		}
	}
	if !projectPattern.MatchString(project) {
		return errors.New("WORKSPACE_INVALID")
	}
	var result map[string]any
	e = nil
	switch {
	case len(args) == 2 && args[0] == "backup":
		result, e = c.Backup(ctx, args[1])
	case len(args) == 3 && args[0] == "restore":
		result, e = c.Restore(ctx, args[1], args[2])
	case len(args) == 1 && args[0] == "purge-lab":
		result, e = c.PurgeLab(ctx)
	case len(args) == 2 && args[0] == "switch":
		result, e = c.Switch(ctx, args[1])
	default:
		return errors.New("MAINTENANCE_USAGE: backup <name.tar.gz> | restore <path> <new-project> | switch <project>")
	}
	if e != nil {
		return e
	}
	return json.NewEncoder(out).Encode(result)
}

func (c Controller) PurgeLab(ctx context.Context) (map[string]any, error) {
	if os.Getenv("CONFIRM_DELETE_LOCAL_LAB") != "yes" {
		return nil, errors.New("WORKSPACE_CONFIRMATION_REQUIRED: CONFIRM_DELETE_LOCAL_LAB=yes deletes this workspace Lab and all installation export copies")
	}
	if e := run(c.compose(ctx, "--profile", "llm-lab", "stop", "llm-lab")); e != nil {
		return nil, e
	}
	if e := run(c.compose(ctx, "--profile", "llm-lab", "rm", "-f", "llm-lab")); e != nil {
		return nil, e
	}
	if c.volume(ctx, "lab-data") {
		if e := run(c.command(ctx, "volume", "rm", c.Project+"_lab-data")); e != nil {
			return nil, e
		}
	}
	if e := os.RemoveAll(filepath.Join(c.Root, "data/config/lab-native")); e != nil {
		return nil, e
	}
	if e := run(c.compose(ctx, "run", "--rm", "--no-deps", "-T", "api", "maintenance-lab-purged")); e != nil {
		return nil, e
	}
	return map[string]any{"status": "lab_erased", "native_results": "retained", "inference_calls": 0}, nil
}
