package localctl

// Only Docker's command boundary is controlled here. Genuine Docker/DB/media/
// browser observations live in tests/recovery-workspace, not in these tests.
import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"syscall"
	"testing"
)

func localFixture(t *testing.T, mode string) Controller {
	t.Helper()
	root := t.TempDir()
	dir := filepath.Join(root, "data/config")
	if e := os.MkdirAll(dir, 0700); e != nil {
		t.Fatal(e)
	}
	trace := filepath.Join(root, "trace")
	t.Setenv("TANGERINE_FAKE_TRACE", trace)
	t.Setenv("TANGERINE_FAKE_MODE", mode)
	script := `#!/bin/sh
printf '%s\n' "$*" >> "$TANGERINE_FAKE_TRACE"
case "$*" in
 *'volume inspect'*) [ "$TANGERINE_FAKE_MODE" = existing-volume ] && exit 0; exit 1;;
 *'ps --status running --services'*) printf 'web\napi\nspeech\n';;
 *'snapshot-create'*) printf 'literal native archive bytes';;
 *'start web api speech'*) [ "$TANGERINE_FAKE_MODE" = restart-failure ] && exit 1;;
 *'up -d --wait'*) [ "$TANGERINE_FAKE_MODE" = target-failure ] && exit 1;;
esac
exit 0
`
	if e := os.WriteFile(filepath.Join(root, "docker"), []byte(script), 0700); e != nil {
		t.Fatal(e)
	}
	t.Setenv("PATH", root+":"+os.Getenv("PATH"))
	return Controller{Root: root, Project: "original", Runtime: filepath.Join(dir, "runtime.env")}
}
func targetFixture(t *testing.T, c Controller) {
	t.Helper()
	dir := filepath.Join(c.Root, "data/config/restores/restored")
	if e := os.MkdirAll(dir, 0700); e != nil {
		t.Fatal(e)
	}
	for k, v := range map[string]string{"status": "ready\n", "runtime.env": "private-test-credentials"} {
		if e := os.WriteFile(filepath.Join(dir, k), []byte(v), 0600); e != nil {
			t.Fatal(e)
		}
	}
}
func TestLocalRecoveryBackupPositive(t *testing.T) {
	c := localFixture(t, "good")
	p, e := c.Backup(context.Background(), "saved.tar.gz")
	if e != nil {
		t.Fatal(e)
	}
	b, e := os.ReadFile(filepath.Join(c.Root, "data/backups/saved.tar.gz"))
	if e != nil || string(b) != "literal native archive bytes" || p["status"] != "complete" {
		t.Fatal(p, e)
	}
	trace, _ := os.ReadFile(filepath.Join(c.Root, "trace"))
	if !strings.Contains(string(trace), "stop web api speech") || !strings.Contains(string(trace), "start web api speech") {
		t.Fatal(string(trace))
	}
}
func TestLocalRecoveryBackupRestartNegative(t *testing.T) {
	c := localFixture(t, "restart-failure")
	_, e := c.Backup(context.Background(), "saved.tar.gz")
	if e == nil || !strings.Contains(e.Error(), "BACKUP_SAVED_RESTART_REQUIRED") {
		t.Fatal(e)
	}
	if _, e = os.Stat(filepath.Join(c.Root, "data/backups/saved.tar.gz")); e != nil {
		t.Fatal("saved backup lost", e)
	}
}
func TestLocalRecoveryBackupCollisionNegative(t *testing.T) {
	c := localFixture(t, "good")
	_, e := c.Backup(context.Background(), "saved.tar.gz")
	if e != nil {
		t.Fatal(e)
	}
	_, e = c.Backup(context.Background(), "saved.tar.gz")
	if e == nil || !strings.Contains(e.Error(), "BACKUP_EXISTS") {
		t.Fatal(e)
	}
}
func TestLocalRecoveryExplicitSwitchPositive(t *testing.T) {
	c := localFixture(t, "good")
	targetFixture(t, c)
	p, e := c.Switch(context.Background(), "restored")
	if e != nil {
		t.Fatal(e)
	}
	b, _ := os.ReadFile(filepath.Join(c.Root, "data/config/active-project"))
	if string(b) != "restored\n" || p["previous_volumes"] != "retained" {
		t.Fatal(p, string(b))
	}
}
func TestLocalRecoverySwitchRollbackNegative(t *testing.T) {
	for _, mode := range []string{"target-failure", "marker-failure"} {
		t.Run(mode, func(t *testing.T) {
			c := localFixture(t, mode)
			targetFixture(t, c)
			if mode == "marker-failure" {
				if e := os.Mkdir(filepath.Join(c.Root, "data/config/active-project"), 0700); e != nil {
					t.Fatal(e)
				}
			}
			if _, e := c.Switch(context.Background(), "restored"); e == nil {
				t.Fatal("failed target selected")
			}
			trace, _ := os.ReadFile(filepath.Join(c.Root, "trace"))
			if !strings.Contains(string(trace), "stop web api speech") || !strings.Contains(string(trace), "start web api speech") {
				t.Fatal("previous workspace was not recovered", string(trace))
			}
		})
	}
}
func TestLocalRecoveryExistingVolumeNegative(t *testing.T) {
	c := localFixture(t, "existing-volume")
	_, e := c.Restore(context.Background(), "missing.tar.gz", "restored")
	if e == nil || !strings.Contains(e.Error(), "RESTORE_TARGET_EXISTS") {
		t.Fatal(e)
	}
}
func TestLocalRecoveryBusyNegative(t *testing.T) {
	c := localFixture(t, "good")
	f, e := os.OpenFile(filepath.Join(c.Root, "data/config/.maintenance-lock"), os.O_CREATE|os.O_RDWR, 0600)
	if e != nil {
		t.Fatal(e)
	}
	defer f.Close()
	if e = syscall.Flock(int(f.Fd()), syscall.LOCK_EX); e != nil {
		t.Fatal(e)
	}
	e = Command(context.Background(), c.Root, c.Project, c.Runtime, []string{"backup", "test.tar.gz"}, os.Stdout)
	if e == nil || !strings.Contains(e.Error(), "WORKSPACE_BUSY") {
		t.Fatal(e)
	}
}
func TestLocalRecoveryPurgePositive(t *testing.T) {
	c := localFixture(t, "good")
	t.Setenv("CONFIRM_DELETE_LOCAL_LAB", "yes")
	dir := filepath.Join(c.Root, "data/config/lab-native")
	if e := os.Mkdir(dir, 0700); e != nil {
		t.Fatal(e)
	}
	if e := os.WriteFile(filepath.Join(dir, "copied-body"), []byte("constructed private body"), 0600); e != nil {
		t.Fatal(e)
	}
	_, e := c.PurgeLab(context.Background())
	if e != nil {
		t.Fatal(e)
	}
	if _, e = os.Stat(dir); !os.IsNotExist(e) {
		t.Fatal("copied body remains", e)
	}
}
func TestLocalRecoveryPurgeConfirmationNegative(t *testing.T) {
	c := localFixture(t, "good")
	t.Setenv("CONFIRM_DELETE_LOCAL_LAB", "")
	if _, e := c.PurgeLab(context.Background()); e == nil {
		t.Fatal("unconfirmed erasure")
	}
	if _, e := os.Stat(filepath.Join(c.Root, "trace")); !os.IsNotExist(e) {
		t.Fatal("unconfirmed command reached Docker")
	}
}
